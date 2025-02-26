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


def quenching_correction(profiles:list[Profile], despiking_method:str="minimum", quench_method:str="night") -> list[Profile]:
    print("Applying quenching correction...")
    with open("Louis/day_night1.txt", "r") as f:
        night = f.readlines()
        night = [True if i.rstrip("\n") == "1" else False for i in night]
        
    night_timings = {}

    for i, profile in enumerate(profiles):
        C_to_B_ratio = profile.data["chlorophyll"] / profile.data[f"bbp_{despiking_method}_despiked"]
        profile.data["CtoB"] = C_to_B_ratio

        mixed_layer_df = profile.data[profile.data["depth"] < profile.mld]
        mixed_layer_df = mixed_layer_df[mixed_layer_df["depth"] > 0.2]

        C_to_B_mixed_layer_max = mixed_layer_df["CtoB"].max()
        C_to_B_mixed_layer_mean = mixed_layer_df["CtoB"].mean()
        
        max_slice = mixed_layer_df[mixed_layer_df["CtoB"] == C_to_B_mixed_layer_max]
        if max_slice.empty == True:
            C_to_B_mixed_layer_max_depth = 0
        else:
            C_to_B_mixed_layer_max_depth = max_slice["depth"].iloc[0]

        profile.CtoB_ML_max = C_to_B_mixed_layer_max
        profile.CtoB_ML_mean = C_to_B_mixed_layer_mean
        profile.CtoB_ML_max_depth = C_to_B_mixed_layer_max_depth


        profile.night = night[i]
        if profile.direction == "up":
            profile.surface_time = profile.end_time
        else:
            profile.surface_time = profile.start_time


        if profile.night and not np.isnan(C_to_B_mixed_layer_mean):
            night_timings[profile.surface_time] = i

    for i, profile in enumerate(profiles):
        if not profile.night:

            nearest_night_surface_time = min(night_timings.keys(), key=lambda x: abs(x - profile.surface_time))
            nearest_night_index = night_timings[nearest_night_surface_time]
            night_CtoB_mean = profiles[nearest_night_index].CtoB_ML_mean         

            chlorophyll = profile.data["chlorophyll"]
            bbp = profile.data[f"bbp_{despiking_method}_despiked"]
            depth = profile.data["depth"]

            qf = night_CtoB_mean if quench_method == "night" else profile.CtoB_ML_max
            profile.qf = (night_CtoB_mean, profile.CtoB_ML_max)

            chlorophyll_corrected = []
            for i in range(depth.first_valid_index(), depth.last_valid_index()+1):
                if depth[i] < profile.CtoB_ML_max_depth:
                    chlorophyll_corrected.append(bbp[i] * qf)
                else:
                    chlorophyll_corrected.append(chlorophyll[i])
            
            profile.data["chlorophyll_corrected"] = chlorophyll_corrected
            profile.night_CtoB_mean = night_CtoB_mean
        else:
            profile.data["chlorophyll_corrected"] = profile.data["chlorophyll"]
            profile.night_CtoB_mean = None
            profile.qf = None

            

    return profiles



def scatter_and_chlorophyll_preprocessing(profiles:list[Profile], despiking_method:str="minimum", quench_method:str="night") -> list[Profile]:
    profiles = scatter_conversion_and_despiking(profiles)
    profiles = deep_chlorophyll_correction(profiles)
    profiles = MLD_calculation(profiles)
    profiles = quenching_correction(profiles, despiking_method, quench_method)
    #despiking is "minimum" or "mean"
    #quenching is "night" or "mean"
    return profiles


if __name__ == "__main__":

    parameters = ["time", "longitude", "latitude",
                "depth", "chlorophyll", "pressure",
                "temperature_final", "salinity_final",
                "temperature", "salinity", "temperature_corrected_thermal",
                "profile_index", "scatter_650"]


    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_preprocessing, parameters=parameters)

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
