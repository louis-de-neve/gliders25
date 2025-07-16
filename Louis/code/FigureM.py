from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib.axes import Axes
from plotting_functions import new_binned_plot
from preprocessing.depth_calculations.chlorophyll_zone import chlorophyll_zone
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

profiles = chlorophyll_zone(profiles)

fig = plt.figure(figsize=(6, 4))
ax: Axes = fig.add_axes([0.1, 0.1, 0.36, 0.88])
ax2: Axes = fig.add_axes([0.49, 0.1, 0.36, 0.88], sharey=ax)


cbar_ax: Axes = fig.add_axes([0.87, 0.1, 0.02, 0.88])
profiles.pop(576)

profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)
profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.007, vmax=3, clip=True)
pcm = new_binned_plot(profiles1, ax, "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)
pcm = new_binned_plot(profiles2, ax2, "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)


for a, pf in [(ax, profiles1), (ax2, profiles2)]:

    az = [-p.active_zone for p in pf if p.active_zone > p.photic_depth]
    az = list(pd.Series(az).interpolate(limit=3))

    pz = [-p.photic_depth for p in pf if p.active_zone > p.photic_depth]
    pz = list(pd.Series(pz).interpolate(limit=3))

    st = [p.start_time + (p.end_time - p.start_time)/2 for p in pf if p.active_zone > p.photic_depth]
    a.plot(st, az, color="red", label="High Chlorophyll zone")
    a.plot(st, pz, color="#000000", label="Photic depth")



ax.set_ylim(-300, 0)
ax2.set_ylim(-300, 0)
ax.set_ylabel("Depth (m)")
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])

ax.set_xticks([17968, 17970, 17972], ["13/3/19", "15/3/19", "17/3/19"])
ax2.set_xticks([17973, 17975, 17977], ["18/3/19", "20/3/19", "22/3/19"])

ax2.invert_xaxis()
for axes, label in zip([ax, ax2], ['a', 'b', 'c', 'd']):
    axes.text(0.91, 0.01, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='left', color="#40FF00FF")

ax.set_xlabel("Date", x=1.03)

plt.colorbar(pcm, cax=cbar_ax, orientation="vertical")
cbar_ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")
ax.legend(loc="lower left", fontsize=8)
#fig.tight_layout()
plt.setp(ax2.get_yticklabels(), visible=False)
plt.savefig("Louis/figures/figureM.png", dpi=300)
