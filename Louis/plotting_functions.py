from setup import Profile, Transect, two_dimensional_binning

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def transect_map(transects:list[Transect], profiles:list[Profile]) -> None:
    for t in transects:
        x, y = tuple(zip(t.start_location, t.finish_location))
        plt.plot(x, y, label=t.name)
    for p in profiles:
        x, y = tuple(zip(p.start_location, p.end_location))
        plt.scatter(x, y, color="black", alpha=0.1)
        #plt.text(x[0], y[0], p.index, fontsize=5)
    plt.legend()
    

def binned_plot(valid_profiles:list[Profile], ax:plt.axes, parameter:str, bin_size:float=0.5) -> mpl.collections.PolyQuadMesh:
    data_array = two_dimensional_binning(valid_profiles, parameter, bin_size)
    depth_bins = -np.arange(0, 1000, bin_size)
    time_bins = np.arange(data_array.shape[1])
    X, Y = np.meshgrid(time_bins, depth_bins)
    if parameter == "chlorophyll":
        pcm = ax.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm(vmin=0.03, vmax=30))
    else:
        pcm = ax.pcolor(X, Y, data_array)
    
    ax.set_xlabel("Downcast number")
    #ax.set_ylabel("Depth (m)")
    return pcm


def temp_salinity_plot(profiles:list[Profile], ax:plt.axes) -> mpl.collections.PathCollection:
    for profile in profiles:
        pcm = ax.scatter(profile.data["salinity_final"], profile.data["temperature_final"],
                   c=-profile.data["depth"], cmap="viridis", alpha=0.5, norm=mpl.colors.Normalize(vmin=-1000, vmax=0))
    return pcm  