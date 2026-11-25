"""Step 1: Apple Health export.xml -> data/processed/{apple_records,apple_daily}.csv"""
from attune.apple_health import daily_table, parse_records
from attune.paths import APPLE_HEALTH_XML, PROCESSED

PROCESSED.mkdir(parents=True, exist_ok=True)
rec = parse_records(APPLE_HEALTH_XML)
rec.to_csv(PROCESSED / "apple_records.csv", index=False)
daily = daily_table(rec)
daily.to_csv(PROCESSED / "apple_daily.csv")

print(f"{len(rec):,} records kept, {len(daily):,} days")
print(rec.groupby("metric")["start"].agg(["size", "min", "max"]))
