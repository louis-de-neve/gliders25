import matplotlib.pyplot as plt
import matplotlib as mpl
from setup import import_split_and_make_transects
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing
import seaborn as sns
from gsw.density import sigma0, sigma1, rho_t_exact
from gsw.conversions import SP_from_SA
import numpy as np
from preprocessing.depth_calculations.mld import MLD_calculation

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

def temp_salinity_plot(profiles:list, ax:plt.axes, c) :
    profiles = MLD_calculation(profiles)
    for profile in profiles:
        pd = profile.data
        #print(pd["SA"].iloc[0], pd["CT"].iloc[0], sigma0(pd["SA"].iloc[0], pd["CT"].iloc[0]))
        pcm = ax.scatter(pd["SA"], pd["CT"],
                   c="#00000000", marker="o", edgecolor=c, linewidth=0.5, s=3, zorder=2)
    return pcm  


profiles.pop(576)
profiles = [p for p in profiles if p.index != 614]

profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 546]#550
b1 = [p for p in profiles if p.index >= 547 and p.index < 549]
exterior1 = [p for p in profiles if p.index >= 549 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 574]#580
b2 = [p for p in profiles if p.index >= 574 and p.index < 580]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]

#profiles 547 and 548 and 574-579 are excluded as they do not fit either water mass
p1 = [p for p in profiles if p.index == 547][0]
print(p1.start_time, p1.end_time)


boundary = b1 + b2
exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]


fig = plt.figure(figsize=(8, 4))
ax1 = fig.add_axes([0.1, 0.13, 0.4, 0.85])
ax2 = fig.add_axes([0.57, 0.13, 0.4, 0.85], sharey=ax1)


colors = ["#ED7779", "#6CA9DB", "#A8D18D"]





print(rho_t_exact(34.6, 1, 0))
print(sigma0(34.6, 1))

p3 = temp_salinity_plot(ref, ax1, colors[2])
p1 = temp_salinity_plot(interior, ax1, colors[0])

p3 = temp_salinity_plot(ref, ax2, colors[2])
p2 = temp_salinity_plot(exterior, ax2, colors[1])

def mesh(ax):
    xlims, ylims = ax.get_xlim(), ax.get_ylim()
    xs = np.linspace(xlims[0]-1, xlims[1]+1, 1000)
    xs = SP_from_SA(xs, 0, -36.5, -61)
    X, Y = np.meshgrid(xs, np.linspace(ylims[0], ylims[1], 1000))


    sigma = sigma0(X, Y) + 1000
    CS = ax.contour(X, Y, sigma, colors="black", linewidths=0.5, levels=(1027.15, 1027.3, 1027.45, 1027.6, 1027.75, 1027.9))
    ax.clabel(CS, fontsize=6)

    ax.scatter([0], [0], c="#00000000", marker="o", edgecolor=colors[0], linewidth=1.5, s=20, label="Interior")
    ax.scatter([0], [0], c="#00000000", marker="o", edgecolor=colors[1], linewidth=1.5, s=20, label="Edge")
    ax.scatter([0], [0], c="#00000000", marker="o", edgecolor=colors[2], linewidth=1.5, s=20, label="Reference")

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

mesh(ax1)
mesh(ax2)




ax1.legend(loc="lower left")


ax1.set_xlabel(r"Salinity / g kg$^{-1}$")
ax2.set_xlabel(r"Salinity / g kg$^{-1}$")
ax1.set_ylabel(r"Temperature / °C")



plt.savefig("Louis/figures/figureR2.png", dpi=300)