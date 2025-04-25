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

fig = plt.figure(figsize=(8, 8))
ax: Axes = fig.add_axes([0.1, 0.1, 0.75, 0.8])
cbar_ax: Axes = fig.add_axes([0.89, 0.1, 0.02, 0.8])
profiles.pop(576)

profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)
profiles = profiles[489:631]

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.007, vmax=3, clip=True)
pcm = new_binned_plot(profiles, ax, "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)


az = [-p.active_zone for p in profiles if p.active_zone > p.photic_depth]
az = list(pd.Series(az).interpolate(limit=3))

pz = [-p.photic_depth for p in profiles if p.active_zone > p.photic_depth]
pz = list(pd.Series(pz).interpolate(limit=3))

st = [p.start_time + (p.end_time - p.start_time)/2 for p in profiles if p.active_zone > p.photic_depth]
ax.plot(st, az, color="red", label="Active zone")
ax.plot(st, pz, color="#000000", label="Photic depth")




ax.set_ylim(-400, 0)
ax.set_ylabel("Depth (m)")
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])
xticks = ax.get_xticks()
print(xticks)
ax.set_xticks(xticks[::2])

plt.colorbar(pcm, cax=cbar_ax, orientation="vertical")
cbar_ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")
ax.legend(loc="lower left", fontsize=8)
#fig.tight_layout()
plt.savefig("Louis/figures/figureM.png", dpi=300)
