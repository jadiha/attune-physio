"""Label each day with its cycle phase from logged period dates.

Phases are counted backwards from the next period, because the luteal phase is
fairly fixed (~14 days) while the follicular phase absorbs cycle-length variation:
  Menstrual   period days
  Follicular  after the period, until the ovulatory window
  Ovulatory   16 to 12 days before the next period (estimated ovulation ~14 days before)
  Luteal      the last 11 days before the next period
Without hormone tests this is an estimate. mcPHASES labels phases from measured LH and hormones.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PHASES = ["Menstrual", "Follicular", "Ovulatory", "Luteal"]


def load_cycles(path: Path) -> pd.DataFrame:
    c = pd.read_csv(path, parse_dates=["start", "end"]).sort_values("start").reset_index(drop=True)
    c["length"] = c["start"].shift(-1) - c["start"]
    return c


def label_days(dates: pd.DatetimeIndex, cycles: pd.DataFrame) -> pd.DataFrame:
    typical = cycles["length"].dropna().median()
    if pd.isna(typical):
        typical = pd.Timedelta(days=28)
    out = []
    for d in dates:
        past = cycles[cycles["start"] <= d]
        if past.empty:
            out.append((pd.NA, pd.NA, pd.NA, True))
            continue
        cur = past.iloc[-1]
        nxt = cur["start"] + (cur["length"] if pd.notna(cur["length"]) else typical)
        predicted = pd.isna(cur["length"])  # current cycle: next period not logged yet
        cycle_day = (d - cur["start"]).days + 1
        to_next = (nxt - d).days
        if d <= cur["end"]:
            phase = "Menstrual"
        elif to_next <= 11:
            phase = "Luteal"
        elif to_next <= 16:
            phase = "Ovulatory"
        else:
            phase = "Follicular"
        out.append((cur["start"].date(), cycle_day, phase, predicted))
    return pd.DataFrame(out, index=dates, columns=["cycle_start", "cycle_day", "phase", "phase_predicted"])
