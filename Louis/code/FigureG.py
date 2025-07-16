from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import linregress
from preprocessing.bbp.bubble_correction import bubble_correction
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

profiles.pop(243)
n = 543
profiles = profiles[n:(n+74)]
for i, p in enumerate(profiles):
    p.index = i
    if "bbp_debubbled_despiked" in p.data.columns:
        p.data.drop(columns=["bbp_debubbled_despiked"], inplace=True)

width = 10
print(f"width: {width}")
profiles = bubble_correction(profiles, width)
profiles = profiles[10:-10]


fig = plt.figure(figsize=(6, 4))
ax = fig.add_axes([0.17, 0.13, 0.8, 0.85])


up = [p.data for p in profiles if p.direction == "up"]
down  = [p.data for p in profiles if p.direction == "down"]

up = pd.concat(up).dropna(subset=["bbp_minimum_despiked"])
down = pd.concat(down).dropna(subset=["bbp_minimum_despiked"])

up["depth"] = up["depth"].round(0)
down["depth"] = down["depth"].round(0)

up_original = up.groupby("depth")["bbp_minimum_despiked"].mean()
down_original = down.groupby("depth")["bbp_minimum_despiked"].mean()
down_new = down.groupby("depth")["bbp_debubbled_despiked"].mean()

old_diff = down_original - up_original
new_diff = down_new - up_original
old_diff.pop(0)
old_diff.pop(1) # ignore top 1m (0 and 1m)
new_diff.pop(0)
new_diff.pop(1)

new_diff = abs(new_diff)
old_diff = abs(old_diff)

old_avg = np.mean(old_diff)
new_avg = np.mean(new_diff)

top_100 = list(old_diff)[:98]
new_100 = list(new_diff)[:98]

old_avg_100 = np.mean(top_100)
new_avg_100 = np.mean(new_100)

improvement100 = old_avg_100 / new_avg_100
improvement = old_avg / new_avg
print(f"Improvement {improvement:.2f}, improvement at 100m {improvement100:.2f}")


ax.set_xscale('log')
ax.plot(old_diff, label="Uncorrected difference", color="#7A0606FF")
ax.plot(new_diff, label='Corrected difference', color="#176304FF")
ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"|$\Delta b_{bp}$| ($m^{-1}$)")
ax.legend()

ax.set_xlim(10, 1000)
ax.grid(alpha=0.5)

#fig.tight_layout()
#plt.savefig("Louis/figures/figureG.png", dpi=300)
