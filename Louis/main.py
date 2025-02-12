import scipy.io
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
import geopy.distance as gp


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
    def __init__(self, cast_data:pd.DataFrame):
        self.data = cast_data
        self.maximum_depth = cast_data["depth"].max()
        self.start_time = cast_data["DateTime"].iloc[0]
        self.start_location = [cast_data["latitude"].iloc[0], cast_data["longitude"].iloc[0]]
        self.end_location = [cast_data["latitude"].iloc[-1], cast_data["longitude"].iloc[-1]]
        #self.cast_length = gp.geodesic(self.start_location, self.end_location).m
        self.cast_duration = cast_data["DateTime"].iloc[-1] - self.start_time
        
    def apply_binning_to_parameter(self, parameter:str, bin_size:float=1.0) -> pd.DataFrame:
        bins = np.arange(0, 1000, bin_size)
        binned_data = self.data.groupby(pd.cut(self.data["depth"], bins), observed=True)[parameter].mean().reset_index()
        binned_data.columns = ["depth_bin", f"binned_{parameter}"]
        binned_data = list(binned_data[f"binned_{parameter}"])
        binned_data += [np.nan] * int(1000/bin_size - len(binned_data))
        return binned_data


def two_dimensional_binning(valid_casts:list[Cast], parameter:str, bin_size:float=1.0) -> np.ndarray:
    data_array = []
    for df in valid_casts:
        cast = Cast(df)
        binned_data = cast.apply_binning_to_parameter(parameter, bin_size)
        data_array.append(binned_data)
    
    data_array = np.asarray(data_array)
    
    return data_array.T


df = import_data_from_mat_file()

#df = df.loc[:100000]

valid_casts = split_dataframe_by_cast(df)

data_array = two_dimensional_binning(valid_casts, "chlorophyll", 0.5)

depth_bins = -np.arange(0, 1000, 0.5)
time_bins = np.arange(data_array.shape[1])/2

X, Y = np.meshgrid(time_bins, depth_bins)
plt.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm())
plt.xlabel("Downcast number")
plt.ylabel("Depth (m)")
#plt.pcolor(data_array, norm=mpl.colors.LogNorm())
plt.show()

# for i, df in enumerate(valid_casts):
#     cast = Cast(df)
#     if i == 3:
#         print(cast.apply_binning_to_parameter("chlorophyll"))
#     #df["color"] = np.where(df["is_rising"], "r", "b")
#     plt.scatter(np.full_like(df["depth"], df["DateTime"].iloc[0], dtype=pd._libs.tslibs.timestamps.Timestamp), -df["depth"], c=df["chlorophyll"], norm=mpl.colors.LogNorm())

plt.show()