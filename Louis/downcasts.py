
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy

import matplotlib as mpl

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

df = import_data_from_mat_file(parameters=["time", "longitude", "latitude", "depth", "chlorophyll", "temperature_final", "salinity_final", "profile_index"])

data1 = []
dfs = dict(tuple(df.groupby('profile_index')))
for d in dfs.values():
    bins = np.arange(0, 1000, 1)
    binned_data = d.groupby(pd.cut(d["depth"], bins), observed=False)["chlorophyll"].mean().reset_index()
    binned_data.columns = ["depth_bin", f"binned_chlorophyll"]
    binned_data = list(binned_data[f"binned_chlorophyll"])
    binned_data += [np.nan] * int(1000 - len(binned_data))
    data1.append(binned_data)
data_array = np.asarray(data1).T
depth_bins = -np.arange(0, 1000, 1)
time_bins = np.arange(data_array.shape[1])/2
X, Y = np.meshgrid(time_bins, depth_bins)
pcm = plt.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm(vmin=0.03, vmax=30))
plt.show()

df = df.loc[1400000:1600000]

df["rolling_mean_depth"] = df["depth"].rolling(window=20, center=True).mean()
df["local_minima"] = df["rolling_mean_depth"] == df["rolling_mean_depth"].rolling(window=20, center=True).max()
df["is_rising"] = df["rolling_mean_depth"] == df["rolling_mean_depth"].rolling(window=20).min()

df["split_location"] = (df["is_rising"] != df["is_rising"].shift(1))

split_indices = df.index[df["split_location"]].tolist()
split_dataframes = np.split(df, split_indices)

print(len(split_dataframes))
valid_casts = []
for dataframe in split_dataframes:
    if (len(dataframe) > 100) & (dataframe["depth"].max() > 1.0):
        valid_casts.append(dataframe)
print(len(valid_casts))


df["color"] = np.where(df["is_rising"], "r", "b")

plt.plot(-df["depth"])
plt.plot(-df["rolling_mean_depth"])
#plt.scatter(df.index, -df["depth"], c=df["color"])



for df in valid_casts:
    df["color"] = np.where(df["is_rising"], "r", "b")
    df["color"] = np.where(df["split_location"], "g", df["color"])
    plt.plot(-df["depth"])
    plt.plot(-df["rolling_mean_depth"])
    plt.scatter(df.index, -df["depth"], c=df["chlorophyll"], cmap="viridis")
    
plt.show()

