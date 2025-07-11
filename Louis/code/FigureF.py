from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)
#profiles.pop(243)
profiles.pop(576)
profiles = profiles[544:598]

fig = plt.figure(figsize=(6, 8))
ax = fig.add_axes([0.17, 0.54, 0.8, 0.44])
ax2 = fig.add_axes([0.17, 0.08, 0.8, 0.44], sharex=ax)


up_profiles = [p.data for p in profiles if p.direction == "up"]
down_profiles = [p.data for p in profiles if p.direction == "down"]


up_df = pd.concat(up_profiles, ignore_index=True)
down_df = pd.concat(down_profiles, ignore_index=True)


up_df["depth"] = up_df["depth"].round(0)
up_df = up_df[up_df["depth"] <= 1000]
up_df = up_df[up_df["depth"] > 0]
down_df["depth"] = down_df["depth"].round(0)
down_df = down_df[down_df["depth"] <= 1000]
down_df = down_df[down_df["depth"] > 0]


up_df = up_df.dropna(subset="bbp_minimum_despiked")
down_df = down_df.dropna(subset="bbp_minimum_despiked")

difference = up_df["bbp_minimum_despiked"] - down_df["bbp_minimum_despiked"]


up_mean = up_df.groupby("depth")["bbp_minimum_despiked"].mean().values
down_mean = down_df.groupby("depth")["bbp_minimum_despiked"].mean().values
depths = up_df.groupby("depth")["depth"].mean().values

difference = down_mean - up_mean




sns.lineplot(data=down_df,
             ax=ax,
             x="depth",
             y="bbp_minimum_despiked",
             color="#7A0606FF",
             label="Downcasts")

sns.lineplot(data=up_df,
             ax=ax,
             x="depth",
             y="bbp_minimum_despiked",
             color="#176304FF",
             label=rf"Upcasts")

ax.plot(depths, difference, color="black", label="Difference")
ax2.plot(depths, difference, color="black", label="Difference")


ylocs = [0, 10, 20, 30, 50, 80, 120, 160, 990]
ylocs = np.append(np.arange(0, 170, 10), 990)
    
def piecewise_function(xs, *yvals):
    section = np.zeros_like(xs)
    for i, xlim in enumerate(ylocs[:-1]):
        section = section + np.asarray([yvals[i] + (yvals[i+1] - yvals[i]) * (x - xlim) / (ylocs[i+1] - xlim) if (x >= xlim) and (x < ylocs[i+1]) else 0 for x in xs])
    return section

d2 = np.maximum(difference, 0)
p0 = [d2[i] for i in ylocs]


popt, pcov = curve_fit(piecewise_function, np.arange(1000), difference, p0=p0, bounds=(0, np.inf))
bubble_correction_adjustment = piecewise_function(np.arange(1000), *popt)

ax2.plot(depths, bubble_correction_adjustment, color="red", label="Bubble correction adjustment")


for axes, label in zip([ax, ax2], ['a', 'b']):
    axes.text(0.02, 0.02, label, transform=axes.transAxes, fontsize=20, va='bottom', ha='left', color="#000000")

ax.set_xlim(0, 200)

ax.set_ylabel(r"b$_{bp}$ (m$^{-1}$)")
ax2.set_ylabel(r"b$_{bp}$ (m$^{-1}$)")
ax.set_xlabel("")
ax2.set_xlabel("Depth (m)")
ax.legend()
ax2.legend()
ax.grid(alpha=0.5)
ax2.grid(alpha=0.5)
ax.tick_params(axis='x', labelbottom=False)







#fig.tight_layout()
plt.savefig("Louis/figures/figureF.png", dpi=300)
