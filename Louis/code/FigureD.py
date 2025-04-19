from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0.1, 0.1, 0.4, 0.8])
ax2 = fig.add_axes([0.54, 0.1, 0.4, 0.8], sharey=ax)

all_data = pd.concat([p.data for p in profiles], ignore_index=True)
all_data = all_data[all_data["depth"] > 300]
all_data = all_data[all_data["bbp_minimum_spikes"].notna()]
noise_threshold = all_data["bbp_minimum_spikes"].quantile(0.9)
print(noise_threshold)


p = profiles[530]
data = p.data

bbp = p.apply_binning_to_parameter("bbp", 1, 1000)
bins = np.arange(0, 1000)
#ax.plot(bins, bbp, color="gray")
data = data.dropna(subset="bbp")
ax.plot(data["bbp"], -data["depth"], color="gray")
ax.plot(data["bbp_minimum_despiked"].fillna(0), -data["depth"], color="black")

ax2.plot(data["bbp_minimum_spikes"].fillna(0), -data["depth"], color="gray")
ax2.vlines(noise_threshold, 0, -500, color="black", linestyles="dashed")


ax2.tick_params(axis='y', labelleft=False)
#ax.set_xlim(-0.001)
ax.set_ylim(-500, 0)
ax.set_yticklabels([f"{int(abs(label))}" for label in ax.get_yticks()])
ax.set_ylabel("Depth (m)")
ax.set_xlabel(r"b$_{bp}$ (m$^{-1}$)")
ax2.set_xlabel(r"b$_{bp}$ (m$^{-1}$)")

ax.grid(alpha=0.5)
ax2.grid(alpha=0.5)
#fig.tight_layout()
plt.savefig("Louis/figures/figureD.png", dpi=300)
