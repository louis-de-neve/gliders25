import scipy.io
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl


from transect_information import all_transect_indexes, short_or_missing_casts, offset_casts

def import_data_from_mat_file(
        filename:str='Louis/data_631_allqc.mat',
        data_location = "DATA_PROC",
        parameters:list[str]=["time", "longitude", "latitude", "depth", "chlorophyll"]
        ) -> pd.DataFrame:
    

    mat = scipy.io.loadmat(filename)
    raw_data = mat[data_location][0, 0]
    raw_data_keys = raw_data.dtype.names
    full_data_dictionary = {}

    for key in raw_data_keys:
        full_data_dictionary[key] = raw_data[key].flatten()

    limited_dict = {key: full_data_dictionary[key] for key in parameters}

    df = pd.DataFrame.from_dict(limited_dict)
    df["DateTime"] = pd.to_datetime(df["time"], unit='s')

    return df


def split_dataframe_by_cast(df:pd.DataFrame) -> list[pd.DataFrame]:
    df["rolling_mean_depth"] = df["depth"].rolling(window=20, center=True).mean()
    df["local_minima"] = df["rolling_mean_depth"] == df["rolling_mean_depth"].rolling(window=20, center=True).max()
    df["is_rising"] = df["rolling_mean_depth"] == df["rolling_mean_depth"].rolling(window=20).min()

    df["split_location"] = (df["is_rising"] != df["is_rising"].shift(1))

    split_indices = df.index[df["split_location"]].tolist()
    split_dataframes = np.split(df, split_indices)

    valid_casts = sanitise_casts(split_dataframes)

    return valid_casts


def sanitise_casts(split_dataframes:list[pd.DataFrame]) -> list[pd.DataFrame]:
    valid_casts = []
    for dataframe in split_dataframes:
        if (len(dataframe) > 100) & (dataframe["depth"].max() > 1.0):
            valid_casts.append(dataframe)

    return valid_casts


class Cast:
    def __init__(self, cast_data:pd.DataFrame, transect_index:int|None=None):
        self.data = cast_data
        self.length = len(self.data["depth"])
        self.maximum_depth = cast_data["depth"].max()
        self.start_time = cast_data["DateTime"].iloc[0]
        self.start_location = [cast_data["latitude"].iloc[0], cast_data["longitude"].iloc[0]]
        self.end_location = [cast_data["latitude"].iloc[-1], cast_data["longitude"].iloc[-1]]
        self.cast_duration = cast_data["DateTime"].iloc[-1] - self.start_time
        self.transect_index = transect_index
        
    def apply_binning_to_parameter(self, parameter:str, bin_size:float=1.0) -> pd.DataFrame:
        bins = np.arange(0, 1000, bin_size)
        binned_data = self.data.groupby(pd.cut(self.data["depth"], bins), observed=False)[parameter].mean().reset_index()
        binned_data.columns = ["depth_bin", f"binned_{parameter}"]
        binned_data = list(binned_data[f"binned_{parameter}"])
        binned_data += [np.nan] * int(1000/bin_size - len(binned_data))
        return binned_data
    
    def merge(self, other) -> None: # occurrs inplace and merges other into self
        self.data = pd.concat([self.data, other.data], ignore_index=True)
        self.maximum_depth = self.data["depth"].max()
        self.start_time = self.data["DateTime"].iloc[0]
        self.start_location = [self.data["latitude"].iloc[0], self.data["longitude"].iloc[0]]
        self.end_location = [self.data["latitude"].iloc[-1], self.data["longitude"].iloc[-1]]
        self.cast_duration = self.data["DateTime"].iloc[-1] - self.start_time
        self.transect_index = self.transect_index
        self.length = len(self.data["depth"])


def two_dimensional_binning(valid_casts:list[pd.DataFrame|Cast], parameter:str, bin_size:float=1.0) -> np.ndarray:
    if type(valid_casts[0]) == pd.DataFrame:
        valid_casts = [Cast(df) for df in valid_casts]

    data_array = []
    for cast in valid_casts:
        binned_data = cast.apply_binning_to_parameter(parameter, bin_size)
        data_array.append(binned_data)
    
    data_array = np.asarray(data_array)
    
    return data_array.T


def ts_plot(valid_casts, ax) -> None:
    for df in valid_casts:
        ax.scatter(df["salinity_final"], df["temperature_final"], c=df["chlorophyll"], norm=mpl.colors.LogNorm())


def binned_plot(valid_casts:list[pd.DataFrame|Cast], ax:plt.axes) -> mpl.collections.PolyQuadMesh:
    data_array = two_dimensional_binning(valid_casts, "chlorophyll", 0.5)
    depth_bins = -np.arange(0, 1000, 0.5)
    time_bins = np.arange(data_array.shape[1])/2

    X, Y = np.meshgrid(time_bins, depth_bins)
    pcm = ax.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm(vmin=0.03, vmax=30))
    ax.set_xlabel("Downcast number")
    #ax.set_ylabel("Depth (m)")
    return pcm



class Transect:
    def __init__(self, name:str, casts:list[Cast]):
        self.casts = casts
        self.start_time = casts[0].start_time
        self.finish_time = casts[-1].data["DateTime"].iloc[-1]
        self.start_location = casts[0].start_location
        self.finish_location = casts[-1].end_location
        self.name = name


def create_transects(valid_casts:list[pd.DataFrame], sanitise:bool=True) -> list[Transect]:
    all_transects = []
    for transect_name, transect_indices in all_transect_indexes.items():
        
        start, end = transect_indices
        transect_casts = valid_casts[start:end+1]

        casts_with_offsets = offset_casts.get(transect_name, [])
        casts_with_errors = short_or_missing_casts.get(transect_name, []) + casts_with_offsets

        transect_casts_sanitised = []
        for i, cast_dataframe in enumerate(transect_casts):
            cast = Cast(cast_dataframe, transect_index=i)

            if (not sanitise) or (i not in casts_with_errors): # If sanitise is False, don't sanitise and if there is no problems, append 
                transect_casts_sanitised.append(cast)

            elif i in casts_with_offsets: # applies only to casts_with_offsets
                print("here")
                if i+1 in casts_with_offsets: # i.e. only the first offset cast
                    print(cast.start_time, cast.length)

                    cast.merge(Cast(transect_casts[i+1], transect_index=i+1))

                    print(cast.start_time, cast.length)
                    transect_casts_sanitised.append(cast)

            else: # applies only to short or missing casts
                pass
                

        if sanitise:
            if transect_name == "B":
                pass

        all_transects.append(Transect(transect_name, transect_casts_sanitised))
    
    return all_transects





def run():
    df = import_data_from_mat_file(parameters=["time", "longitude", "latitude", "depth", "chlorophyll", "temperature_final", "salinity_final"])

    #df = df.loc[:100000]


    valid_casts = split_dataframe_by_cast(df)

    transects = create_transects(valid_casts, sanitise=True)

    fig, axs = plt.subplots(2, 5, figsize=(30, 10), sharey=True)
    axs = axs.flatten()

    for T, ax in zip(transects, axs):
        ax.set_title(T.name)
        pcm = binned_plot(T.casts, ax)

    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
    cbar_ax.set_xlabel("Chlorophyll (mg/m^3)")
    #plt.colorbar(pcm, orientation="horizontal")

    axs[0].set_ylabel("Depth (m)")
    axs[5].set_ylabel("Depth (m)")
    plt.savefig("Louis/outputs/output5.png", dpi=300)
    plt.show()






    # fig, axs = plt.subplots(3, 1)

    # ax = axs[1]

    # for i, df in enumerate(valid_casts):
    #     ax.scatter(i/2, df["latitude"].iloc[0])
    #     ax.set_xlim(0, len(valid_casts)/2)
    #     ax.set_ylabel("Latitude")

    # ax = axs[2]
    # for i, df in enumerate(valid_casts):
    #     ax.scatter(i/2, df["longitude"].iloc[0])
    #     ax.set_xlim(0, len(valid_casts)/2)
    #     ax.set_ylabel("Longitude")
        

    #binned_plot(valid_casts, ax=axs[0])

if __name__ == "__main__":
    run()

