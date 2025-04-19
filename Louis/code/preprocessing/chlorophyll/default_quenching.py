import numpy as np
def default_quenching_correction(profiles:list, despiking_method:str="minimum") -> list:
    print("Applying quenching correction...")
    with open("Louis/data/day_night1.txt", "r") as f:
        night = f.readlines()
        night = [True if i.rstrip("\n") == "1" else False for i in night]
        
    night_timings = {}

    for i, profile in enumerate(profiles):
        C_to_B_ratio = profile.data["chlorophyll"] / profile.data[f"bbp_debubbled_despiked"]
        profile.data["CtoB"] = C_to_B_ratio

        mixed_layer_df = profile.data[profile.data["depth"] < profile.mld]
        mixed_layer_df = mixed_layer_df[mixed_layer_df["depth"] > 3]

        C_to_B_mixed_layer_mean = mixed_layer_df["CtoB"].mean()
        profile.CtoB_ML_mean = C_to_B_mixed_layer_mean

        profile.night = night[i]
        if profile.direction == "up":
            profile.surface_time = profile.end_time
        else:
            profile.surface_time = profile.start_time


        if profile.night and (not np.isnan(C_to_B_mixed_layer_mean) and profile.direction == "up"):
            night_timings[profile.surface_time] = i

    for i, profile in enumerate(profiles):
        if not profile.night:

            nearest_night_surface_time = min(night_timings.keys(), key=lambda x: abs(x - profile.surface_time))
            nearest_night_index = night_timings[nearest_night_surface_time]
            night_CtoB_mean = profiles[nearest_night_index].CtoB_ML_mean    
            


            chlorophyll = profile.data["chlorophyll"].fillna(0)
            bbp = profile.data["bbp_debubbled_despiked"]
            depth = profile.data["depth"]

            chlorophyll_corrected = []
            for j in range(depth.first_valid_index(), depth.last_valid_index()+1):
                if profile.mld < 5:
                    chlorophyll_corrected.append(chlorophyll[j])
                elif depth[j] < profile.mld:
                    new_c = bbp[j] * night_CtoB_mean
                    new_c = new_c if new_c > chlorophyll[j] else chlorophyll[j]
                    chlorophyll_corrected.append(new_c)
                else:
                    chlorophyll_corrected.append(chlorophyll[j])
            
            profile.data["chlorophyll_corrected"] = chlorophyll_corrected
        else:
            profile.data["chlorophyll_corrected"] = profile.data["chlorophyll"].fillna(0)

          

    return profiles