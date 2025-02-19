import matplotlib.pyplot as plt
from setup import import_split_and_make_transects
from plotting_functions import binned_plot, temp_salinity_plot, transect_map


def run():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all")

    print("here")


    transect = transects[0]
    d = transect.get_profiles()[8].data

    d["scatter_smoothed"] = d["scatter_650"].rolling(window=20, center=True).mean()
#
    #plt.plot(d["depth"], d["scatter_650"])
    plt.plot(d["depth"], d["scatter_smoothed"], color="red")
    plt.show()

    plt.hist(d[d["depth"] > 300]["chlorophyll"], bins=100)
    plt.show()
    
    #all transect chlorophyll plot:
    fig, axs = plt.subplots(2, 5, figsize=(30, 10), sharey=True)
    axs = axs.flatten()

    for transect, ax in zip(transects, axs):
        ax.set_title(transect.name)
        pcm = binned_plot(transect.get_profiles(), ax, "chlorophyll", bin_size=2)

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

