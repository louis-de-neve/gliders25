from setup.setup import Profile, Transect, two_dimensional_binning

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
 

def binned_plot(valid_profiles:list[Profile], ax:plt.axes, parameter:str, bin_size:float=2, max_depth:float=1000., **kwargs) -> mpl.collections.PolyQuadMesh:
    data_array = two_dimensional_binning(valid_profiles, parameter, bin_size, max_depth)
    depth_bins = -np.arange(bin_size/2, max_depth, bin_size)
    time_bins = np.arange(data_array.shape[1])
    X, Y = np.meshgrid(time_bins, depth_bins)
    if parameter in ["chlorophyll", "chlorophyll_corrected"]:
        pcm = ax.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm(vmin=0.01, vmax=36))
    # elif parameter == "chlorophyll_corrected":
    #         pcm = ax.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm())
    else:
        pcm = ax.pcolor(X, Y, data_array, **kwargs)
    
    #ax.set_xlabel("Profile number")
    #ax.set_ylabel("Depth (m)")
    return pcm


def temp_salinity_plot(profiles:list[Profile], ax:plt.axes) -> mpl.collections.PathCollection:
    for profile in profiles:
        pcm = ax.scatter(profile.data["salinity_final"], profile.data["temperature_final"],
                   c=-profile.data["depth"], cmap="viridis", alpha=0.5, norm=mpl.colors.Normalize(vmin=-1000, vmax=0))
    return pcm  