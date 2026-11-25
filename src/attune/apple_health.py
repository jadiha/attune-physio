"""Stream-parse an Apple Health export.xml into tidy record and daily tables.

export.xml is ~100MB+ and grows every year, so it is parsed with iterparse and
each element is cleared after use instead of loading the whole tree.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

# HealthKit identifier -> short metric name
METRICS = {
    "HKQuantityTypeIdentifierHeartRate": "hr",
    "HKQuantityTypeIdentifierRestingHeartRate": "rhr",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv_sdnn",
    "HKQuantityTypeIdentifierRespiratoryRate": "resp_rate",
    "HKQuantityTypeIdentifierAppleSleepingWristTemperature": "wrist_temp",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
    "HKCategoryTypeIdentifierMenstrualFlow": "menstrual_flow",
}


def parse_records(xml_path: Path) -> pd.DataFrame:
    rows = []
    for _, el in ET.iterparse(xml_path, events=("end",)):
        if el.tag == "Record":
            metric = METRICS.get(el.get("type"))
            if metric:
                rows.append((metric, el.get("sourceName"), el.get("startDate"),
                             el.get("endDate"), el.get("value")))
        if el.tag in ("Record", "Workout", "ActivitySummary"):
            el.clear()
    df = pd.DataFrame(rows, columns=["metric", "source", "start", "end", "value"])
    # Apple writes local time with an offset ("2025-01-01 07:00:00 -0500"); keep local wall time.
    for c in ("start", "end"):
        df[c] = pd.to_datetime(df[c].str[:19])
    df["numeric"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def daily_table(rec: pd.DataFrame) -> pd.DataFrame:
    """One row per calendar day. Sleep is credited to the morning you wake up."""
    rec = rec.assign(date=rec["start"].dt.normalize())
    q = rec.dropna(subset=["numeric"])

    def per_day(metric, how):
        return q[q.metric == metric].groupby("date")["numeric"].agg(how)

    # Steps: iPhone and Watch both count steps; take the larger source per day to avoid double counting.
    steps = (q[q.metric == "steps"].groupby(["date", "source"])["numeric"].sum()
             .groupby("date").max())

    sleep = rec[(rec.metric == "sleep") & rec["value"].str.contains("Asleep", na=False)].copy()
    sleep["hours"] = (sleep["end"] - sleep["start"]).dt.total_seconds() / 3600
    sleep["date"] = (sleep["end"] - pd.Timedelta(hours=12)).dt.normalize() + pd.Timedelta(days=1)

    daily = pd.DataFrame({
        "steps": steps,
        "rhr": per_day("rhr", "mean"),
        "min_hr": per_day("hr", "min"),
        "hr_samples": per_day("hr", "size"),
        "hrv_sdnn": per_day("hrv_sdnn", "mean"),
        "resp_rate": per_day("resp_rate", "mean"),
        "wrist_temp": per_day("wrist_temp", "mean"),
        "sleep_hours": sleep.groupby("date")["hours"].sum(),
    })
    daily.index.name = "date"
    return daily.sort_index()
