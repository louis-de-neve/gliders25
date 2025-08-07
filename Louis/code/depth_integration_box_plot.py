from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
import seaborn as sns
from matplotlib.axes import Axes
from plotting_functions import new_binned_plot
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig, ax = plt.subplots(figsize=(5,5))



profiles.pop(576)
profiles = [p for p in profiles if p.index != 614]

profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 546]
exterior1 = [p for p in profiles if p.index >= 546 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]

mean_depth_integrated_between_100_and_900m = []
for profile_set in [interior, exterior, ref]:
    xs, ys = [], []
    for p in profile_set:
        data = p.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=1, max_depth=1000, includeZero=True)
        data = [d if not np.isnan(d) else 0 for d in data]
        depth_integrated_under_100m = np.sum(data[:100])
        depth_integrated_over_100m = np.sum(data[100:900])
        if depth_integrated_over_100m != 0:
            ys.append(depth_integrated_over_100m)
        xs.append(p.start_time)

    mean_depth_integrated_between_100_and_900m.append(ys)
    #axes.scatter(xs, ys, color="black", s=1)

labels = ["Interior", "Exterior", "Reference"]
labels = [1, 2, 3]
means = [np.nanmean(m) for m in mean_depth_integrated_between_100_and_900m]
stds = [np.nanstd(m) for m in mean_depth_integrated_between_100_and_900m]
print(means)
dfs = [pd.DataFrame({"datapoints": ys, "label": label, "split":True}) for ys, label in zip(mean_depth_integrated_between_100_and_900m, labels)]
df = pd.concat(dfs)
extra_df = pd.DataFrame({"datapoints": -1, "label": [1, 2, 3], "split": False})
df = pd.concat([df, extra_df])

std_error_bars = ax.boxplot(mean_depth_integrated_between_100_and_900m, 
                            positions=[0,1,2], 
                            tick_labels=labels,
                            #showfliers=False,
                            flierprops={"marker": "+", "markerfacecolor": "black", "markeredgecolor": "black", "markersize": 5},
                            capwidths=0.1,
                            widths=0.25,
                            medianprops={"color":"black"},
                            meanprops={"marker": "x", "markerfacecolor": "black", "markeredgecolor": "black"},
                            showmeans=True,
                            zorder=2)

# _, caps, _ = ax.errorbar([0, 1, 2], means, yerr=stds,
#                              fmt='o',
#                              capsize=5,
#                              capthick=1,
#                              color='black',
#                              zorder=2,
#                              label="Mean ± 1 Std. Dev.",)


for i, ys in enumerate(mean_depth_integrated_between_100_and_900m):
    ys = np.array(ys)
    hist_size = ((ys.max() - ys.min())/14)
    hist_range = (ys.min() - hist_size/2, ys.max() + hist_size/2)
    n, bins, rects = ax.hist(ys, bins=15, orientation='horizontal',
            alpha=0.5, 
            bottom=i,
            range=hist_range,
            color=sns.palettes.color_palette("Set1")[i],
            zorder=1)
    for r in rects:
        r.set_width(-r.get_width()/(len(ys)*0.5))
        width = r.get_width()
        left = r.get_x()
        r.set_x(left - width)
        r.set_width(width*2)
     
ax.set_ylim(0,0.08)
ax.set_yticks([0, 0.02, 0.04, 0.06, 0.08], ["0", "0.02", "0.04", "0.06", "0.08"])
ax.set_xlim(-0.6,2.5)
#sns.stripplot(data=df, ax=ax, x="label", y="datapoints", color="black", size=2, jitter=True)
#bplot = sns.kdeplot(data=df, ax=ax, x="label", y="datapoints", palette="Set2")
ax.set_ylabel("Depth Integrated Backscatter from spikes (m$^{-1}$ m)")
ax.set_xticks([0, 1, 2], ["Interior", "Edge", "Reference"])
fig.tight_layout()
plt.savefig("Louis/figures/depth_integration_box_plot.png", dpi=300)
#plt.show()
