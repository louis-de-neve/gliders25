import matplotlib.pyplot as plt
from setup import import_split_and_make_transects
import numpy as np
from bbp_correction_and_despiking import scatter_and_chlorophyll_preprocessing

def regression():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all", pre_processing_function=scatter_and_chlorophyll_preprocessing, despiking_method="minimum", quench_method="night")
    c, cc = [], []
    for profile in transects[0].get_profiles():
        c += list(np.asarray(profile.data["chlorophyll"]))
        cc += list(np.asarray(profile.data["chlorophyll_corrected"]))

    c = np.asarray(c).flatten()
    cc = np.asarray(cc).flatten()

    plt.scatter(c, cc, c="blue", alpha=0.05, marker="x")
    plt.show()


def run():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all", pre_processing_function=scatter_and_chlorophyll_preprocessing, despiking_method="minimum", quench_method="mean")
    for p in all_valid_profiles:
        plt.plot(p.data["depth"], p.data["chlorophyll"])
        plt.plot(p.data["depth"], p.data["chlorophyll_corrected"])
        plt.title(str(p.qf))
        plt.vlines(p.CtoB_ML_max_depth, 0, 10, colors="red")
        plt.vlines(p.mld, 0, 10, colors="green")
        plt.xlim(0, 130)
        plt.show()


if __name__ == "__main__":
    regression()