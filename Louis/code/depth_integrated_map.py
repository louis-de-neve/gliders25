import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot
import numpy as np
import pandas as pd
import matplotlib as mpl
from scipy.stats import linregress
import matplotlib.axes as mpl_axes

transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_cache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=True,
                                                                despiking_method="minimum")

def map_plot(profiles:list[Profile], colour_parameter:str, ax:mpl_axes.Axes, variable_limit=None) -> None:
    longitudes, latitudes, hues, all_hues = [], [], [], []
    for p in profiles:
        if p.direction == "up":
            data = p.data.sort_values("depth")
            data = data[data["depth"] > 1]

            if variable_limit is not None:
                data = variable_limit(p, data)
                
            xs = np.asarray(data["depth"])
            ys = np.asarray(data[colour_parameter])
            ys = np.nan_to_num(ys)
            integral = np.trapezoid(ys, x=xs)
            if integral > 1.:
                hues.append(integral)
                longitudes.append(p.start_location[0])
                latitudes.append(p.start_location[1])
            all_hues.append(integral)
          
    hues = np.asarray(hues)

    

    pcm = ax.scatter(longitudes, latitudes, c=hues, cmap="viridis", norm=mpl.colors.LogNorm(vmin=10, vmax=500))

    return pcm, all_hues
    
def above_photic_limit(p:Profile, d:pd.DataFrame) -> float:
    return d[d["depth"] < p.photic_depth]

    
def below_photic_limit(p:Profile, d:pd.DataFrame) -> float:
    return d[d["depth"] >= p.photic_depth]



fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
pcm, hues = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0], variable_limit=None)
pcm, hues_above = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0], variable_limit=above_photic_limit)
pcm, hues_below = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0], variable_limit=below_photic_limit)
# ax[0].set_xlabel("Longitude")
# ax[0].set_ylabel("Latitude")

# plt.colorbar(pcm, cax=ax[1], orientation="horizontal")
# ax[1].set_xlabel(r"Depth Integrated Chlorophyll (mg m$^{-2}$)")
# plt.tight_layout()
# plt.savefig("Louis/outputs/map_plot_chlorophyll.png", dpi=300)
# plt.show()
plt.close()


# zero = np.zeros(len(hues))
# plt.plot(hues, color="green", alpha=0.5)
# plt.fill_between(np.arange(len(hues)), hues_below, hues, color="green", alpha=0.5, label="Above Photic Zone")
# plt.plot(hues_below, color="red", alpha=0.5)
# plt.fill_between(np.arange(len(hues)), zero, hues_below, color="red", alpha=0.5, label="Below Photic Zone")
# plt.legend()

# plt.savefig("Louis/outputs/depth_integrated_chlorophyll_photic.png", dpi=300)
# plt.show()

plt.scatter(hues_above, hues_below, color="black", alpha=0.5, marker="x")
plt.xlabel("Chlorophyll Above Photic Zone")
plt.ylabel("Chlorophyll Below Photic Zone")
slope, intercept, r_value, p_value, std_err = linregress(hues_above, hues_below)
plt.plot(hues_above, slope * np.array(hues_above) + intercept, color="blue", label=f"y={slope:.2f}x+{intercept:.2f}\nR²={r_value**2:.2f}")
plt.legend()
plt.show()