from setup import import_split_and_make_transects, Profile, Transect, concatenate_profiles
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from plotting_functions import new_binned_plot
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

fig = plt.figure(figsize=(5, 3.5))
ax = fig.add_axes([0.14, 0.08, 0.8, 0.83])
#ax2 = fig.add_axes([0.49, 0.14, 0.25, 0.83], sharey=ax)
#ax3 = fig.add_axes([0.79, 0.14, 0.25, 0.83], sharey=ax)
ax4 = ax.twiny()
profiles.pop(612)
profiles.pop(612)

profiles.pop(576)
profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)

# for p in profiles:
#     p.data = p.data[p.data["bbp_debubbled_spikes_denoised"] > 0]

profiles1 = profiles[494:562]
profiles2 = profiles[562:629]

interior = profiles1[:-20] + profiles2[15:]
exterior = profiles1[-20:] + profiles2[:15]
total = profiles1 + profiles2
# d=interior[50].data
# ax.scatter(d["depth"], d["bbp_debubbled_spikes_denoised"], linewidth=1, color="black", label="Transect 1")
# plt.show()



def stacking_method(profiles1, ax, ax2, color):
    t1 = pd.concat([p.data for p in profiles1])
    t1.sort_values(by="depth", inplace=True)
    t1["date"] = t1["DateTime"].dt.date
    profiles_day_binned = [Profile(t1[t1["date"] == d], d) for d in sorted(t1["date"].unique())]
    
    print(profiles_day_binned)

    for day in profiles1:

        day_binnedlist, freqs = day.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=50, max_depth=1000, returnFreq=True, includeZero=True)
        day_binned = pd.DataFrame()
        day_binned["bbp_debubbled_spikes_denoised"] = day_binnedlist
        day_binned["Depth"] = np.arange(0, 1000, 50)
        day_binned["freq"] = freqs
        day_binned = day_binned[day_binned["freq"] > 100]
        ax.plot(day_binned["bbp_debubbled_spikes_denoised"], -day_binned["Depth"])
        ax2.plot(list(freqs), -np.arange(0, 1000, 50))

    depth_bins = np.arange(0, 1000, 1)

    #ax.plot(t1_binned, -depth_bins, color=color, linewidth=1, label="Binned Transect 1")
    #ax2.plot(t1_series, -depth_bins, color=color, linewidth=1, label="Binned Transect 1")

# stacking_method(interior, ax, ax2, "black")
# stacking_method(exterior, ax, ax2, "red")

interior_profile = concatenate_profiles(interior, giveProfile=True)
exterior_profile = concatenate_profiles(exterior, giveProfile=True)

ip = interior_profile.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=10, max_depth=1000, includeZero=True)
ep = exterior_profile.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=10, max_depth=1000, includeZero=True)

ratio = np.asarray(ip)/np.asarray(ep)
mean_ratio = np.nanmean(ratio)
ip = pd.Series(ip).rolling(window=1, min_periods=1).mean()
ep = pd.Series(ep).rolling(window=1, min_periods=1).mean()
ratio = pd.Series(ratio).rolling(window=10, min_periods=1).mean()


ax4.plot(ratio, -np.arange(0, 1000, 10), color="blue", alpha=0.8, linewidth=1, label=f"Rolling mean ratio\nof interior to exterior \nmean: {mean_ratio:.2f}")
ax.plot(ip, -np.arange(0, 1000, 10), color="black", linewidth=1, label="Interior of Taylor Column spike bbp")
ax.plot(ep, -np.arange(0, 1000, 10), color="red", linewidth=1, label="Edge of Taylor Column spike bbp")


my_cmap = mpl.colormaps["inferno"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.003, clip=True)
#new_binned_plot(total, ax2, "bbp_debubbled_spikes_denoised", bin_size=10, max_depth=1000, cmap=my_cmap, norm=my_norm)

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)

#new_binned_plot(total, ax3, "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)
ax4.set_xlabel(r"Ratio")
ax.set_xlabel(r"Depth Gridded $b_{bp}$ / m$^{-1}$")
ax.legend(loc="lower center")
ax4.legend(loc="upper center")
plt.show()

# pcm = new_binned_plot(profiles1, ax, "bbp_debubbled_spikes_denoised", bin_size=1, cmap="viridis", norm=None)
# pcm = new_binned_plot(profiles2, ax2, "bbp_debubbled_spikes_denoised", bin_size=1, cmap="viridis", norm=None)

# ax2.invert_xaxis()
# plt.show()

# def average_method(profiles1, profiles2, ax, ax2):

#     for axes, profiles in ((ax, profiles1), (ax2, profiles2)):
#         binned_data = []
#         for p in profiles:
#             binned_spikes = p.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=1, max_depth=1000)  
#             binned_spikes = pd.Series(binned_spikes).rolling(window=10, min_periods=1).mean()
#             binned = pd.DataFrame()
#             binned["data"] = binned_spikes
#             binned["depth"] = np.arange(0, 1000, 1)
#             binned_data.append(binned)
#             #axes.plot(binned_spikes, -np.arange(0, 1000, 1), linewidth=1, alpha=0.1, color="black")
#         stacked = pd.concat(binned_data, ignore_index=True)
#         sns.lineplot(data=stacked, y="data", x="depth", ax=ax, linewidth=1)


#     for axes, profiles in ((ax, profiles1), (ax2, profiles2)):
#         binned_data = []
#         for p in profiles:
#             binned_spikes = p.apply_binning_to_parameter("bbp_debubbled", bin_size=1, max_depth=1000)  
#             binned_spikes = pd.Series(binned_spikes).rolling(window=10, min_periods=1).mean()
#             binned = pd.DataFrame()
#             binned["data"] = binned_spikes
#             binned["depth"] = np.arange(0, 1000, 1)
#             binned_data.append(binned)
#             #axes.plot(binned_spikes, -np.arange(0, 1000, 1), linewidth=1, alpha=0.1, color="black")
#         stacked = pd.concat(binned_data, ignore_index=True)
#         sns.lineplot(data=stacked, y="data", x="depth", ax=ax2, linewidth=1)
#     plt.show()