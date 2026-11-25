"""Within-person phase comparisons.

Everyone's resting HR and HRV sit at different levels, so pooling raw values hides
the cycle effect. Each person is compared against their own follicular baseline,
then we count how many people move in the same direction (sign test) and how
large the shift is (Wilcoxon signed-rank on the paired differences).
"""
from __future__ import annotations

import pandas as pd
from scipy import stats


def phase_shift(df: pd.DataFrame, value: str, person: str = "id",
                a: str = "Luteal", b: str = "Follicular") -> dict:
    means = df.groupby([person, "phase"])[value].mean().unstack()
    diff = (means[a] - means[b]).dropna()
    up = int((diff > 0).sum())
    return {
        "metric": value,
        "comparison": f"{a} - {b}",
        "n_people": int(len(diff)),
        "mean_shift": float(diff.mean()),
        "median_shift": float(diff.median()),
        "n_up": up,
        "sign_test_p": float(stats.binomtest(up, len(diff)).pvalue),
        "wilcoxon_p": float(stats.wilcoxon(diff).pvalue),
    }


def rolling_baseline(series: pd.Series, window: str = "28D", min_periods: int = 7) -> pd.DataFrame:
    """Personal baseline: rolling median and robust spread over the previous window (today excluded)."""
    s = series.dropna()
    past = s.shift(1)
    med = past.rolling(window, min_periods=min_periods).median()
    mad = (past - med).abs().rolling(window, min_periods=min_periods).median() * 1.4826
    z = (s - med) / mad
    return pd.DataFrame({"value": s, "baseline": med, "spread": mad, "z": z})
