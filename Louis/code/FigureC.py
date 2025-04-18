from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

night_profiles = []
day_profiles = []
for p in profiles:
    if not p.night:
        day_profiles.append(p.data)
    else:
        night_profiles.append(p.data)


day_df = pd.concat(day_profiles, ignore_index=True)
night_df = pd.concat(night_profiles, ignore_index=True)


day_df["depth"] = day_df["depth"].round(0)
day_df = day_df[day_df["depth"] < 1000]
day_df = day_df[day_df["depth"] > 1]
night_df["depth"] = night_df["depth"].round(0)
night_df = night_df[night_df["depth"] < 1000]
night_df = night_df[night_df["depth"] > 1]


day_df["chlorophyll_corrected"] = day_df["chlorophyll_corrected"].fillna(0)
night_df["chlorophyll"] = night_df["chlorophyll"].fillna(0)
day_df["chlorophyll"] = day_df["chlorophyll"].fillna(0)


day_mean_values = day_df.groupby("depth")["chlorophyll"].mean().values
night_mean_values = night_df.groupby("depth")["chlorophyll"].mean().values
day_corrected_mean_values = day_df.groupby("depth")["chlorophyll_corrected"].mean().values
depths = day_df.groupby("depth")["depth"].mean().values

slope, intercept, r1_value, p_value, std_err = linregress(night_mean_values, day_mean_values)
slope, intercept, r2_value, p_value, std_err = linregress(day_corrected_mean_values, night_mean_values)
print(r1_value, r2_value)


sns.lineplot(data=night_df,
             ax=ax,
             x="depth",
             y="chlorophyll",
             color="#000000FF",
             label="Night",)

sns.lineplot(data=day_df,
             ax=ax,
             x="depth",
             y="chlorophyll",
             color="#920808FF",
             label=rf"Day, Uncorrected: R$^2$ = {r1_value**2:.5f}",)

sns.lineplot(data=day_df,
             ax=ax,
             x="depth",
             y="chlorophyll_corrected",
             color="#045613FF",
             label=rf"Day, Corrected: R$^2$ = {r2_value**2:.5f}",)


ax.set_xlim(0, 125)

ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")
ax.legend()
#fig.tight_layout()
plt.savefig("Louis/figures/figureC.png", dpi=300)
