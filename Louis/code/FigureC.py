from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


from preprocessing.chlorophyll.default_quenching import default_quenching_correction
profiles = default_quenching_correction(profiles)


#profiles = profiles[90:]

fig = plt.figure(figsize=(6, 4.5))
ax = fig.add_axes([0.11, 0.1, 0.87, 0.88])


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


#day_df["chlorophyll_corrected"] = day_df["chlorophyll_corrected"].fillna(0)
#night_df["chlorophyll"] = night_df["chlorophyll"].fillna(0)
#day_df["chlorophyll"] = day_df["chlorophyll"].fillna(0)

night_df = night_df.dropna(subset=["chlorophyll"])
day_df = day_df.dropna(subset=["chlorophyll"])
day_df_c = day_df.dropna(subset=["chlorophyll_corrected"])



day_mean_values = day_df.groupby("depth")["chlorophyll"].mean().values
night_mean_values = night_df.groupby("depth")["chlorophyll"].mean().values
day_corrected_mean_values = day_df_c.groupby("depth")["chlorophyll_corrected"].mean().values
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
             label=rf"Day, Uncorrected",)

sns.lineplot(data=day_df_c,
             ax=ax,
             x="depth",
             y="chlorophyll_corrected",
             color="#045613FF",
             label=rf"Day, Corrected",)


ax.set_xlim(0, 80)
ax.set_ylim(0.8, 2.7)
ax.set_yticks([1, 1.5, 2, 2.5])

ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")
ax.legend()
ax.grid(alpha=0.5)

#fig.tight_layout()
plt.savefig("Louis/figures/figureC.png", dpi=300)
