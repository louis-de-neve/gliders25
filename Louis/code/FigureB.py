from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


fig = plt.figure(figsize=(6, 6))
ax = fig.add_axes([0.12, 0.1, 0.85, 0.87])


#a, b, c = 530, 563, 750
a, b, c = 591, 563, 754

profiles_to_plot = []

profiles_to_plot.append((profiles[a], "Interior", "#FF0000FF"))
profiles_to_plot.append((profiles[b], "Edge", "#3A9CF1FF"))
profiles_to_plot.append((profiles[c], "Reference", "#3FD057FF"))

# Create a quantized colormap with 30 colors
# cmap = mpl.cm.get_cmap('hsv', 30)
# colors = [mpl.colors.rgb2hex(cmap(i)) for i in range(cmap.N)]
# profiles_to_plot = []
# for i, p in enumerate(profiles[549:580]):
#     profiles_to_plot.append((p, f"Profile {i}", colors[i % 30]))



for profile, label, color in profiles_to_plot:
    df = profile.data
    df["depth"] = df["depth"].round(0)
    d = df.groupby("depth")["density_anomaly"].mean()

    ax.plot(d.values,
            -d.index,
            label=label,
            color=color,
            linewidth=2)
ax.vlines(0.03, -1000, 1000, color="red", linestyles="dashed", label=r"$\Delta \rho$ = 0.03")


ax.set_ylim(-120, 0)
ax.set_xlim(-0.01, 0.45)
ax.set_ylabel("Depth (m)")
ax.set_xlabel(r"Density Anomaly, $\Delta \rho$ (kg m$^{-3}$)")
ax.legend(loc="upper right")
ax.grid(alpha=0.5)


#fig.tight_layout()
plt.savefig("Louis/figures/figureB.png", dpi=300)
