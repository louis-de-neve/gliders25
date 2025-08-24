from gsw import SA_from_SP, CT_from_t, sigma0


def MLD_calculation(profiles:list) -> list:
    print("Calculating MLDs...")
    for profile in profiles:
        salinity = profile.data["salinity_final"].interpolate()
        pressure = profile.data["pressure"].interpolate()
        temperature = profile.data["temperature_final"].interpolate()
        lat = profile.data["latitude"]
        lon = profile.data["longitude"]
        corrected_salinity = SA_from_SP(salinity, pressure, lon, lat)
        corrected_temperature = CT_from_t(corrected_salinity, temperature, pressure)
        profile.data["SA"] = corrected_salinity
        profile.data["CT"] = corrected_temperature
             
        absolute_density = sigma0(corrected_salinity, corrected_temperature)
        
        profile.data["density"] = absolute_density

        df = profile.data
        df = df.sort_values("depth")
        temp_df = df.dropna(subset=["density"])
        surface_density = temp_df.iloc[0]["density"] if (len(temp_df) > 0) and (temp_df.iloc[0]["depth"] < 5) else 0
        df["density_anomaly"] = df["density"] - surface_density 
        profile.data["density_anomaly"] = profile.data["density"] - surface_density
        df = df[df["density_anomaly"] > 0.03]
        df = df[df["depth"] < 200]

        if len(df) == 0:
            profile.mld = 1
        else:
            mld_index = int(df.iloc[0]["original_index"])
            mld_depth = profile.data[profile.data["original_index"] == mld_index]["depth"].iloc[0]

            if profile.direction == "up":
                other_index = mld_index + 1
            else:
                other_index = mld_index - 1
            try:
                other_depth = profile.data[profile.data["original_index"] == other_index]["depth"].iloc[0]
            except IndexError:
                other_depth = mld_depth
            profile.mld = (mld_depth + other_depth)/2

    return profiles