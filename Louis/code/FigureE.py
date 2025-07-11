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
profiles = profiles[544:597]


my_cmap = mpl.colormaps["inferno"].copy()

my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.003, clip=True)


pcm = new_binned_plot(profiles, ax, "bbp", cmap=my_cmap, norm=my_norm, max_depth=500)
pcm = new_binned_plot(profiles, ax2, "bbp_minimum_despiked", cmap=my_cmap, norm=my_norm, max_depth=500)
pcm = new_binned_plot(profiles, ax3, "bbp_debubbled_despiked", cmap=my_cmap, norm=my_norm, max_depth=500)
pcm = new_binned_plot(profiles, ax4, "bbp_debubbled_spikes_denoised", cmap=my_cmap, norm=my_norm, max_depth=500)

for axes, label in zip([ax, ax2, ax3, ax4], ['a', 'b', 'c', 'd']):
    axes.text(0.04, 0.02, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='left', color="#40FF00FF")




ax.set_ylabel("Depth (m)")
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])
ax2.tick_params(axis='y', labelleft=False)
ax3.tick_params(axis='y', labelleft=False)
ax4.tick_params(axis='y', labelleft=False)
for ax in [ax, ax2, ax3, ax4]:
    xticks = ax.get_xticks()
    print(xticks)
    ax.set_xticks([17971, 17973, 17975], ["16/3/19", "18/3/19", "20/3/19"])
ax2.set_xlabel("Date", x=1.05)
plt.colorbar(pcm, cax=cbar_ax, orientation="vertical")
cbar_ax.set_ylabel(r"b$_{bp}$ (m$^{-1}$)")

#fig.tight_layout()
plt.savefig("Louis/figures/figureE.png", dpi=300)
