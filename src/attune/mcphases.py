"""Load mcPHASES into one participant-day table with hormone-based phase labels."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

KEY = ["id", "study_interval", "day_in_study"]


def load_daily(root: Path) -> pd.DataFrame:
    phases = (pd.read_csv(root / "hormones_and_selfreport.csv")
              .dropna(subset=["phase"]).drop_duplicates(KEY))
    phases["phase"] = phases["phase"].replace({"Fertility": "Ovulatory"})

    rhr = pd.read_csv(root / "resting_heart_rate.csv")
    rhr = rhr[rhr["value"] > 0].groupby(KEY)["value"].mean().rename("rhr")

    hrv = (pd.read_csv(root / "heart_rate_variability_details.csv", usecols=KEY + ["rmssd"])
           .groupby(KEY)["rmssd"].mean().rename("hrv_rmssd"))

    cols = ["lh", "estrogen", "pdg", "fatigue", "moodswing", "stress", "bloating", "cramps"]
    return (phases[KEY + ["phase"] + cols].set_index(KEY)
            .join([rhr, hrv]).reset_index())
