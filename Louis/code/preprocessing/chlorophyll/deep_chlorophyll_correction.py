def deep_chlorophyll_correction(profiles:list) -> list:
    print("Correcting deep chlorophyll...")
    for profile in profiles:
        profile.data["original_chlorophyll"] = profile.data["chlorophyll"]
        df = profile.data
        deep_df = df[df["depth"] > 300]
        deep_c_95 = deep_df["chlorophyll"].quantile(0.05)
        df["chlorophyll"] -= deep_c_95

        df.loc[df["chlorophyll"] < 0, "chlorophyll"] = 0

        profile.data = df
            
    return profiles