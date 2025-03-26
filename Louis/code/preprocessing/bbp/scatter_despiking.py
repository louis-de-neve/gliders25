from preprocessing.bbp.beta_to_bbp import beta_to_bbp
import numpy as np


def scatter_conversion_and_despiking(profiles:list) -> list:
    print("Despiking and converting scatter to bbp...")
    # interpolate temperature and salinity
    # calculate bbp using code from kate
    # apply 30 wide median, lowpass, 40 wide median and then 7 wide mean to bbp to get despiked

    # alternative method is the same as above, but then averaged with an average local minima (4x10wide rolling mean of the 30 wide minima)

    for i, profile in enumerate(profiles):
        beta = np.asarray(profile.data["scatter_650"])
        temp = np.asarray(profile.data["temperature_final"].interpolate())
        salinity = np.asarray(profile.data["salinity_final"].interpolate())   

        profile.data["bbp"] = beta_to_bbp(beta, temp, salinity)

        temporary_df = profile.data.dropna(subset=["bbp"]).copy()

        bbp = temporary_df["bbp"]
        bbp_minima = bbp.rolling(window=7, min_periods=1, center=True).min()
        #for i in range(4):
        #   bbp_local_minima = bbp_local_minima.rolling(window=15, min_periods=1, center=True).mean()
        bbp_local_minima = bbp_minima.rolling(window=7, min_periods=1, center=True).max()
        
        temporary_df["bbp_minimum_despiked"] = bbp_local_minima

        profile.data = profile.data.merge(temporary_df, how="outer")
        profile.data["bbp_minimum_despiked"] = profile.data["bbp_minimum_despiked"].interpolate()
        profile.data["bbp_minimum_spikes"] = profile.data["bbp"] - profile.data["bbp_minimum_despiked"]


        # bbp = bbp.rolling(window=30, min_periods=1, center=True).median()
        # b, a = sp.signal.butter(3, 0.1, analog=False)
        # bbp = sp.signal.filtfilt(b, a, bbp.interpolate())
        # profile.data["bbp_mean_despiked"] = bbp
        # bbp = profile.data["bbp_mean_despiked"]
        # bbp = bbp.rolling(window=40, min_periods=1, center=True).median()
        # bbp = bbp.rolling(window=7, min_periods=1, center=True).mean()
    
    
        profile.data["bbp_mean_despiked"] = bbp    
        profile.data["bbp_spikes"] = profile.data["bbp"] - profile.data["bbp_mean_despiked"]

        profile.data["bbp_mean_despiked"] = bbp    
        profile.data["bbp_spikes"] = profile.data["bbp"] - profile.data["bbp_mean_despiked"]
    
        # profile.data["bbp_mean_despiked"] = bbp    
        # profile.data["bbp_spikes"] = profile.data["bbp"] - profile.data["bbp_mean_despiked"]

    return profiles