import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from plotting_functions import binned_plot
import numpy as np
import matplotlib as mpl
import matplotlib.axes as mpl_axes

transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing)

def map_plot(profiles:list[Profile], colour_parameter:str, ax:mpl_axes.Axes) -> None:
    longitudes, latitudes, hues = [], [], []
    for p in profiles:
        if p.direction == "up":
            data = p.data.sort_values("depth")
            data = data[data["depth"] > 1]
            xs = np.asarray(data["depth"])
            ys = np.asarray(data[colour_parameter])
            ys = np.nan_to_num(ys)
            integral = np.trapezoid(ys, x=xs)
            if integral > 1.:
                hues.append(integral)
                longitudes.append(p.start_location[0])
                latitudes.append(p.start_location[1])
          
    hues = np.asarray(hues)

    pcm = ax.scatter(longitudes, latitudes, c=hues, cmap="viridis", norm=mpl.colors.LogNorm(vmin=10, vmax=500))
    return pcm
    
fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
pcm = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0])
ax[0].set_xlabel("Longitude")
ax[0].set_ylabel("Latitude")

plt.colorbar(pcm, cax=ax[1], orientation="horizontal")
ax[1].set_xlabel(r"Depth Integrated Chlorophyll (mg m$^{-2}$)")
plt.tight_layout()
plt.savefig("Louis/outputs/map_plot.png", dpi=300)
plt.show()