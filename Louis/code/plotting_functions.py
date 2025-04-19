from setup import Profile, Transect, two_dimensional_binning, import_split_and_make_transects

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from scipy.interpolate import griddata
 

def binned_plot(valid_profiles:list[Profile], ax:plt.axes, parameter:str, bin_size:float=2, max_depth:float=1000., **kwargs) -> mpl.collections.PolyQuadMesh:
    data_array = two_dimensional_binning(valid_profiles, parameter, bin_size, max_depth)
    depth_bins = -np.arange(0, max_depth+bin_size, bin_size)
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


def new_binned_plot(valid_profiles:list[Profile], ax:plt.axes, parameter:str, bin_size:float=2, max_depth:float=1000., **kwargs) -> mpl.collections.PolyQuadMesh:
    dirs = [p.direction for p in valid_profiles]
    
    depth_bins = -np.arange(0, max_depth+bin_size, bin_size)
   
    
    for i, p in enumerate(valid_profiles):
        p.data = p.data.sort_values("depth")
        p.data = p.data.dropna(subset=[parameter])
        data = p.apply_binning_to_parameter(parameter, bin_size, max_depth)
        data = np.asarray([data]).T

        end_time = p.start_time + 2*(p.end_time - p.start_time)
        
        p.valid_next = "n"
        if "down" in dirs:
            end_time = p.end_time 
            if i != len(valid_profiles)-1 and valid_profiles[i+1].index - p.index < 4:
                end_time = valid_profiles[i+1].start_time
                p.valid_next="y"
                
        time_bins = [p.start_time, end_time]      
        X, Y = np.meshgrid(time_bins, depth_bins)

        pcm = ax.pcolormesh(X, Y, data, **kwargs)
    return pcm





def temp_salinity_plot(profiles:list[Profile], ax:plt.axes) -> mpl.collections.PathCollection:
    for profile in profiles:
        pcm = ax.scatter(profile.data["salinity_final"], profile.data["temperature_final"],
                   c=-profile.data["depth"], cmap="viridis", alpha=0.5, norm=mpl.colors.Normalize(vmin=-1000, vmax=0))
    return pcm  

if __name__ == "__main__":
    transects, all_valid_profiles = import_split_and_make_transects(use_cache=True)
    ps = all_valid_profiles[2:22] + all_valid_profiles[60:80] 
    ps.pop(5)
    new_binned_plot(ps, plt.gca(), "chlorophyll_corrected", bin_size=2, max_depth=150)
    plt.show()