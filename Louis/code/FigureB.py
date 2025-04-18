from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(8, 8))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])


df = pd.concat([p.data for p in profiles])
df = profiles[300].data
df["depth"] = df["depth"].round(0)
d = df.groupby("depth")["density_anomaly"].mean()

ax.plot(d,
         label="Density",
         color="#000000FF",
         linewidth="2")
ax.hlines(0.03, 0, 1000, color="red", linestyles="dashed", label=r"$\Delta \rho$ = 0.03")


ax.set_xlim(0, 100)
ax.set_ylim(ax.get_ylim()[0], 0.5)
ax.set_xlabel("Depth (m)")
ax.set_ylabel(r"Density Anomaly, $\Delta \rho$ (kg m$^{-3}$)")
ax.legend(loc="upper left")
#fig.tight_layout()
plt.savefig("Louis/figures/figureB.png", dpi=300)
