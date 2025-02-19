from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from betasw_zhh09 import betasw_ZHH2009

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

    for profile in profiles:
        beta = np.asarray(profile.data["scatter_650"])
        temp = np.asarray(profile.data["temperature_final"])
        salinity = np.asarray(profile.data["salinity_final"])
        profile.data["bbp"] = beta_to_bbp(beta, temp, salinity)

    return profiles



transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_conversion_and_despiking)

profile = all_valid_profiles[50]

plt.plot(profile.data["depth"], profile.data["temperature_final"], label="bbp")
plt.show()