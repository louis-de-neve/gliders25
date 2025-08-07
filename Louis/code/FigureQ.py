from setup import import_split_and_make_transects, Profile, Transect, concatenate_profiles
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from plotting_functions import new_binned_plot
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)
from scipy.optimize import curve_fit
from scipy.stats.distributions import t as t_dist
from functools import partial
from matplotlib.legend_handler import HandlerTuple

fig,  axs = plt.subplots(ncols=2, figsize=(7, 5), sharey=True)

profiles.pop(612)
profiles.pop(612)
profiles.pop(576)
profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)


profiles = [p for p in profiles if p.index != 614]
profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]
interior1 = [p for p in profiles if p.index >= 495 and p.index < 546]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior1 = [p for p in profiles if p.index >= 546 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
exterior = exterior1 + exterior2
interior = interior1 + interior2
ref = [p for p in profiles if p.index >= 710 and p.index < 760]

interior_profile = concatenate_profiles(interior, giveProfile=True)
exterior_profile = concatenate_profiles(exterior, giveProfile=True)
ref_profile = concatenate_profiles(ref, giveProfile=True)

interior_data = interior_profile.data
exterior_data = exterior_profile.data
ref_data = ref_profile.data

def two_day_sections(data):
    data = data.sort_values('DateTime')
    start_time = data["DateTime"].min()
    end_time = data["DateTime"].max()
    two_day_sections = []
    current_start = start_time
    while current_start < end_time:
        current_end = current_start + pd.Timedelta(days=2)
        section = data[(data['DateTime'] >= current_start) & (data['DateTime'] < current_end)]
        if len(section) > 0:
            two_day_sections.append(section)
        current_start = current_end
    return two_day_sections

int_2_day_sections = two_day_sections(interior_data)
ext_2_day_sections = two_day_sections(exterior_data)
ref_2_day_sections = two_day_sections(ref_data)

# #print(len(int_2_day_sections), len(ext_2_day_sections), len(ref_2_day_sections))
# for section in int_2_day_sections:
#     print("Interior section length:", len(section), "Start time:", section['DateTime'].min(), "End time:", section['DateTime'].max())

binsize = 50
start, stop = 100, 1000
depths = np.arange(0, 1000, binsize)
curve_depths = np.arange(start, stop, 1)

useable_depths = np.arange(start, stop, binsize)


degrees_of_freedom = len(useable_depths) - 2
tval = t_dist.ppf(0.95/2., degrees_of_freedom) 


def martin_curve(z, b, z0):
    f_z = z0 * (z/100)**(-b)
    return f_z



h = []
for sections, name, ax in zip([int_2_day_sections, ext_2_day_sections], ["Interior", "Exterior"], axs):
    bs, cis = [], []
    for section in sections:
        section = Profile(section)
        binned_data = section.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=binsize, max_depth=1000, includeZero=True)
        useable_data = binned_data[int(start/binsize):int(stop/binsize)]
        useable_data = [d if not np.isnan(d) else 0 for d in useable_data]
        z0 = binned_data[int(100/binsize)]
        popt, pcov = curve_fit(partial(martin_curve, z0=z0), useable_depths, useable_data)
        b = popt[0]
        sigma = np.diag(pcov)[0]**0.5
        ci = sigma * tval
        scatter_marker = ax.scatter(depths, binned_data, marker="x", color="black", linewidth=1)
        bs.append(b)
        cis.append(ci)

    b_mean = np.nanmean(bs)
    b_std = np.nanstd(bs)
    ci_max = np.max(cis)
    print(f"{name} b: {b_mean:.4f} $\pm$ {ci_max:.4f}")
    line_marker = ax.plot(curve_depths, martin_curve(curve_depths, b_mean, z0),
                          color="black", linewidth=2, label=f"{name} b={b_mean:.3f} $\pm$ {b_std:.3f}")
    if name == "Interior":
        ax.plot(np.arange(35, 1000, 1), martin_curve(np.arange(35, 1000, 1), b_mean, z0), color="black", linewidth=0.5,)
    else:
        ax.plot(np.arange(15, 1000, 1), martin_curve(np.arange(15, 1000, 1), b_mean, z0), color="black", linewidth=0.5,)
    
    h.append(scatter_marker)
    h.append(line_marker)


for ax in axs:
    ax.set_xlabel("Depth (m)")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.5, which='both')
    ax.set_xlim(-20, 820)

ax, ax2 = axs
for axes, label in zip([ax, ax2], ['a', 'b', 'c', 'd']):
    axes.text(0.96, 0.92, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='right', color="#000000")

ax.set_ylabel(r"Spike $b_{bp}$ ($10^{-4}$ m$^{-1}$)")
ax.set_yticks(np.arange(0, 0.0007, 0.0001), np.arange(0, 7, 1))
fig.tight_layout()
plt.savefig("Louis/figures/figureQ.png", dpi=300)
