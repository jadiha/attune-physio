# Attune: personal physiological intelligence

How do resting heart rate, HRV, sleep and temperature move across the menstrual cycle,
in a research cohort and in one person's own wearable data?

Most wearables treat a body as if it were the same every day. For roughly half the
population it isn't: hormones shift on a ~28–35 day rhythm, and resting heart rate, HRV
and skin temperature shift with them. A "bad recovery" score in the week before a period may
just be the luteal phase, not overtraining or getting sick. This project measures that
rhythm, first across 42 people with lab-measured hormones, then on my own Apple Watch.
The goal is baselines that know where you are in your cycle.

## Questions

1. Across a cohort, do RHR and HRV change by cycle phase, and does it happen for most
   people or only on average?
2. Does my own data show the same pattern, and how large is my personal swing?
3. Can cycle-aware baselines tell normal hormonal variation apart from real anomalies
   (illness, poor sleep, stress)?

## Data

| Source | What | Phase labels |
|---|---|---|
| [mcPHASES](https://physionet.org/content/mcphases/) (PhysioNet) | 42 participants, Fitbit + LH/estrogen/PdG + daily symptoms, 2022 & 2024 | From measured hormones |
| My Apple Health export | Watch: HR, HRV (SDNN), resting HR, respiratory rate, wrist temp, sleep. iPhone: 2 yrs of steps | From logged period dates (`config/cycles.csv`) |

## Findings so far

**mcPHASES (42 participants, 5,658 phase-labelled days).** Each person is compared against
their own follicular baseline:

| Metric | Luteal vs follicular | People moving that way | p (sign test) |
|---|---|---|---|
| Resting HR | **+2.5 bpm** | 37 / 42 | < 0.001 |
| HRV (RMSSD) | **−5.4 ms** | 33 / 39 | < 0.001 |

This is consistent with published work on wearables and the menstrual cycle, which reports
RHR rising and HRV falling after ovulation as progesterone climbs.

**Personal data.** Collection in progress. Personal results stay local (see Privacy).

## Pipeline

```
export.xml ──► ingest_apple_health.py ──► apple_daily.csv ─┐
                (streaming XML parse)                      ├─► analyze_personal.py ──► reports/private/
config/cycles.csv ──► cycles.label_days ───────────────────┘    (phase means, rolling baselines, anomaly flags)

mcPHASES CSVs ──► mcphases.load_daily ──► analyze_mcphases.py ──► reports/public/ (aggregate only)
                                           (within-person shifts, sign + Wilcoxon tests)
```

- `src/attune/apple_health.py`: streams the 100MB+ export with `iterparse`, de-duplicates
  iPhone vs Watch steps, and credits sleep to the morning you wake up.
- `src/attune/cycles.py`: phase labels counted back from the next period, since the luteal
  phase is the stable one.
- `src/attune/stats.py`: within-person phase shifts, plus a rolling 28-day median/MAD baseline
  for anomaly flags.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
cp config/cycles.example.csv config/cycles.csv      # then put your own period dates in it
# put data in data/raw/ (see data/README.md)
.venv/bin/python scripts/ingest_apple_health.py
.venv/bin/python scripts/analyze_mcphases.py
.venv/bin/python scripts/analyze_personal.py
```

## Privacy

This repo contains code and aggregate results only.

- **mcPHASES** is under the PhysioNet Restricted Health Data License: the data can't be shared,
  so it is never committed. Only cohort-level summaries (no participant ids) go in `reports/public/`.
- **Personal health data and period dates** stay in `data/`, `config/cycles.csv` and
  `reports/private/`, which are all git-ignored.
- A pre-commit hook (`.githooks/pre-commit`) blocks data files and private paths even if
  someone force-adds them. Enable it after cloning: `git config core.hooksPath .githooks`.

## Roadmap

- [x] Apple Health ingestion pipeline
- [x] mcPHASES cohort analysis
- [x] Cycle phase labelling, personal baselines, first anomaly flags
- [ ] Flo export import (longer period history → steps by phase over 2 years)
- [ ] 3+ cycles of nightly watch wear → personal luteal vs follicular comparison
- [ ] Compare personal effect sizes to the cohort distribution
- [ ] Interactive dashboard (React)
- [ ] Cycle-aware anomaly detection: does knowing the phase reduce false alarms?
