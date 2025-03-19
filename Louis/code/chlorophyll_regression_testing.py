import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, concatenate_profiles
import numpy as np
from plotting_functions import binned_plot
from scipy.stats import linregress
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing as new_preprocessing
from preprocessing.deprecated_bbp_correction_and_despiking import scatter_and_chlorophyll_preprocessing as old_preprocessing
from preprocessing.quenching.default import default_quenching_correction
import seaborn as sns
import pandas as pd
import pickle

parameters = ["time", "longitude", "latitude",
                "depth", "chlorophyll", "pressure",
                "temperature_final", "salinity_final",
                "temperature", "salinity", "temperature_corrected_thermal",
                "profile_index", "scatter_650"]

def regression():
    fig, axs = plt.subplots(1, 2)
    axs = axs.flatten()

    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=new_preprocessing,
                                                                    despiking_method="minimum")
    c, cc = [], []
    for profile in transects[0].get_profiles():
        d = profile.data
        d = d[d["depth"] < profile.mld]
        d = d[d["depth"] > 3]
        c += list(np.asarray(d["chlorophyll"]))
        cc += list(np.asarray(d["chlorophyll_corrected"]))

    c = np.asarray(c).flatten()
    cc = np.asarray(cc).flatten()

    axs[0].scatter(c, cc, c="blue", alpha=0.05, marker="x")
    axs[0].set_xlabel("raw C")
    mask = ~np.isnan(c) & ~np.isnan(cc)
    slope, intercept, r_value, p_value, std_err = linregress(c[mask], cc[mask])
    axs[0].set_title(f"new (R² = {r_value**2:.2f})")
    axs[0].set_ylabel("corrected C")
    del d, c, cc
    del transects, all_valid_profiles

    
    
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=old_preprocessing,
                                                                    despiking_method="minimum")
    c, cc = [], []
    for profile in transects[0].get_profiles():
        d = profile.data
        d = d[d["depth"] < profile.mld]
        d = d[d["depth"] > 3]
        c += list(np.asarray(d["chlorophyll"]))
        cc += list(np.asarray(d["chlorophyll_corrected"]))

    c = np.asarray(c).flatten()
    cc = np.asarray(cc).flatten()

    axs[1].scatter(c, cc, c="blue", alpha=0.05, marker="x")
    axs[1].set_xlabel("raw C")
    mask = ~np.isnan(c) & ~np.isnan(cc)
    slope, intercept, r_value, p_value, std_err = linregress(c[mask], cc[mask])
    axs[1].set_title(f"old (R² = {r_value**2:.2f})")
    axs[1].set_ylabel("corrected C")

    plt.show()


def compare():
    transects, all_valid_profiles = import_split_and_make_transects(parameters="all",
                                                                    pre_processing_function=new_preprocessing,
                                                                    despiking_method="minimum")
    for p in all_valid_profiles:
        plt.plot(p.data["depth"], p.data["chlorophyll"], label="raw")
        plt.plot(p.data["depth"], p.data["chlorophyll_corrected"], label="corrected")
        plt.title(f"{str(p.mld)}, {p.night}")
        plt.vlines(p.mld, 0, 10, colors="green", label="MLD")
        plt.legend()
        plt.xlim(0, 130)
        plt.show()


def run():
    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=new_preprocessing, quenching_method=default_quenching_correction, use_cache=True,
                                                                    despiking_method="minimum")
    p_of_interest = []
    for p in all_valid_profiles:
        if not p.night and p.direction == "up":
            p_of_interest.append(p)
    
    d = concatenate_profiles(p_of_interest)
    d = d[d["depth"] < 40]
    d = d[d["depth"] > 3]

    fig, axs = plt.subplots(2, 2)
    axs = axs.flatten()

    axs[0].scatter(d["chlorophyll"], d["scatter_650"], c=d["depth"], marker="x", linewidth=1)
    axs[0].set_title("up day")
    axs[0].set_xlabel("Chlorophyll")
    axs[0].set_ylabel("Scatter 650")
    axs[1].scatter(d["chlorophyll"], d["bbp_minimum_despiked"], c=d["depth"], marker="x", linewidth=1)
    axs[1].set_title("up day")
    axs[1].set_xlabel("Chlorophyll")
    axs[1].set_ylabel("bbp despiked")


    p_of_interest = []
    for p in all_valid_profiles:
        if not p.night and p.direction == "down":
            p_of_interest.append(p)
    
    d = concatenate_profiles(p_of_interest)
    d = d[d["depth"] < 40]
    d = d[d["depth"] > 3]

    axs[2].scatter(d["chlorophyll"], d["scatter_650"], c=d["depth"], marker="x", linewidth=1)
    axs[2].set_title("down day")
    axs[2].set_xlabel("Chlorophyll")
    axs[2].set_ylabel("Scatter 650")
    pcm = axs[3].scatter(d["chlorophyll"], d["bbp_minimum_despiked"], c=d["depth"], marker="x", linewidth=1)
    axs[3].set_title("down day")
    axs[3].set_xlabel("Chlorophyll")
    axs[3].set_ylabel("bbp despiked")

    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")

    plt.show()


def dump():
    # change the line below and the label as well as depth vs MLD_normalised_depth
    preprocessing = new_preprocessing
    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=preprocessing, quenching_method=default_quenching_correction, use_cache=True,
                                                                    despiking_method="minimum")
    
    fig, axs = plt.subplots(1,1)
    axs = [axs]
    #axs = axs.flatten()


    for profile in all_valid_profiles:
        profile.data["MLD_normalised_depth"] = profile.data["depth"] / profile.mld 

    night_profiles = []
    day_profiles = []
    for p in all_valid_profiles:
        if not p.night:
            day_profiles.append(p.data)
        else:
            night_profiles.append(p.data)

    day_df = pd.concat(day_profiles)
    night_df = pd.concat(night_profiles)

    day_df = day_df[day_df["MLD_normalised_depth"] < 2]
    day_df = day_df[day_df["depth"] > 3]
    day_df = day_df[day_df["depth"] < 100]
    day_df["MLD_normalised_depth"] = day_df["MLD_normalised_depth"].round(2)
    day_df["depth"] = day_df["depth"].round(0)

    night_df = night_df[night_df["MLD_normalised_depth"] < 2]
    night_df = night_df[night_df["depth"] > 3]
    night_df = night_df[night_df["depth"] < 100]
    night_df["MLD_normalised_depth"] = night_df["MLD_normalised_depth"].round(2)
    night_df["depth"] = night_df["depth"].round(0)
    
    day_mean_values = day_df.groupby("depth")["chlorophyll"].mean().values
    night_mean_values = night_df.groupby("depth")["chlorophyll"].mean().values
    day_corrected_mean_values = day_df.groupby("depth")["chlorophyll_corrected"].mean().values
    depths = day_df.groupby("depth")["depth"].mean().values

    slope, intercept, r1_value, p_value, std_err = linregress(day_mean_values, night_mean_values)
    slope, intercept, r2_value, p_value, std_err = linregress(day_corrected_mean_values, night_mean_values)


    sns.lineplot(data=day_df, ax=axs[0], x="depth", y="chlorophyll", label="day, raw")
    sns.lineplot(data=day_df, ax=axs[0], x="depth", y="chlorophyll_corrected", label="day, new")
    sns.lineplot(data=night_df, ax=axs[0], x="depth", y="chlorophyll_corrected", label="night")


    axs[0].set_xlabel("")
    axs[0].set_ylabel("")        
    axs[0].text(s=f"R²s: {r1_value**2:.2f}, {r2_value**2:.2f}", x=0.5, y=0.25)
    print(r2_value**2)
    axs[0].text(0.95, 0.95, f'overall', transform=axs[0].transAxes, ha='right', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
    #plt.title(f"day/night :{r1_value**2:.2f}, daycorrected/night: {r2_value**2:.2f}")




    # for i, transect in enumerate(transects):
    #     all_valid_profiles = transect.get_profiles()

    #     for profile in all_valid_profiles:
    #         profile.data["MLD_normalised_depth"] = profile.data["depth"] / profile.mld 

    #     night_profiles = []
    #     day_profiles = []
    #     for p in all_valid_profiles:
    #         if not p.night:
    #             day_profiles.append(p.data)
    #         else:
    #             night_profiles.append(p.data)

    #     day_df = pd.concat(day_profiles)
    #     night_df = pd.concat(night_profiles)

    #     day_df = day_df[day_df["MLD_normalised_depth"] < 2]
    #     day_df = day_df[day_df["depth"] > 3]
    #     day_df = day_df[day_df["depth"] < 100]
    #     day_df["MLD_normalised_depth"] = day_df["MLD_normalised_depth"].round(2)
    #     day_df["depth"] = day_df["depth"].round(0)

    #     night_df = night_df[night_df["MLD_normalised_depth"] < 2]
    #     night_df = night_df[night_df["depth"] > 3]
    #     night_df = night_df[night_df["depth"] < 100]
    #     night_df["MLD_normalised_depth"] = night_df["MLD_normalised_depth"].round(2)
    #     night_df["depth"] = night_df["depth"].round(0)
        
    #     day_mean_values = day_df.groupby("depth")["chlorophyll"].mean().values
    #     night_mean_values = night_df.groupby("depth")["chlorophyll"].mean().values
    #     day_corrected_mean_values = day_df.groupby("depth")["chlorophyll_corrected"].mean().values
    #     depths = day_df.groupby("depth")["depth"].mean().values

    #     slope, intercept, r1_value, p_value, std_err = linregress(day_mean_values, night_mean_values)
    #     slope, intercept, r2_value, p_value, std_err = linregress(day_corrected_mean_values, night_mean_values)

    #     if i == 0:
    #         sns.lineplot(data=day_df, ax=axs[i], x="depth", y="chlorophyll", label="day, raw")
    #         sns.lineplot(data=day_df, ax=axs[i], x="depth", y="chlorophyll_corrected", label="day, new")
    #         sns.lineplot(data=night_df, ax=axs[i], x="depth", y="chlorophyll_corrected", label="night")
    #     else:
    #         sns.lineplot(data=day_df, ax=axs[i], x="depth", y="chlorophyll")
    #         sns.lineplot(data=day_df, ax=axs[i], x="depth", y="chlorophyll_corrected")
    #         sns.lineplot(data=night_df, ax=axs[i], x="depth", y="chlorophyll_corrected")

    #     axs[i].set_xlabel("")
    #     axs[i].set_ylabel("")        
    #     axs[i].text(s=f"R²s: {r1_value**2:.2f}, {r2_value**2:.2f}", x=0.5, y=0.25)
    #     print(r2_value)
    #     axs[i].text(0.95, 0.95, f'Transect {i+1}', transform=axs[i].transAxes, ha='right', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
    #plt.title(f"day/night :{r1_value**2:.2f}, daycorrected/night: {r2_value**2:.2f}")

    axs[0].legend()
    plt.show()



    with open('Louis/cache/new_chlorophyll_values.pkl', 'wb') as f:
        pickle.dump({
        'day_mean_values': day_mean_values,
        'night_mean_values': night_mean_values,
        'day_corrected_mean_values': day_corrected_mean_values,
        'depths': depths
        }, f)

def load():
    with open('Louis/cache/old_chlorophyll_values.pkl', 'rb') as f:
        data = pickle.load(f)
    with open('Louis/cache/new_chlorophyll_values.pkl', 'rb') as f:
        data2 = pickle.load(f)
    depths = data['depths']
    day =  data['day_mean_values']
    night = data['night_mean_values']
    old = data['day_corrected_mean_values']
    new = data2['day_corrected_mean_values']



    slope, intercept, r1_value, p_value, std_err = linregress(day, night)
    print(f"Raw Day vs Night R²: {r1_value**2:.2f}")
    slope, intercept, r2_value, p_value, std_err = linregress(new, night)
    print(f"New Corrected Day vs Night R²: {r2_value**2:.2f}")
    slope, intercept, r3_value, p_value, std_err = linregress(old, night)
    print(f"Old Corrected Day vs Night R²: {r3_value**2:.2f}")


    fig, axs = plt.subplots(1, 3)   
    axs[0].scatter(night, day, c=depths)
    axs[1].scatter(night, old, c=depths)
    pcm=axs[2].scatter(night, new, c=depths)

    axs[0].set_xlabel("Night Chlorophyll")
    axs[0].set_ylabel("Day Chlorophyll")
    axs[1].set_xlabel("Night Chlorophyll")
    axs[1].set_ylabel("Day Corrected Chlorophyll")
    axs[2].set_xlabel("Night Chlorophyll")
    axs[2].set_ylabel("Day Corrected Chlorophyll")
    axs[0].set_title("Raw Day vs Night, R²: {:.2f}".format(r1_value**2))
    axs[1].set_title("Old Corrected Day vs Night, R²: {:.2f}".format(r3_value**2))
    axs[2].set_title("New Corrected Day vs Night, R²: {:.2f}".format(r2_value**2))
  
    cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
    plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
    plt.show()



   


def correlate():
    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=new_preprocessing, quenching_method=default_quenching_correction, use_cache=True,
                                                                    despiking_method="minimum")
    
    
    main_df = pd.concat([profile.data for profile in transects[0].get_profiles()])
    main_df = main_df[main_df["depth"] > 5]



    sns.scatterplot(data=main_df, x="chlorophyll_corrected", y="chlorophyll", color="#FFFFFF00", edgecolor="black", marker="o")
    plt.title("excluding top 10m")
    plt.show()


def transect_plot():
    transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=new_preprocessing, use_cache=True, quenching_method=default_quenching_correction)
    for j in range(10):
        fig, axs = plt.subplots(2, 1, sharey=True)
        axs = axs.flatten()
        profiles = transects[j].get_profiles()
        profiles = [p for p in profiles if p.direction == "up"]
        pcm = binned_plot(profiles, axs[1], "chlorophyll_corrected", 2, 150)
        binned_plot(profiles, axs[0], "chlorophyll", 2, 150)
        axs[0].set_ylabel("Depth (m)")
        axs[0].set_title("Unprocessed")
        axs[1].set_title("Processed")
        cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
        plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
        cbar_ax.set_xlabel("Chlorophyll (mg/m^3)")
        plt.suptitle("Downcast chlorophyll")
        plt.show()

if __name__ == "__main__":
    #transect_plot()
    dump()
    #correlate()