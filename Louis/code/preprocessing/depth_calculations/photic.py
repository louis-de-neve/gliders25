import numpy as np
import pandas as pd

def photic_calculation(profiles:list) -> list:
    for p in profiles:
        df = p.data#[p.data["depth"] > 0.5]
        par_max = df["PAR"].max()
        df = df.sort_values("depth")
        df = df.dropna(subset=["PAR"])
        df = df[df["PAR"] < 0.01*par_max]
        photic_depth = df["depth"].iloc[0] if len(df) > 3 else np.nan
        p.photic_depth = photic_depth
    photic_depths = np.asarray([p.photic_depth if (p.photic_depth < 200 and p.photic_depth > 10) else np.nan for p in profiles ])
    photic_depths = pd.Series(photic_depths).interpolate(method='linear', limit_direction='both').to_numpy()
    for i, p in enumerate(profiles):
        p.photic_depth = photic_depths[i]       
    return profiles
