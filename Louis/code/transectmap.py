import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Profile, Transect
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing

def transect_map(transects:list[Transect], profiles:list[Profile]) -> None:
    for t in transects:
        x, y = tuple(zip(t.start_location, t.finish_location))
        plt.plot(x, y, label=t.name)
    for p in profiles:
        x, y = tuple(zip(p.start_location, p.end_location))
        plt.scatter(x, y, color="black", alpha=0.1)
        #plt.text(x[0], y[0], p.index, fontsize=5)
    plt.legend()


transects, all_valid_profiles = import_split_and_make_transects()
transect_map(transects, all_valid_profiles)
plt.savefig("Louis/outputs/transect_map.png", dpi=300)
plt.show()