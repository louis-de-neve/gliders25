import matplotlib.pyplot as plt
from setup import import_split_and_make_transects, concatenate_profiles
import numpy as np
from bbp_correction_and_despiking import scatter_and_chlorophyll_preprocessing

def regression():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=scatter_and_chlorophyll_preprocessing,
                                                                    despiking_method="minimum",
                                                                    quench_method="regression")
    c, cc = [], []
    for profile in transects[0].get_profiles():
        d = profile.data
        d = d[d["depth"] < profile.mld]
        d = d[d["depth"] > 3]
        c += list(np.asarray(d["chlorophyll"]))
        cc += list(np.asarray(d["chlorophyll_corrected"]))

    c = np.asarray(c).flatten()
    cc = np.asarray(cc).flatten()

    plt.scatter(c, cc, c="blue", alpha=0.05, marker="x")
    plt.xlabel("raw C")
    plt.ylabel("corrected C")
    plt.show()


def compare():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=scatter_and_chlorophyll_preprocessing,
                                                                    despiking_method="minimum",
                                                                    quench_method="mean")
    for p in all_valid_profiles:
        plt.plot(p.data["depth"], p.data["chlorophyll"])
        plt.plot(p.data["depth"], p.data["chlorophyll_corrected"])
        plt.title(str(p.qf))
        plt.vlines(p.CtoB_ML_max_depth, 0, 10, colors="red")
        plt.vlines(p.mld, 0, 10, colors="green")
        plt.xlim(0, 130)
        plt.show()


def run():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=scatter_and_chlorophyll_preprocessing,
                                                                    despiking_method="minimum",
                                                                    quench_method="mean")
    p_of_interest = []
    for p in all_valid_profiles:
        if not p.night and p.direction == "down":
            p_of_interest.append(p)
    
    d = concatenate_profiles(p_of_interest)
    d = d[d["depth"] < 40]
    d = d[d["depth"] > 3]

    fig, axs = plt.subplots(2, 2)
    axs = axs.flatten()

    axs[0].scatter(d["chlorophyll"], d["scatter_650"], c=d["depth"], marker="x", linewidth=1)
    axs[0].set_title("down day")
    axs[0].set_xlabel("Chlorophyll")
    axs[0].set_ylabel("Scatter 650")
    axs[1].scatter(d["chlorophyll"], d["bbp_minimum_despiked"], c=d["depth"], marker="x", linewidth=1)
    axs[1].set_title("down day")
    axs[1].set_xlabel("Chlorophyll")
    axs[1].set_ylabel("bbp despiked")


    p_of_interest = []
    for p in all_valid_profiles:
        if not p.night and p.direction == "up":
            p_of_interest.append(p)
    
    d = concatenate_profiles(p_of_interest)
    d = d[d["depth"] < 40]
    d = d[d["depth"] > 3]

    axs[2].scatter(d["chlorophyll"], d["scatter_650"], c=d["depth"], marker="x", linewidth=1)
    axs[2].set_title("up day")
    axs[2].set_xlabel("Chlorophyll")
    axs[2].set_ylabel("Scatter 650")
    pcm = axs[3].scatter(d["chlorophyll"], d["bbp_minimum_despiked"], c=d["depth"], marker="x", linewidth=1)
    axs[3].set_title("up day")
    axs[3].set_xlabel("Chlorophyll")
    axs[3].set_ylabel("bbp despiked")

    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")


    plt.show()


if __name__ == "__main__":
    regression()