from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.1, 0.1, 0.89, 0.88])
ax2 = fig.add_axes([0.49, 0.38, 0.5, 0.6])

df = pd.concat([p.data for p in transects[5].get_profiles()])

df = profiles[406].data
tempdf = df[df["depth"] > 300]
c_95 = tempdf["original_chlorophyll"].quantile(0.05)


df["depth"] = df["depth"].round(0)
c = df.groupby("depth")["chlorophyll"].mean()
c_old = df.groupby("depth")["original_chlorophyll"].mean()



ax.plot(c_old,
         label="Original Chlorophyll",
         color="#095503FF",
         linewidth="1")

ax.plot(c,
         label="Chlorophyll",
         color="#76FA4DFF",
         linewidth="1")

ax2.plot(c_old,
         label="Original Chlorophyll",
         color="#095503FF",
         linewidth="1")

ax2.plot(c,
         label="Deep Corrected Chlorophyll",
         color="#76FA4DFF",
         linewidth="1")



ax.hlines(c_95, 0, 1000, color="red", linestyles="dashed", label="95% C.I.")
ax2.hlines(c_95, 0, 1000, color="red", linestyles="dashed", label="5th Percentile")
print(c_95)


ax.set_xlim(0, 1000)
ax2.set_xlim(0, 1000)
ax2.set_ylim(-0.005,0.12)
ax2.set_xticks(ax2.get_xticks()[:-1])
ax2.set_yticks(ax2.get_yticks()[1:-1])

ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"Chlorophyll (mg m$^{-3}$)")

ax2.legend()
ax.grid(alpha=0.5)
ax2.grid(alpha=0.5)
plt.savefig("Louis/figures/figureA.png", dpi=300)
