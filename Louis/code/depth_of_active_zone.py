import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from setup import import_split_and_make_transects
from plotting_functions import binned_plot, new_binned_plot


transects, all_valid_profiles = import_split_and_make_transects(use_cache=False,
                                                                use_downcasts=True,)

profiles = all_valid_profiles[460:666]

#profiles = all_valid_profiles[666:780]
#profiles = all_valid_profiles[36:65]

#profiles = all_valid_profiles[2:47] + all_valid_profiles[64:105]
# print(profiles[47].index)
# plt.plot(profiles[47].data["depth"], profiles[47].data["bbp_debubbled"], color="red")
# plt.plot(profiles[47].data["depth"], profiles[47].data["bbp_minimum_despiked"], color="blue")
# plt.show()
# profiles.pop(47)
#profiles.pop(14)
#profiles.pop(44)





ts = [p.transect_index for p in profiles]
if ts[0] != ts[-1]:
    change_index = ts.index(ts[-1])
else:
    change_index = None


fig = plt.figure(figsize=(8, 8))
bottom_ax = fig.add_axes([0.1, 0.1, 0.75, 0.27])  # [left, bottom, width, height]
main_ax = fig.add_axes([0.1, 0.4, 0.75, 0.55], sharex=bottom_ax)  # [left, bottom, width, height]
side_ax = fig.add_axes([0.87, 0.4, 0.02, 0.55])  # [left, bottom, width, height]
ax = [main_ax, bottom_ax, side_ax]


# AXIS 0
ax[0].set_ylabel("Depth (m)")
plt.setp(ax[0].get_xticklabels(), visible=False)

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.007, vmax=3, clip=True)
pcm = new_binned_plot(profiles, ax[0], "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)
ax[0].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
#ax[0].vlines(profiles[change_index].end_time, 0, -1000, color="red", linestyle="--")
ax[0].set_ylim(-1000, 0)

az = [-p.active_zone for p in profiles]
az = list(pd.Series(az).interpolate(limit=3))
st = [p.start_time + (p.end_time - p.start_time)/2 for p in profiles]
ax[0].plot(st, az, color="red")






# AXIS 1
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
    
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Depth of chlorophyll active zone (m)")
ax[1].yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax[1].set_xticks(ax[1].get_xticks()[::2])
#ax[1].vlines(profiles[change_index].end_time, 0, -4500, color="red", linestyle="--")
ax[1].set_ylim(-4500, 0)

# AXIS 2
plt.colorbar(pcm, cax=ax[2], orientation="vertical")
ax[2].set_ylabel(r"b$_{bp}$ (m$^{-1}$)")



plt.suptitle("Transects A and B")
plt.savefig("Louis/outputs/bathymetrynewtemp.png", dpi=300)
#plt.show()

