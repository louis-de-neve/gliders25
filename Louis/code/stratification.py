from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(6, 4.5))
ax = fig.add_axes([0.11, 0.1, 0.87, 0.88])


profiles.pop(576)
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

interior_df = pd.concat([p.data for p in interior1], ignore_index=True)
exterior_df = pd.concat([p.data for p in exterior], ignore_index=True)
ref_df = pd.concat([p.data for p in ref], ignore_index=True)


interior_df["depth"] = interior_df["depth"].round(0)
exterior_df["depth"] = exterior_df["depth"].round(0)
ref_df["depth"] = ref_df["depth"].round(0)
interior_df = interior_df[interior_df["depth"] < 1000]
exterior_df = exterior_df[exterior_df["depth"] < 1000]
ref_df = ref_df[ref_df["depth"] < 1000]
interior_df = interior_df[interior_df["depth"] > 1]
exterior_df = exterior_df[exterior_df["depth"] > 1]
ref_df = ref_df[ref_df["depth"] > 1]

interior_df = interior_df.dropna(subset=["density_anomaly"])
exterior_df = exterior_df.dropna(subset=["density_anomaly"])
ref_df = ref_df.dropna(subset=["density_anomaly"])

interior_mean_values = interior_df.groupby("depth")["density_anomaly"].mean().values
exterior_mean_values = exterior_df.groupby("depth")["density_anomaly"].mean().values
ref_mean_values = ref_df.groupby("depth")["density_anomaly"].mean().values


depths = interior_df.groupby("depth")["depth"].mean().values



sns.lineplot(data=interior_df,
             ax=ax,
             x="depth",
             y="density_anomaly",
             color="#DC2B2BFF",
             label="Interior",
             errorbar="sd")

sns.lineplot(data=exterior_df,
             ax=ax,
             x="depth",
             y="density_anomaly",
             color="#1C35D7FF",
             label=rf"Exterior",
             errorbar="sd")

sns.lineplot(data=ref_df,
             ax=ax,
             x="depth",
             y="density_anomaly",
             color="#045613FF",
             label=rf"Reference",
             errorbar="sd")


ax.set_xlim(30, 120)

ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"Density Anomaly, $\Delta \rho$ (kg m$^{-3}$)")
ax.legend()
ax.grid(alpha=0.5)

#fig.tight_layout()
plt.savefig("Louis/figures/Strat.png", dpi=300)
