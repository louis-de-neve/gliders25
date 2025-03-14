import scipy.io
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl

def import_data_from_mat_file(
        filename:str='Louis/data/data_631_allqc.mat',
        data_location = "DATA_PROC",
        parameters:list[str]|str="all"
        ) -> pd.DataFrame:
    
    mat = scipy.io.loadmat(filename)
    
    raw_data = mat[data_location][0, 0]
    raw_data_keys = raw_data.dtype.names
    full_data_dictionary = {}

    for key in raw_data_keys:
        full_data_dictionary[key] = raw_data[key].flatten()

    if parameters == "all":
        parameters = raw_data_keys

    
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
        self.night = False

    def __repr__(self) -> str:
        return f"Profile {self.index} from transect {self.transect_index}"
        
    def apply_binning_to_parameter(self, parameter:str, bin_size:float=1.0, max_depth:float=1000.) -> list[float]:
        bins = np.arange(bin_size/2, max_depth, bin_size)
        d = self.data
        d = d[d["depth"] < max_depth]
        d = d[d["depth"] >= bin_size/2]
        binned_data = d.groupby(pd.cut(d["depth"], bins), observed=False)[parameter].mean().reset_index()
        binned_data.columns = ["depth_bin", f"binned_{parameter}"]
        binned_data = list(binned_data[f"binned_{parameter}"])
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

def concatenate_profiles(profiles:list[Profile]) -> pd.DataFrame:
    p0 = profiles[0]
    for profile in profiles[1:]:
        p0.merge(profile)
    return p0.data  


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


def create_transects(valid_profiles:list[pd.DataFrame], use_upcasts:bool=False) -> list[Transect]:
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

        if not use_upcasts:
            downcasts = []
            for p in transect_profiles:
                if p.direction == "up":
                    downcasts.append(p)
            transect_profiles=downcasts

        transect_list.append(Transect(transect_name, transect_profiles))
    
    print(f"Created {len(transect_list)} transects")

    return transect_list


def no_pre_processing(profiles:list[Profile]) -> list[Profile]:
    return profiles

def no_quenching_correction(profiles:list[Profile]) -> list[Profile]:
    return profiles

def import_split_and_make_transects(parameters:list[str]|None=["time", "longitude", "latitude",
                                                               "depth", "chlorophyll", "pressure",
                                                               "temperature_final", "salinity_final",
                                                               "temperature", "salinity", "temperature_corrected_thermal",
                                                               "profile_index", "scatter_650"],
                                    pre_processing_function=no_pre_processing,
                                    use_cache:bool=True,
                                    quenching_method=no_quenching_correction,
                                    use_downcasts:bool=False,
                                    **kwargs
                                    ) -> tuple[list[Transect], list[Profile]]:
    
    if not use_cache:
        df = import_data_from_mat_file(parameters=parameters)
        profiles = split_raw_data_into_profiles(df)
    else:
        profiles = []
    profiles = pre_processing_function(profiles, quenching_method, use_cache, **kwargs)

    

    transects = create_transects(profiles, use_downcasts)

    if not use_downcasts:
        downcasts = []
        for p in profiles:
            if p.direction == "up":
                downcasts.append(p)
        profiles=downcasts
    
        
    return transects, profiles

