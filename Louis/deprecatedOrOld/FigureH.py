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


fig = plt.figure(figsize=(5, 4))
ax: Axes = fig.add_axes([0.14, 0.1, 0.62, 0.4])
ax2: Axes = fig.add_axes([0.14, 0.57, 0.62, 0.4], sharex=ax)
cbar_ax: Axes = fig.add_axes([0.8, 0.1, 0.04, 0.87])
profiles.pop(576)


profiles = profiles[544:598]
profiles.pop(6)

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)


pcm = new_binned_plot(profiles, ax2, "chlorophyll", bin_size=3, cmap=my_cmap, norm=my_norm)
pcm = new_binned_plot(profiles, ax, "chlorophyll_corrected", bin_size=3, cmap=my_cmap, norm=my_norm)


for axes, label in zip([ax2, ax], ['a', 'b', 'c', 'd']):
    axes.text(0.04, 0.02, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='left', color="#000000FF")


# mldmap = [-p.mld for p in profiles]
# times = [p.start_time for p in profiles]
# ax.plot(times, mldmap, color="red", label="MLD", linestyle="dashed", linewidth=1.5)
# ax2.plot(times, mldmap, color="red", label="Mixed Layer Depth", linestyle="dashed", linewidth=1.5)

ax.set_ylim(-40, 0)
ax2.set_ylim(-40, 0)

ax.set_ylabel("Depth (m)")
ax2.set_ylabel("Depth (m)")
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])
ax2.set_yticklabels([f"{int(abs(label))}" for label in ax2.get_yticks()])


for axes in [ax2]:
    xticks = axes.get_xticks()
    print(xticks)
    axes.set_xticks([17971, 17973, 17975], ["16/3/19", "18/3/19", "20/3/19"])
plt.setp(ax2.get_xticklabels(), visible=False)
#ax2.legend(loc="lower right", fontsize=8)

plt.colorbar(pcm, cax=cbar_ax, orientation="vertical")
cbar_ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")
ax.set_xlabel("Date")
#fig.tight_layout()
plt.savefig("Louis/figures/figureH.png", dpi=300)
