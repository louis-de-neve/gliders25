import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np


widths = [6, 8, 10, 12, 14, 16]
dictionary = {w: [] for w in widths}
dictionary100 = {w: [] for w in widths}

times = [1/2.76, 1/1.74, 1.04, 1.13, 1.73, 2.21]

for n in [100, 200, 280, 350, 420, 490, 520, 560, 630, 700, 770]:#, 520]:
    if os.path.exists(f"Louis/cache/analysis{n}.pkl"):
        with open(f"Louis/cache/analysis{n}.pkl", "rb") as f:
            data = pd.read_pickle(f)
        result_dict = data["dict"]
        result_dict_top_100 = data["dict100"]

        for k, v in result_dict.items():
            dictionary[k].extend(v)
        for k, v in result_dict_top_100.items():
            dictionary100[k].extend(v)

    


fig, ax = plt.subplots(figsize=(5, 5))
ax2 = plt.twinx(ax)

line = ax2.scatter(widths, times, color='b', marker='x', s=60, zorder=1, label="Computational Efficiency")
ax2.set_ylabel(r'Iterations per second (s$-1$)')
# Fit a quadratic curve to the times data


print(len(dictionary[14]))

bplot1 = ax.boxplot([dictionary[w] for w in widths],
           positions=np.asarray(widths)-0.25,
           manage_ticks=False,
           patch_artist=True,
           medianprops={"color":'black'},
           showfliers=False,
           label="Whole profile")
bplot2 = ax.boxplot([dictionary100[w] for w in widths],
           positions=np.asarray(widths)+0.25,
           manage_ticks=False,
           patch_artist=True,
           medianprops={"color":'black'},
           showfliers=False,
           label='Top 100m',)

for patch in bplot1['boxes']:
    patch.set_facecolor("#8ffaa1")

for patch in bplot2['boxes']:
    patch.set_facecolor("#ff8f8f")


# for w in widths:
#     ax.scatter(np.full_like(dictionary[w], w), dictionary[w],
#                marker="x",
#                color='black',
#                alpha=0.5,)
#     ax.scatter(np.full_like(dictionary100[w], w), dictionary100[w],
#                marker="x",
#                color='red',
#                alpha=0.5,)
#ax.boxplot([dictionary100[w] for w in widths], positions=widths, boxprops={"color":'r'})



ax.set_ylim(top=17)
#ax.set_xlim(5, 15)
ax.set_ylabel('Improvement factor')
ax.set_xlabel('Bubble correction segment width (m)')
ax.legend(handles=[bplot1["boxes"][0], bplot2["boxes"][0], line],
           labels=["Full profile", "Top 100m", "Computational Speed"],
           loc="upper left",)

# ax.grid(axis="y", alpha=0.5)
fig.tight_layout()
plt.savefig("Louis/figures/figureO.png", dpi=300)
#plt.show()