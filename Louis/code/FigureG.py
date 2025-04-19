from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0.12, 0.1, 0.8, 0.8])

profiles.pop(243)
profiles = profiles[544:598]
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

old_avg_100 = np.mean(old_diff[:100])
new_avg_100 = np.mean(new_diff[:100])



ax.plot(old_diff, label="Raw Difference\nmean = {:.2e}\ntop 100 mean: {:.2e}".format(old_avg, old_avg_100), color="#7A0606FF")
ax.plot(new_diff, label='Debubbled Difference\nmean = {:.2e}\ntop 100 mean: {:.2e}'.format(new_avg, new_avg_100), color="#176304FF")
ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"|$\Delta b_{bp}$| ($m^{-1}$)")
ax.legend()

ax.set_xlim(0, 1000)
ax.grid(alpha=0.5)

#fig.tight_layout()
plt.savefig("Louis/figures/figureG.png", dpi=300)
