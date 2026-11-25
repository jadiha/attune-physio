"""Step 3: your own data by cycle phase, plus personal baselines and anomaly flags.

Everything this writes is personal, so it goes to reports/private/ (git-ignored).
"""
import pandas as pd

from attune.cycles import PHASES, label_days, load_cycles
from attune.paths import CYCLES, PROCESSED, REPORTS_PRIVATE
from attune.stats import rolling_baseline

daily = pd.read_csv(PROCESSED / "apple_daily.csv", parse_dates=["date"], index_col="date")
cycles = load_cycles(CYCLES)
daily = daily[daily.index >= cycles["start"].min()]
daily = daily.join(label_days(daily.index, cycles))

metrics = ["rhr", "min_hr", "hrv_sdnn", "resp_rate", "wrist_temp", "sleep_hours", "steps"]
by_phase = daily.groupby("phase")[metrics].agg(["mean", "count"]).reindex(PHASES)

flags = []
for m in ["rhr", "hrv_sdnn", "wrist_temp"]:
    b = rolling_baseline(daily[m]).assign(metric=m)
    flags.append(b[b["z"].abs() >= 2.5])
flags = pd.concat(flags)

REPORTS_PRIVATE.mkdir(parents=True, exist_ok=True)
daily.to_csv(REPORTS_PRIVATE / "daily_with_phase.csv")
by_phase.to_csv(REPORTS_PRIVATE / "phase_summary.csv")
flags.to_csv(REPORTS_PRIVATE / "anomalies.csv")

pd.set_option("display.width", 200)
print("Cycle lengths (days):", cycles["length"].dt.days.dropna().astype(int).tolist())
print("\nBy phase (mean / days with data):\n", by_phase.round(1).to_string())
print(f"\n{len(flags)} anomaly flags (|robust z| >= 2.5 vs previous 28 days)")
if not flags.empty:
    print(flags.round(1).to_string())
