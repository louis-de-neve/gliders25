import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot
import matplotlib as mpl
from matplotlib import MatplotlibDeprecationWarning
import warnings

warnings.filterwarnings("ignore",category=MatplotlibDeprecationWarning)





transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_supercache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=False,
                                                                despiking_method="minimum")


profiles = all_valid_profiles[36:65]

#profiles = all_valid_profiles[2:47] + all_valid_profiles[64:105]
#profiles.pop(5)

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
pcm = binned_plot(profiles, ax[0], "bbp_minimum_spikes", 10, 1000, cmap="inferno", norm=mpl.colors.LogNorm(vmin=0.00005, vmax=0.001))
ax[0].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
#ax[0].vlines(4.5, 0, -1000, color="red", linestyle="--")


# AXIS 1
ax[1].set_xlabel("Profile Number")
ax[1].set_ylabel("Ocean Depth (m)")
bath = [p.bathymetry for p in profiles]
ax[1].plot(range(len(bath)), bath, color="black")
ax[1].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
#ax[1].vlines(4.5, 0, -4500, color="red", linestyle="--")
ax[1].set_ylim(-4500, 0)

# AXIS 2
plt.colorbar(pcm, cax=ax[2], orientation="vertical")
ax[2].set_ylabel(r"b$_{bp}$ (m$^{-1}$)")









plt.suptitle("AB turning point")
#plt.tight_layout()
plt.savefig("Louis/outputs/bathymetrynew.png", dpi=300)
#plt.show()
