import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import warnings
from code.setup.setup import import_split_and_make_transects, Profile, Transect, two_dimensional_binning
from code.preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from code.preprocessing.quenching.default import default_quenching_correction



transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_cache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_upcasts=True,
                                                                despiking_method="minimum")

plt.plot([p.photic_depth for p in all_valid_profiles])
plt.show()





# INDIVIDUAL NORMALISED
# for j in range(160):
#     ps = profiles[20*j:20*j+20]
#     fig, axs = plt.subplots(5, 4)
#     axs = axs.flatten()
#     for i, profile in enumerate(ps):
#         c = "red" if profile.night else "black"
#         array = np.asarray(profile.apply_binning_to_parameter("chlorophyll", 1, 1000))
#         array1max = np.nanmax(array) 
#         array *= 1/array1max
#         array2 = np.asarray(profile.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000))
#         array2 *= 1/np.nanmax(array2)
#         array3 = np.asarray(profile.apply_binning_to_parameter("chlorophyll_corrected", 1, 1000))
#         array3 *= 1/array1max

#         axs[i].vlines(profile.mld, 0, 2, color="red", linestyle="--")
#         axs[i].plot(array2, c="#6F6D6DE1")
#         axs[i].plot(array, c=c)
#         axs[i].plot(array3, c="#5F9A3FB2")
#         axs[i].set_xlim(0, 120)
#         top = max([1, array3.max()])
#         axs[i].set_ylim(0, top+0.1)
#     plt.suptitle(f"{20*j} to {20*j+19}")
#     plt.show()


    

exit()
pass
# NORMALISED EXPERIMENTS

profiles = all_valid_profiles
night_timings = {}
for i, profile in enumerate(profiles):
    if profile.night and (not np.isnan(profile.CtoB_ML_mean) and profile.direction == "up"):
        night_timings[profile.surface_time] = i

for profile in profiles:
    nearest_night_surface_time = min(night_timings.keys(), key=lambda x: abs(x - profile.surface_time))
    nearest_night_index = night_timings[nearest_night_surface_time]
    night_CtoB_mean = profiles[nearest_night_index].CtoB_ML_mean    


    night_chlorophyll = np.asarray(profiles[nearest_night_index].apply_binning_to_parameter("chlorophyll", 1, 1000))
    day_chlorophyll = np.asarray(profile.apply_binning_to_parameter("chlorophyll", 1, 1000))
    corrected = np.asarray(profile.apply_binning_to_parameter("chlorophyll_corrected", 1, 1000))
    bbp = np.asarray(profile.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000))

    normalized_bbp = bbp / np.nanmax(bbp)
    normalized_night_chlorophyll = night_chlorophyll / np.nanmax(night_chlorophyll)
    day_normalisation = np.nanmax(day_chlorophyll)
    normalized_day_chlorophyll = day_chlorophyll / day_normalisation
    normalized_corrected = corrected / day_normalisation
    normalized_difference = normalized_night_chlorophyll - normalized_day_chlorophyll

    diff_series = pd.Series(normalized_difference).rolling(5).mean()

    rolling_normal_bbp = pd.Series(normalized_bbp).rolling(5).mean()
    rolling_normal_c = pd.Series(normalized_day_chlorophyll).rolling(5).mean()
    rolling_normal_diff = np.asarray(rolling_normal_bbp - rolling_normal_c)
    rolling_normal_diff_reversed = rolling_normal_diff[:120]
    rolling_normal_diff_reversed = rolling_normal_diff_reversed[::-1]

    d2 = 0
    breaker = True
    for i, val in enumerate(rolling_normal_diff_reversed):
        if val < 0 and breaker and rolling_normal_diff_reversed[i+1] > 0:
            breaker = False
            d2=120-i




    bins = np.arange(1/2, 1000, 1)
    difference = night_chlorophyll - day_chlorophyll

    ### norm plots
    # plt.plot(bins, rolling_normal_bbp, label="bbp")
    # plt.plot(bins, rolling_normal_c, label="Day")
    # plt.plot(bins, rolling_normal_diff, label="Difference")
    # plt.plot(bins, diff_series, c="#2431C4FF")

    
    plt.plot(bins, difference, label="Difference")
   
    plt.plot(bins, day_chlorophyll, label="Day")
    plt.plot(bins, night_chlorophyll, label="Night")
    plt.plot(bins, corrected, label="Corrected")
    plt.plot(bins, bbp, label="bbp")


    plt.xlim(0, 120)
    # difference.min()-1, max([day_chlorophyll.max(), night_chlorophyll.max()])+1]
    ylims = plt.ylim()
    plt.vlines(profile.mld, -100, 100, color="red", label="MLD")
    plt.vlines(d2, -100, 100, color="green", label="diff_intersection")
    plt.hlines(0, 120, 0, color="#535353FF")
    plt.ylim(ylims)
    plt.legend()
    plt.show()