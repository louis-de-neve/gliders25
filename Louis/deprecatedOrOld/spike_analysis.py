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
#print(profiles[0].data.columns)

fig,  ax = plt.subplots(figsize=(6, 5))
#ax = fig.add_axes([0.14, 0.08, 0.8, 0.83])
#ax2 = fig.add_axes([0.49, 0.14, 0.25, 0.83], sharey=ax)
#ax3 = fig.add_axes([0.79, 0.14, 0.25, 0.83], sharey=ax)
#ax4 = ax.twinx()
profiles.pop(612)
profiles.pop(612)

profiles.pop(576)
profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
profiles[540].start_time = profiles[539].start_time
profiles.pop(539)
profiles.pop(538)

# for p in profiles:
#     p.data = p.data[p.data["bbp_debubbled_spikes_denoised"] > 0]

profiles = [p for p in profiles if p.index != 614]

profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 550]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior1 = [p for p in profiles if p.index >= 550 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]
# d=interior[50].data
# ax.scatter(d["depth"], d["bbp_debubbled_spikes_denoised"], linewidth=1, color="black", label="Transect 1")
# plt.show()



# def stacking_method(profiles1, ax, ax2, color):
#     t1 = pd.concat([p.data for p in profiles1])
#     t1.sort_values(by="depth", inplace=True)
#     t1["date"] = t1["DateTime"].dt.date
#     profiles_day_binned = [Profile(t1[t1["date"] == d], d) for d in sorted(t1["date"].unique())]
    
#     print(profiles_day_binned)

#     for day in profiles1:

#         day_binnedlist, freqs = day.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=50, max_depth=1000, returnFreq=True, includeZero=True)
#         day_binned = pd.DataFrame()
#         day_binned["bbp_debubbled_spikes_denoised"] = day_binnedlist
#         day_binned["Depth"] = np.arange(0, 1000, 50)
#         day_binned["freq"] = freqs
#         day_binned = day_binned[day_binned["freq"] > 100]
#         ax.plot(day_binned["bbp_debubbled_spikes_denoised"], -day_binned["Depth"])
#         ax2.plot(list(freqs), -np.arange(0, 1000, 50))

#     depth_bins = np.arange(0, 1000, 1)

#     #ax.plot(t1_binned, -depth_bins, color=color, linewidth=1, label="Binned Transect 1")
#     #ax2.plot(t1_series, -depth_bins, color=color, linewidth=1, label="Binned Transect 1")

# stacking_method(interior, ax, ax2, "black")
# stacking_method(exterior, ax, ax2, "red")




interior_profile:Profile = concatenate_profiles(interior, giveProfile=True)
exterior_profile = concatenate_profiles(exterior, giveProfile=True)
ref_profile = concatenate_profiles(ref, giveProfile=True)


i = interior_profile.data
e = exterior_profile.data

i = i[i["depth"] >= 200]
i = i[i["depth"] <= 250]


e = e[e["depth"] >= 200]
e = e[e["depth"] <= 250]



binsize = 50
d = np.arange(0, 1000, binsize)

ip = interior_profile.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=binsize, max_depth=1000, includeZero=True,)
ep = exterior_profile.apply_binning_to_parameter("bbp_debubbled_spikes_denoised", bin_size=binsize, max_depth=1000, includeZero=True,)
re = ref_profile.apply_binning_to_parameter("bbp_minimum_spikes_denoised", bin_size=binsize, max_depth=1000, includeZero=True)


print(ip[4], ep[4])

ratio = np.asarray(ip)/np.asarray(ep)
mean_ratio = np.nanmean(ratio)
ip = pd.Series(ip).rolling(window=1, min_periods=1).mean()
ep = pd.Series(ep).rolling(window=1, min_periods=1).mean()
re = pd.Series(re).rolling(window=1, min_periods=1).mean()


ratio = pd.Series(ratio)#.rolling(window=10, min_periods=1).mean()

boundary = int(100/binsize)
lower_boundary = int(700/binsize)
ip_useable = ip[boundary:lower_boundary]
ep_useable = ep[boundary:lower_boundary]
re_useable = re[boundary:lower_boundary]
d_useable = np.arange(0, 1000, binsize)[boundary:lower_boundary]

def martin_curve(z, a, b):
    f_z = a * (z/100)**(-b)
    return f_z

popt_ip, pcov_ip = curve_fit(martin_curve, d_useable, ip_useable,)# bounds=([0, 0], [0.001, 2]))
popt_ep, pcov_ep = curve_fit(martin_curve, d_useable, ep_useable,)# bounds=([0, 0], [0.001, 2]))
popt_re, pcov_re = curve_fit(martin_curve, d_useable, re_useable,)# bounds=([0, 0], [0.001, 2]))

degrees_of_freedom = len(ep_useable) - 2
tval = t_dist.ppf(0.95/2., degrees_of_freedom) 

sigma_ip = np.diag(pcov_ip)[1]**0.5
b_ip = popt_ip[1]
print(f"Interior b: {b_ip:.4f} [{b_ip - sigma_ip*tval:.4f}  {b_ip + sigma_ip*tval:.4f}]")
sigma_ep = np.diag(pcov_ep)[1]**0.5
b_ep = popt_ep[1]
print(f"Exterior b: {b_ep:.4f} [{b_ep - sigma_ep*tval:.4f}  {b_ep + sigma_ep*tval:.4f}]")
sigma_ep = np.diag(pcov_re)[1]**0.5
b_re = popt_re[1]
print(f"Reference b: {b_re:.4f} [{b_re - sigma_ep*tval:.4f}  {b_re + sigma_ep*tval:.4f}]")



first_part = np.arange(45, 100, 1)
second_part = np.arange(100, 700, 1)

ip_fit = martin_curve(second_part, *popt_ip)
ep_fit = martin_curve(second_part, *popt_ep)
re_fit = martin_curve(second_part, *popt_re)

ax.plot(second_part, ip_fit, color="black", linewidth=1.5, label=f"Interior of Taylor Column, b={popt_ip[1]:.3f}")
ax.plot(second_part, ep_fit, color="red", linewidth=1.5, label=f"Edge of Taylor Column, b={popt_ep[1]:.3f}")
#ax.plot(second_part, re_fit, color="green", linewidth=1.5, label=f"Reference, b={popt_re[1]:.3f}")

ax.scatter(d, ip, color="black", linewidth=1, marker="x")
ax.scatter(d, ep, color="red", linewidth=1, marker="x")
#ax.scatter(d, re, color="green", linewidth=1, marker="x")


my_cmap = mpl.colormaps["inferno"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.0004, vmax=0.003, clip=True)
#new_binned_plot(total, ax2, "bbp_debubbled_spikes_denoised", bin_size=10, max_depth=1000, cmap=my_cmap, norm=my_norm)

my_cmap = mpl.colormaps["viridis"].copy()
my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)

#ax.set_xscale()
#ax.set_xticklabels([f"{int(abs(label))}" for label in ax.get_xticks()])
ax.set_xlabel("Depth (m)")
ax.set_ylim(bottom=0)
ax.grid(alpha=0.5, which='both')
#ax.set_yscale("log")
ax.set_xlim(-20, 820)
#new_binned_plot(total, ax3, "chlorophyll_corrected", 10, 1000, cmap=my_cmap, norm=my_norm)
#ax4.set_xlabel(r"Ratio")
ax.set_ylabel(r"Spike $b_{bp}$ / m$^{-1}$")
ax.legend(loc="upper right")
#ax4.legend(loc="upper center")
fig.tight_layout()
plt.savefig("Louis/figures/taylor_column_spike_bbp_bad.png", dpi=300)
#plt.show()

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