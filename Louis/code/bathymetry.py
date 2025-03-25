import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot, new_binned_plot
import matplotlib as mpl
from matplotlib import MatplotlibDeprecationWarning
import warnings
import numpy as np

warnings.filterwarnings("ignore",category=MatplotlibDeprecationWarning)





transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_supercache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=False,
                                                                despiking_method="minimum")


#profiles = all_valid_profiles[36:65]

profiles = all_valid_profiles[2:47] + all_valid_profiles[64:105]
profiles.pop(5)

#profiles = [p for p in profiles if p.data["depth"].max() > 425]

#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(8, 8))
bottom_ax = fig.add_axes([0.1, 0.1, 0.75, 0.27])  # [left, bottom, width, height]
main_ax = fig.add_axes([0.1, 0.4, 0.75, 0.55], sharex=bottom_ax)  # [left, bottom, width, height]
side_ax = fig.add_axes([0.87, 0.4, 0.02, 0.55])  # [left, bottom, width, height]
ax = [main_ax, bottom_ax, side_ax]

# AXIS 0
ax[0].set_ylabel("Depth (m)")
plt.setp(ax[0].get_xticklabels(), visible=False)
pcm = new_binned_plot(profiles, ax[0], "bbp_minimum_despiked", 10, 1000, cmap="inferno", norm=mpl.colors.LogNorm(vmin=0.0005, vmax=0.001))
ax[0].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax[0].vlines(profiles[40].end_time, 0, -1000, color="red", linestyle="--")
ax[0].set_ylim(-995, 0)

bath = [p.bathymetry for p in profiles]
time = [p.start_time for p in profiles]
valid_nexts = np.asarray([p.valid_next for p in profiles])
masks = "".join(valid_nexts).rsplit("n")
masks.pop(-1)
for m in masks:
    times = []
    baths = []
    while len(times) < len(m):
        times.append(time.pop(0))
        baths.append(bath.pop(0))
    times.append(time.pop(0))
    baths.append(bath.pop(0))
    ax[1].plot(times, baths, color="black")
    


# AXIS 1
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Ocean Depth (m)")
ax[1].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax[1].set_xticks(ax[1].get_xticks()[::2])
ax[1].vlines(profiles[40].end_time, 0, -4500, color="red", linestyle="--")
ax[1].set_ylim(-4500, 0)

# AXIS 2
plt.colorbar(pcm, cax=ax[2], orientation="vertical")
ax[2].set_ylabel(r"b$_{bp}$ (m$^{-1}$)")









plt.suptitle("Transects A and B")
#plt.tight_layout()
plt.savefig("Louis/outputs/bathymetrynew.png", dpi=300)
#plt.show()

