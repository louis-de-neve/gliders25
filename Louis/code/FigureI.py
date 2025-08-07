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


fig = plt.figure(figsize=(10, 7.7))
ax: Axes = fig.add_axes([0.1, 0.65, 0.35, 0.33])
axb: Axes = fig.add_axes([0.48, 0.65, 0.35, 0.33])
axb.invert_xaxis()
ax1: Axes = fig.add_axes([0.1, 0.29, 0.35, 0.33], sharex=ax, sharey=ax)
ax1b: Axes = fig.add_axes([0.48, 0.29, 0.35, 0.33], sharex=axb, sharey=axb)
ax2: Axes = fig.add_axes([0.1, 0.07, 0.35, 0.19], sharex=ax)
ax2b: Axes = fig.add_axes([0.48, 0.07, 0.35, 0.19], sharex=axb, sharey=ax2)
cbar_ax: Axes = fig.add_axes([0.85, 0.65, 0.02, 0.33])
cbar_ax2: Axes = fig.add_axes([0.85, 0.29, 0.02, 0.33])
profiles.pop(576)

profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)



profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 550]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior1 = [p for p in profiles if p.index >= 550 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
exterior = exterior1 + exterior2
interior = interior1 + interior2


print(exterior1[0].start_time, exterior1[-1].end_time)
print(exterior2[0].start_time, exterior2[-1].end_time)



for profiles, loop_ax, loop_ax1, loop_ax2 in [(profiles1, ax, ax1, ax2), (profiles2, axb, ax1b, ax2b)]:
    print(profiles[-1].end_time)
    az_depths = [-p.active_zone for p in profiles]

    # AXIS 0

    my_cmap = mpl.colormaps["viridis"].copy()
    my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
    my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)

    pcm = new_binned_plot(profiles, loop_ax, "chlorophyll_corrected", 3, 800, cmap=my_cmap, norm=my_norm)
    c1 = plt.colorbar(pcm, cax=cbar_ax)
    cbar_ax.set_ylabel(r"Chlorophyll (mg m$^{-}$)")


    my_cmap = mpl.colormaps["inferno"].copy()
    my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
    my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.003, clip=True)

    pcm2 = new_binned_plot(profiles, loop_ax1, "bbp_debubbled_despiked", 3, 800, cmap=my_cmap, norm=my_norm)
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
        az = []
        while len(times) < len(m):
            times.append(time.pop(0))
            baths.append(bath.pop(0))
        times.append(time.pop(0))
        baths.append(bath.pop(0))
        loop_ax2.plot(times, baths, color="black")


    az_depths = pd.Series([-p.active_zone for p in profiles]).interpolate(method="linear", limit_direction="both")
    ts = [p.start_time + 0.5*(p.end_time-p.start_time) for p in profiles]
    loop_ax.plot(ts, az_depths, color="red", label="High Chlorohyll Zone Depth")




axb.legend(loc="lower right", fontsize=8, framealpha=1)




ax.set_ylabel("Depth (m)")
ax1.set_ylabel("Depth (m)")
plt.setp(ax.get_xticklabels(), visible=False)
plt.setp(ax1.get_xticklabels(), visible=False)
plt.setp(axb.get_xticklabels(), visible=False)
plt.setp(ax1b.get_xticklabels(), visible=False)

plt.setp(axb.get_yticklabels(), visible=False)
plt.setp(ax1b.get_yticklabels(), visible=False)
plt.setp(ax2b.get_yticklabels(), visible=False)


ax.yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax.set_ylim(-800, 0)
    
ax2.set_xlabel("Date", x=1.04)
ax2.set_ylabel("Ocean Depth (m)")
ax2.yaxis.set_major_formatter(lambda x, pos: int(abs(x)))
ax2.set_xticks(ax2.get_xticks()[::2])
ax2b.set_yticks(ax2.get_yticks())
ax2.set_ylim(-6000, 0)



ax2.set_xticks([17968, 17970, 17972], ["13/3/19", "15/3/19", "17/3/19"])
ax2b.set_xticks([17973, 17975, 17977], ["18/3/19", "20/3/19", "22/3/19"])


ax.vlines([17971.3], -800, 0, color="white", linestyle="--", linewidth=1)
axb.vlines([17974.03], -800, 0, color="white", linestyle="--", linewidth=1)
ax1.vlines([17971.3], -800, 0, color="white", linestyle="--", linewidth=1)
ax1b.vlines([17974.03], -800, 0, color="white", linestyle="--", linewidth=1)
ax2.vlines([17971.3], -6000, 0, color="black", linestyle="--", linewidth=1)
ax2b.vlines([17974.03], -6000, 0, color="black", linestyle="--", linewidth=1)

ax2.grid(alpha=0.5)
ax2b.grid(alpha=0.5)

for axes, label in zip([ax, ax1, ax2, axb, ax1b, ax2b], ['a', 'c', 'e', 'b', 'd', 'f']):
    axes.text(0.02, 0.02, label, transform=axes.transAxes, fontsize=12, va='bottom', ha='left', color="#000000")



#fig.tight_layout()
plt.savefig("Louis/figures/figureI.png", dpi=300)
