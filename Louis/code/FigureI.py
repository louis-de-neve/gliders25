from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib.axes import Axes
from plotting_functions import new_binned_plot
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

# from preprocessing.chlorophyll.default_quenching import default_quenching_correction
# profiles = default_quenching_correction(profiles)


fig = plt.figure(figsize=(8, 8))
ax: Axes = fig.add_axes([0.1, 0.62, 0.73, 0.37])
ax1: Axes = fig.add_axes([0.1, 0.23, 0.73, 0.37], sharex=ax, sharey=ax)
ax2: Axes = fig.add_axes([0.1, 0.06, 0.73, 0.15], sharex=ax)
cbar_ax: Axes = fig.add_axes([0.85, 0.62, 0.02, 0.37])
cbar_ax2: Axes = fig.add_axes([0.85, 0.23, 0.02, 0.37])
profiles.pop(576)

profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)






profiles = profiles[489:631]
print(profiles[0].index, profiles[-1].index)



# AXIS 0

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)

pcm = new_binned_plot(profiles, ax, "chlorophyll_corrected", 3, 1000, cmap=my_cmap, norm=my_norm)
c1 = plt.colorbar(pcm, cax=cbar_ax)
cbar_ax.set_ylabel(r"Chlorophyll (mg m$^{-}$)")


my_cmap = mpl.colormaps["inferno"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.003, clip=True)

pcm2 = new_binned_plot(profiles, ax1, "bbp_debubbled_despiked", 3, 1000, cmap=my_cmap, norm=my_norm)
c2 = plt.colorbar(pcm2, cax=cbar_ax2)
cbar_ax2.set_ylabel(r"b$_{bp}$ (m$^{-1}$)")




# AXIS 2
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
    ax2.plot(times, baths, color="black")


ax.set_ylabel("Depth (m)")
ax1.set_ylabel("Depth (m)")
plt.setp(ax.get_xticklabels(), visible=False)
plt.setp(ax1.get_xticklabels(), visible=False)
ax.yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax.set_ylim(-1000, 0)
    
ax2.set_xlabel("Date")
ax2.set_ylabel("Ocean Depth (m)")
ax2.yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax2.set_xticks(ax2.get_xticks()[::2])
ax2.set_ylim(-6000, 0)

ax2.grid(alpha=0.5)

#fig.tight_layout()
print(cbar_ax2.get_xticks())
plt.savefig("Louis/figures/figureI.png", dpi=300)
