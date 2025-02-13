import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from setup import Profile, Transect, import_split_and_make_transects, two_dimensional_binning

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
    pcm = ax.pcolor(X, Y, data_array, norm=mpl.colors.LogNorm(vmin=0.03, vmax=30))
    ax.set_xlabel("Downcast number")
    #ax.set_ylabel("Depth (m)")
    return pcm


def temp_salinity_plot(profiles:list[Profile], ax:plt.axes) -> mpl.collections.PathCollection:
    for profile in profiles:
        pcm = ax.scatter(profile.data["salinity_final"], profile.data["temperature_final"],
                   c=-profile.data["depth"], cmap="viridis", alpha=0.5, norm=mpl.colors.Normalize(vmin=-1000, vmax=0))
    return pcm  

def run():
    transects, all_valid_profiles = import_split_and_make_transects()

    
    #all transect chlorophyll plot:
    fig, axs = plt.subplots(2, 5, figsize=(30, 10), sharey=True)
    axs = axs.flatten()

    for transect, ax in zip(transects, axs):
        ax.set_title(transect.name)
        pcm = binned_plot(transect.get_profiles(), ax, "chlorophyll")

    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
    cbar_ax.set_xlabel("Chlorophyll (mg/m^3)")

    axs[0].set_ylabel("Depth (m)")
    axs[5].set_ylabel("Depth (m)")
    plt.savefig("Louis/outputs/chlorophyll_all_transects.png", dpi=300)
    plt.show()


    #all transect temp/salinity plot:
    fig, axs = plt.subplots(2, 5, figsize=(30, 10), sharey=True)
    axs = axs.flatten()

    for transect, ax in zip(transects, axs):
        ax.set_title(transect.name)
        pcm = temp_salinity_plot(transect.get_profiles(), ax)

    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
    cbar_ax.set_xlabel("Depth (m)")

    plt.savefig("Louis/outputs/TS_all_transects.png", dpi=300)
    plt.show()
    

    #transect map plot:
    transect_map(transects, all_valid_profiles)
    plt.savefig("Louis/outputs/transect_map.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    run()

