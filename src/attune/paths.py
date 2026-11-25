from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
APPLE_HEALTH_XML = RAW / "apple_health_export" / "export.xml"
MCPHASES = RAW / "mcphases"
CYCLES = ROOT / "config" / "cycles.csv"
REPORTS_PUBLIC = ROOT / "reports" / "public"     # aggregate, shareable outputs only
REPORTS_PRIVATE = ROOT / "reports" / "private"   # anything derived from personal data
