from setup.setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from preprocessing.betasw_zhh09 import betasw_ZHH2009
import scipy as sp
from plotting_functions import binned_plot
from gsw import SA_from_SP, CT_from_t, sigma0
import os


def beta_to_bbp(beta, temp, salinity):
    theta = 124
    delta = 0.039
    Xi = 1.077
    l = 700
    betasw, beta90sw, bsw = betasw_ZHH2009(l, temp, theta, salinity, delta)
    betap = beta - betasw
    bbp = betap * 2 * np.pi * Xi
    return bbp

def scatter_conversion_and_despiking(profiles:list[Profile]) -> list[Profile]:
    print("Despiking and converting scatter to bbp...")
    # interpolate temperature and salinity
    # calculate bbp using code from kate
    # apply 30 wide median, lowpass, 40 wide median and then 7 wide mean to bbp to get despiked

    # alternative method is the same as above, but then averaged with an average local minima (4x10wide rolling mean of the 30 wide minima)

    for profile in profiles:
        beta = np.asarray(profile.data["scatter_650"])
        temp = np.asarray(profile.data["temperature_final"].interpolate())
        salinity = np.asarray(profile.data["salinity_final"].interpolate())   
        profile.data["bbp"] = beta_to_bbp(beta, temp, salinity)
        bbp  = profile.data["bbp"]


        bbp_local_minima = bbp.rolling(window=7, min_periods=1, center=True).min()
        #for i in range(4):
        #   bbp_local_minima = bbp_local_minima.rolling(window=15, min_periods=1, center=True).mean()
        bbp_local_minima = bbp_local_minima.rolling(window=7, min_periods=1, center=True).max()


        bbp = bbp.rolling(window=30, min_periods=1, center=True).median()
        b, a = sp.signal.butter(3, 0.1, analog=False)
        bbp = sp.signal.filtfilt(b, a, bbp.interpolate())
        profile.data["bbp_mean_despiked"] = bbp
        bbp = profile.data["bbp_mean_despiked"]
        bbp = bbp.rolling(window=40, min_periods=1, center=True).median()
        bbp = bbp.rolling(window=7, min_periods=1, center=True).mean()

    
        profile.data["bbp_mean_despiked"] = bbp    
        profile.data["bbp_spikes"] = profile.data["bbp"] - profile.data["bbp_mean_despiked"]

        bbp_alternative= bbp_local_minima #+ 0.5*(bbp - bbp_local_minima)
        profile.data["bbp_minimum_despiked"] = bbp_alternative
        profile.data["bbp_minimum_spikes"] = profile.data["bbp"] - profile.data["bbp_minimum_despiked"]

    return profiles


def deep_chlorophyll_correction(profiles:list[Profile]) -> list[Profile]:
    print("Correcting deep chlorophyll...")
    for profile in profiles:

        df = profile.data
        deep_df = df[df["depth"] > 300]
        deep_c_95 = deep_df["chlorophyll"].quantile(0.95)
        df["chlorophyll"] -= deep_c_95

        df.loc[df["chlorophyll"] < 0, "chlorophyll"] = 0

        profile.data = df
            
    return profiles


def MLD_calculation(profiles:list[Profile]) -> list[Profile]:
    print("Calculating MLDs...")
    for profile in profiles:
        salinity = profile.data["salinity_final"].interpolate()
        pressure = profile.data["pressure"].interpolate()
        temperature = profile.data["temperature_final"].interpolate()
        lat = profile.data["latitude"]
        lon = profile.data["longitude"]
        corrected_salinity = SA_from_SP(salinity, pressure, lon, lat)
        corrected_temperature = CT_from_t(corrected_salinity, temperature, pressure)
             
        absolute_density = sigma0(corrected_salinity, corrected_temperature)
        
        profile.data["density"] = absolute_density

        

        df = profile.data
        df = df.sort_values("depth")
        temp_df = df.dropna(subset=["density"])
        surface_density = temp_df.iloc[0]["density"] if len(temp_df) > 0 else 0
        df["density_anomaly"] = df["density"] - surface_density 
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

            other_depth = profile.data[profile.data["original_index"] == other_index]["depth"].iloc[0]

            profile.mld = (mld_depth + other_depth)/2

    return profiles


def photic_calc(profiles:list[Profile]) -> list[Profile]:
    for p in profiles:
        df = p.data#[p.data["depth"] > 0.5]
        par_max = df["PAR"].max()
        df = df.sort_values("depth")
        df = df.dropna(subset=["PAR"])
        df = df[df["PAR"] < 0.01*par_max]
        photic_depth = df["depth"].iloc[0] if len(df) > 3 else np.nan
        p.photic_depth = photic_depth
    photic_depths = np.asarray([p.photic_depth if (p.photic_depth < 200 and p.photic_depth > 10) else np.nan for p in profiles ])
    photic_depths = pd.Series(photic_depths).interpolate(method='linear', limit_direction='both').to_numpy()
    for i, p in enumerate(profiles):
        p.photic_depth = photic_depths[i]       
    return profiles


def preprocessing_function(profiles:list[Profile]) -> list[Profile]:
    profiles = scatter_conversion_and_despiking(profiles)
    profiles = deep_chlorophyll_correction(profiles)
    profiles = MLD_calculation(profiles)
    profiles = photic_calc(profiles)
    return profiles


def scatter_and_chlorophyll_processing(profiles:list[Profile], quench_method, use_cache:bool=True, **kwargs) -> list[Profile]:


    if use_cache and os.path.exists("Louis/cache/unprocessed.pkl"):
        with open("Louis/cache/unprocessed.pkl", "rb") as f:
            data = pd.read_pickle(f)
        profiles = data["profiles"]

    elif use_cache:
        print("No cache found...")
        exit()

    else:
        profiles = preprocessing_function(profiles)
        with open("Louis/cache/unprocessed.pkl", "wb") as f:
            pd.to_pickle({"profiles": profiles, "null": None}, f)
        

    profiles = quench_method(profiles, **kwargs)
    #despiking is "minimum" or "mean"
    return profiles


if __name__ == "__main__":
    from quenching.default import default_quenching_correction
    parameters = ["time", "longitude", "latitude",
                "depth", "chlorophyll", "pressure",
                "temperature_final", "salinity_final",
                "temperature", "salinity", "temperature_corrected_thermal",
                "profile_index", "scatter_650"]


    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                    use_cache=False,
                                                                    quenching_method=default_quenching_correction,
                                                                    use_downcasts=True,
                                                                    despiking_method="minimum")
    # mlds = [profile.mld for profile in all_valid_profiles]
    # indexes = [profile.index for profile in all_valid_profiles]

    # plt.scatter(indexes, mlds)
    # plt.show()
    # plt.plot(profile.data["depth"], profile.data["density_anomaly"], label="density")
    # plt.scatter(profile.data["depth"], profile.data["salinity_final"], label="temperature")
    # plt.show()





    # DESPIKING PLOT
    # plt.plot(profile.data["depth"], profile.data["bbp"], label="bbp")
    # plt.plot(profile.data["depth"], profile.data["bbp_mean_despiked"], label="despiked")
    # plt.plot(profile.data["depth"], profile.data["bbp_minimum_spikes"], label="alternative despiked")
    # plt.title(f"Profile {profile.index}, {profile.direction}")
    # plt.xlim(0, 100)
    # plt.legend()
    # plt.show()
