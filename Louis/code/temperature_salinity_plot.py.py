import matplotlib.pyplot as plt
import matplotlib as mpl
from setup import import_split_and_make_transects
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing
import seaborn as sns

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

def temp_salinity_plot(profiles:list, ax:plt.axes, c) :
    for profile in profiles:
        pcm = ax.scatter(profile.data["salinity_final"], profile.data["temperature_final"],
                   c="#00000000", marker="o", edgecolor=c, linewidth=0.5, s=3)
    return pcm  


#profiles.pop(576)
profiles = [p for p in profiles if p.index != 614]

profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 546]#550
exterior1 = [p for p in profiles if p.index >= 548 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 574]#580
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]

#profiles 547 and 548 and 574-579 are excluded as they do not fit either water mass
p1 = [p for p in profiles if p.index == 547][0]
print(p1.start_time, p1.end_time)



exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]


fig = plt.figure(figsize=(4, 4))
ax1 = fig.add_axes([0.2, 0.15, 0.75, 0.75])



colors = sns.palettes.color_palette("Set1")[:2]


p1 = temp_salinity_plot(interior, ax1, colors[0])
p2 = temp_salinity_plot(exterior, ax1, colors[1])

xlims, ylims = ax1.get_xlim(), ax1.get_ylim()

ax1.scatter([0], [0], c="#00000000", marker="o", edgecolor=colors[0], linewidth=1, s=20, label="Interior")
ax1.scatter([0], [0], c="#00000000", marker="o", edgecolor=colors[1], linewidth=1, s=20, label="Edge")

ax1.set_xlim(xlims)
ax1.set_ylim(ylims)

ax1.legend()


ax1.set_xlabel("Salinity / g/kg")
ax1.set_ylabel("Temperature / °C")



plt.savefig("Louis/figures/TS_all_transects.png", dpi=300)