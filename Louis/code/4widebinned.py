from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib.axes import Axes
from plotting_functions import new_binned_plot
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(12, 11))
ax: Axes = fig.add_axes([0.06, 0.06, 0.19, 0.92])
ax2: Axes = fig.add_axes([0.27, 0.06, 0.19, 0.92], sharey=ax)
ax3: Axes = fig.add_axes([0.48, 0.06, 0.19, 0.92], sharey=ax)
ax4: Axes = fig.add_axes([0.69, 0.06, 0.19, 0.92], sharey=ax)
cbar_ax: Axes = fig.add_axes([0.9, 0.06, 0.02, 0.92])

profiles.pop(576)
interior1 = [p for p in profiles if p.index >= 495 and p.index < 550]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior1 = [p for p in profiles if p.index >= 550 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]

my_cmap = mpl.colormaps["inferno"].copy()

my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.006, clip=True)


pcm = new_binned_plot(interior1, ax, "bbp_debubbled_spikes_denoised", cmap=my_cmap, norm=my_norm, max_depth=1000)
pcm = new_binned_plot(interior2, ax2, "bbp_debubbled_spikes_denoised", cmap=my_cmap, norm=my_norm, max_depth=1000)
pcm = new_binned_plot(exterior, ax3, "bbp_debubbled_spikes_denoised", cmap=my_cmap, norm=my_norm, max_depth=1000)
pcm = new_binned_plot(ref, ax4, "bbp_debubbled_spikes_denoised", cmap=my_cmap, norm=my_norm, max_depth=1000)

ys_save = []
for axes, profile_set in [(ax, interior1), (ax2, interior2), (ax3, exterior), (ax4, profiles[764:818])]:
    xs, ys = [], []
    for p in profile_set:
        data = p.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=1, max_depth=1000, includeZero=True)
        data = [d if not np.isnan(d) else 0 for d in data]
        depth_integrated_under_100m = np.sum(data[:100])
        depth_integrated_over_100m = np.sum(data[100:800])
        ys.append(depth_integrated_over_100m)
        xs.append(p.start_time)
    print(np.nanmean(ys))
    ys_save.append(ys)
    #axes.scatter(xs, ys, color="black", s=1)
    
interior_means = ys_save[0] + ys_save[1]
exterior_means = ys_save[2]
reference_means = ys_save[3]

mean_depth_integrated_between_100_and_800m = [interior_means, exterior_means, reference_means]
labels = ["Interior", "Exterior", "Reference"]



for axes, label in zip([ax, ax2, ax3, ax4], ['a', 'b', 'c', 'd']):
    axes.text(0.04, 0.02, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='left', color="#40FF00FF")




ax.set_ylabel("Depth (m)")
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])
ax2.tick_params(axis='y', labelleft=False)
ax3.tick_params(axis='y', labelleft=False)
ax4.tick_params(axis='y', labelleft=False)
#for ax in [ax, ax2, ax3, ax4]:
#    xticks = ax.get_xticks()
#    print(xticks)
 #   ax.set_xticks([17971, 17973, 17975], ["16/3/19", "18/3/19", "20/3/19"])
ax2.set_xlabel("Date", x=1.05)
plt.colorbar(pcm, cax=cbar_ax, orientation="vertical")
cbar_ax.set_ylabel(r"b$_{bp}$ (m$^{-1}$)")

#fig.tight_layout()
#plt.savefig("Louis/figures/figureE.png", dpi=300)
plt.show()