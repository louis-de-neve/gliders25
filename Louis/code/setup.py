import scipy.io
import numpy as np
import pandas as pd
import os
import xarray as xr
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing

def import_data_from_mat_file(
        filename:str='Louis/data/data_631_allqc.mat',
        data_location = "DATA_PROC",
        parameters:list[str]|str="all",
        print_keys:bool=False,
        ) -> pd.DataFrame:
    
    mat = scipy.io.loadmat(filename)
    
    raw_data = mat[data_location][0, 0]
    raw_data_keys = raw_data.dtype.names
    full_data_dictionary = {}

    for key in raw_data_keys:
        full_data_dictionary[key] = raw_data[key].flatten()

    if parameters == "all":
        parameters = raw_data_keys

    if print_keys:
        print(f"Keys: {raw_data_keys}")
        return()

    
    limited_dict = {key: full_data_dictionary[key] for key in parameters}
    

    df = pd.DataFrame.from_dict(limited_dict)
    df["DateTime"] = pd.to_datetime(df["time"], unit='s')
    df["original_index"] = df.index
    
    
    return df


class Profile:
    def __init__(self, cast_data:pd.DataFrame,
                       transect_index:int|None=None,
                       profile_index:int|None=None):
        self.data = cast_data
        self.index = profile_index
        self.transect_index = transect_index
        self.length = len(self.data["depth"])
        self.maximum_depth = cast_data["depth"].max()
        self.start_time = cast_data["DateTime"].iloc[0]
        self.start_location = [cast_data["longitude"].iloc[0], cast_data["latitude"].iloc[0]]
        self.end_time = cast_data["DateTime"].iloc[-1]
        self.end_location = [cast_data["longitude"].iloc[-1], cast_data["latitude"].iloc[-1]]
        self.profile_duration = self.end_time - self.start_time
        self.MLD = np.nan
        self.bathymetry = 0
        self.night = False

    def __repr__(self) -> str:
        return f"Profile {self.index} from transect {self.transect_index}"
        
    def apply_binning_to_parameter(self, parameter:str, bin_size:float=1.0, max_depth:float=1000.) -> list[float]:
        bins = np.arange(0, max_depth+bin_size, bin_size)
        d = self.data
        d = d[d["depth"] < max_depth]
        d = d[d["depth"] >= bin_size/2]
        d[parameter] = d[parameter].replace(0, np.nan)
        binned_data = d.groupby(pd.cut(d["depth"], bins), observed=False)[parameter].mean().reset_index()
        binned_data.columns = ["depth_bin", f"binned_{parameter}"]
        binned_data = list(binned_data[f"binned_{parameter}"].fillna(0))
        if self.data["depth"].max() < max_depth:
            data_max_depth = self.data["depth"].max()
            binned_data = [d if i <= data_max_depth/bin_size else np.nan for i, d in enumerate(binned_data)]

        binned_data += [np.nan] * int( max_depth/bin_size - len(binned_data))
        return binned_data
    
    def allocate_profile_to_transect(self, transect_index:int) -> None:
        self.transect_index = transect_index

    def merge(self, other):
        index = min([self.index, other.index])
        self.data = pd.concat([self.data, other.data])
        self.index = index
        self.length = len(self.data["depth"])
        self.maximum_depth = self.data["depth"].max()
        self.start_time = min(self.start_time, other.start_time)
        self.start_location = self.start_location if self.start_time <= other.start_time else other.start_location
        self.end_location = self.end_location if self.data["DateTime"].iloc[-1] >= other.data["DateTime"].iloc[-1] else other.end_location
        self.profile_duration = self.data["DateTime"].iloc[-1] - self.start_time
        self.direction = "up" if self.data["depth"].iloc[0] > self.data["depth"].iloc[-1] else "down" # depth is positive
        return self
    
    def get_bathymetry(self, dataset:xr.Dataset) -> float:
        lon = self.start_location[0]
        lat = self.start_location[1]
        bathymetry = dataset.sel(lon=lon, lat=lat, method="nearest")["elevation"].values
        return bathymetry


def concatenate_profiles(profiles:list[Profile]) -> pd.DataFrame:
    p0 = profiles[0]
    for profile in profiles[1:]:
        p0.merge(profile)
    return p0.data  


def apply_bathymetry(profiles:list[Profile]) -> list[Profile]:
    dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")
    for profile in profiles:
        profile.bathymetry = profile.get_bathymetry(dataset)
    return profiles


def split_raw_data_into_profiles(df:pd.DataFrame, include_non_integer_profiles:bool=True) -> list[Profile]:
    split_dataframes = list(df.groupby('profile_index'))

    all_profiles = [Profile(dataframe, profile_index=profile_index) for profile_index, dataframe in split_dataframes]
    
    all_profiles.pop(0)
    integer_profiles = []

    if include_non_integer_profiles:
        for i, profile in enumerate(all_profiles):
            if not profile.index.is_integer():
                integer_profiles.append(all_profiles[i-1].merge(profile))

    else:
        for profile in all_profiles:
            if (profile.length > 1000) & (profile.data["depth"].max() > 3.0):
                integer_profiles.append(profile)

    print(f"Found {len(integer_profiles)} valid profiles")
    integer_profiles = apply_bathymetry(integer_profiles)
    return integer_profiles


def two_dimensional_binning(valid_profiles:list[Profile], parameter:str, bin_size:float=0.5, max_depth:float=1000.) -> np.ndarray:
    data_array = []
    for profile in valid_profiles:
        binned_data = profile.apply_binning_to_parameter(parameter, bin_size, max_depth)
        data_array.append(binned_data)
    data_array = np.asarray(data_array)
    return data_array.T


class Transect:
    def __init__(self, name:str, profiles:list[Profile]):
        self.profiles = profiles
        self.start_time = profiles[0].start_time
        self.finish_time = profiles[-1].data["DateTime"].iloc[-1]
        self.start_location = profiles[0].start_location
        self.finish_location = profiles[-1].end_location
        self.name = name

    def get_profiles(self) -> list[Profile]:
        return self.profiles


def create_transects(valid_profiles:list[pd.DataFrame], use_downcasts:bool=False) -> list[Transect]:
    TRANSECT_INDICES = {
    "A": (1, 89),
    "B": (90, 225),
    "C": (226, 297),
    "D": (298, 340),
    "E": (341, 428),
    "F": (429, 488),
    "G": (489, 565),
    "H": (566, 668),
    "I": (669, 765),
    "J": (766, 831),
    }

    transect_list = []
    for transect_name, transect_indices in TRANSECT_INDICES.items():
        
        start, end = transect_indices
        transect_profiles = valid_profiles[start:end+1]

        for profile in transect_profiles:
            profile.allocate_profile_to_transect(transect_name)

        if not use_downcasts:
            upcasts = []
            for p in transect_profiles:
                if p.direction == "up":
                    upcasts.append(p)
            transect_profiles=upcasts

        transect_list.append(Transect(transect_name, transect_profiles))
    
    print(f"Created {len(transect_list)} transects")

    return transect_list



def import_split_and_make_transects(parameters:list[str]|None=["time", "longitude", "latitude",
                                                               "depth", "chlorophyll", "pressure",
                                                               "temperature_final", "salinity_final",
                                                               "temperature", "salinity", "temperature_corrected_thermal",
                                                               "profile_index", "scatter_650", "PAR"],
                                    use_downcasts:bool=False,
                                    use_cache:bool=False,
                                    ) -> tuple[list[Transect], list[Profile]]:
    
    if use_cache and os.path.exists("Louis/cache/supercache.pkl"):
        with open("Louis/cache/supercache.pkl", "rb") as f:
            data = pd.read_pickle(f)
        profiles = data["profiles"]
        transects = data["transects"]


        if not use_downcasts:
            upcasts = []
            for p in profiles:
                if p.direction == "up":
                    upcasts.append(p)
            profiles=upcasts

        if use_downcasts:
            profiles.pop(538) # remove bad profiles



        return transects, profiles

    
    df = import_data_from_mat_file(parameters=parameters)
    profiles = split_raw_data_into_profiles(df)
    profiles = scatter_and_chlorophyll_processing(profiles, use_downcasts)
    transects = create_transects(profiles, use_downcasts)
    
    if not use_downcasts:
        downcasts = []
        for p in profiles:
            if p.direction == "up":
                downcasts.append(p)
        profiles=downcasts

    print("caching data...")
    with open("Louis/cache/supercache.pkl", "wb") as f:
        pd.to_pickle({"profiles": profiles, "transects": transects}, f)


    


    return transects, profiles

if __name__ == "__main__":
    import_data_from_mat_file(print_keys=True)