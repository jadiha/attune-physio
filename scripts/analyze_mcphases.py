"""Step 2: cohort-level phase effects in mcPHASES.

Writes ONLY aggregate results to reports/public/ (no participant ids, no per-person rows),
which is what the PhysioNet license allows to be published.
"""
import pandas as pd

from attune.cycles import PHASES
from attune.mcphases import load_daily
from attune.paths import MCPHASES, REPORTS_PUBLIC
from attune.stats import phase_shift

df = load_daily(MCPHASES)
print(f"{df['id'].nunique()} participants, {len(df):,} phase-labelled days")

shifts = pd.DataFrame([phase_shift(df, "rhr"), phase_shift(df, "hrv_rmssd")])

# Phase means of each person's z-scored values, so differences in personal level drop out.
z = df.copy()
for col in ["rhr", "hrv_rmssd"]:
    z[col] = z.groupby("id")[col].transform(lambda s: (s - s.mean()) / s.std())
profile = (z.groupby(["id", "phase"])[["rhr", "hrv_rmssd"]].mean()
           .groupby("phase").mean().reindex(PHASES))

REPORTS_PUBLIC.mkdir(parents=True, exist_ok=True)
shifts.to_csv(REPORTS_PUBLIC / "mcphases_luteal_vs_follicular.csv", index=False)
profile.round(3).to_csv(REPORTS_PUBLIC / "mcphases_phase_profile_z.csv")

pd.set_option("display.width", 160)
print(shifts.to_string(index=False, float_format=lambda x: f"{x:.3g}"))
print("\nMean within-person z-score by phase:\n", profile.round(2))
