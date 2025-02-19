from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from betasw_zhh09 import betasw_ZHH2009
import scipy as sp
from plotting_functions import binned_plot
from gsw import SA_from_SP, CT_from_t, sigma0


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


        bbp_local_minima = bbp.rolling(window=20, min_periods=1, center=True).min()
        for i in range(4):
           bbp_local_minima = bbp_local_minima.rolling(window=15, min_periods=1, center=True).mean()


        bbp = bbp.rolling(window=30, min_periods=1, center=True).median()
        b, a = sp.signal.butter(3, 0.1, analog=False)
        bbp = sp.signal.filtfilt(b, a, bbp.interpolate())
        profile.data["bbp_despiked"] = bbp
        bbp = profile.data["bbp_despiked"]
        bbp = bbp.rolling(window=40, min_periods=1, center=True).median()
        bbp = bbp.rolling(window=7, min_periods=1, center=True).mean()

        


        profile.data["bbp_despiked"] = bbp    
        profile.data["bbp_spikes"] = profile.data["bbp"] - profile.data["bbp_despiked"]

        bbp_alternative= bbp_local_minima + 0.5*(bbp - bbp_local_minima)
        profile.data["bbp_alternative_despiked"] = bbp_alternative
        profile.data["bbp_alternative_spikes"] = profile.data["bbp"] - profile.data["bbp_alternative_despiked"]

    return profiles


def deep_chlorophyll_correction(profiles:list[Profile]) -> list[Profile]:

    for profile in profiles:

        df = profile.data
        deep_df = df[df["depth"] > 300]
        deep_c = deep_df["chlorophyll"]
        med_deep_c = deep_c.median()

        profile.data["chlorophyll"] = profile.data["chlorophyll"] - med_deep_c
        

    return profiles


def MLD_calculation(profiles:list[Profile]) -> list[Profile]:
    for profile in profiles:
        salinity = profile.data["salinity_final"].interpolate()
        pressure = profile.data["pressure"].interpolate()
        temperature = profile.data["temperature_final"].interpolate()
        lat = profile.data["latitude"]
        lon = profile.data["longitude"]
        corrected_salinity = SA_from_SP(salinity, pressure, lon, lat)
        corrected_temperature = CT_from_t(corrected_salinity, temperature, pressure)
             
        absolute_density = sigma0(corrected_salinity, corrected_temperature)
        
        profile.data["density_anomaly"] = absolute_density

        df = profile.data
        df = df.sort_values("depth")
        surface_density = df.iloc[0]["density_anomaly"]
        df["density_anomaly"] = absolute_density - surface_density
        df = df[df["density_anomaly"] > 0.03]
        df = df[df["depth"] < 200]

        if len(df) == 0:
            profile.mld = None
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


def scatter_and_chlorophyll_preprocessing(profiles:list[Profile]) -> list[Profile]:
    profiles = scatter_conversion_and_despiking(profiles)
    profiles = deep_chlorophyll_correction(profiles)
    profiles = MLD_calculation(profiles)
    return profiles



parameters = ["time", "longitude", "latitude",
              "depth", "chlorophyll", "pressure",
              "temperature_final", "salinity_final",
              "temperature", "salinity", "temperature_corrected_thermal",
              "profile_index", "scatter_650"]


transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_preprocessing, parameters=parameters)

profile = all_valid_profiles[4]

mlds = [profile.mld for profile in all_valid_profiles]
indexes = [profile.index for profile in all_valid_profiles]

plt.scatter(indexes, mlds)
plt.show()

plt.plot(profile.data["depth"], profile.data["density_anomaly"], label="bbp")
plt.show()





# DESPIKING PLOT
#plt.plot(profile.data["depth"], profile.data["bbp"], label="bbp")
#plt.plot(profile.data["depth"], profile.data["bbp_despiked"], label="despiked")
#plt.plot(profile.data["depth"], profile.data["bbp_alternative_despiked"], label="alternative despiked")
#plt.title(f"Profile {profile.index}, {profile.direction}")
#plt.xlim(0, 100)
#plt.legend()
#plt.show()
