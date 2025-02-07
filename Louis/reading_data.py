import scipy.io
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


mat = scipy.io.loadmat('Louis/data_631_allqc.mat')
raw_data = mat["DATA_PROC"][0, 0]
raw_data_keys = raw_data.dtype.names
full_data_dictionary = {}

for key in raw_data_keys:
    full_data_dictionary[key] = raw_data[key].flatten()

limited_parameters = ["time", "longitude", "latitude", "depth", "chlorophyll"]
limited_dict = {key: full_data_dictionary[key] for key in limited_parameters}

df = pd.DataFrame.from_dict(limited_dict)
df["DateTime"] = pd.to_datetime(df["time"], unit='s')


locations = df[df["depth"] == 0]
print(locations)

df = df.loc[:10000]

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
    plt.plot(-df["depth"])
    plt.plot(-df["rolling_mean_depth"])
    plt.scatter(df.index, -df["depth"], c=df["color"])
    

plt.show()