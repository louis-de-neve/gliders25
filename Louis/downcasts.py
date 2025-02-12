df = df.loc[:20000]

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
    