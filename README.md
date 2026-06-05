# Quick Disk Check

[![CI](https://github.com/Oussama-Ouaanine/quick-disk-check/actions/workflows/ci.yml/badge.svg)](https://github.com/Oussama-Ouaanine/quick-disk-check/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Fast Linux disk screening with SMART data (`smartctl -x -j`) for quick used-drive decisions.

## Highlights

- Structured SMART JSON parsing (no brittle text scraping)
- Clear verdict engine (`GOOD`, `GOOD (USED)`, `CAUTION`, `DO NOT BUY`, `INCONCLUSIVE`)
- GUI mode for quick checks and CLI mode for automation
- Saves both human-readable `.txt` and raw `.json` reports
- Covered by unit tests and CI

## Requirements

- Linux
- Python **3.10+**
- `smartmontools` (`smartctl`)
- `pkexec` (GUI privilege elevation)

Install dependencies:

```bash
python3 -m pip install .[dev]
```

## Installation

### Option 1: Run directly from repository

```bash
python3 /tmp/workspace/Oussama-Ouaanine/quick-disk-check/quick_disk_check.py
```

### Option 2: Install CLI entrypoint

```bash
cd /tmp/workspace/Oussama-Ouaanine/quick-disk-check
python3 -m pip install .[dev]
quick-disk-check --test /dev/sda
```

## Usage

### GUI mode

```bash
python3 /tmp/workspace/Oussama-Ouaanine/quick-disk-check/quick_disk_check.py
```

Then select a disk and run the scan.

### CLI mode

```bash
quick-disk-check --test /dev/sda
```

Optional output directory:

```bash
quick-disk-check --test /dev/sda --reports-dir /path/to/reports
```

> For complete SMART attributes, run CLI with elevated privileges when needed (for example `sudo`).

## Decision Rules

A disk is considered unsafe if any hard-failure indicator is non-zero or SMART overall health reports failure.

Hard-failure indicators:

- `Reallocated_Sector_Ct`
- `Current_Pending_Sector`
- `Offline_Uncorrectable`

Power-on-hours guidance:

- `< 10000` → low wear
- `10000-30000` → moderate wear
- `> 30000` → high wear (`CAUTION`)

## Verdicts

- **DO NOT BUY**: hard-failure indicators present or SMART health failed
- **CAUTION**: hard indicators are clean, but wear is high
- **GOOD (USED)**: hard indicators are clean with moderate wear
- **GOOD**: hard indicators are clean with low wear
- **INCONCLUSIVE**: SMART data incomplete (usually permissions)

## Output

Each scan writes to `reports/`:

- `disk_report_<disk>_<timestamp>.txt`
- `disk_report_<disk>_<timestamp>.json`

## Project Structure

- `/tmp/workspace/Oussama-Ouaanine/quick-disk-check/quick_disk_check.py` — backward-compatible launcher (GUI by default)
- `/tmp/workspace/Oussama-Ouaanine/quick-disk-check/src/quick_disk_check/` — package code
  - `smartctl_io.py` — SMART I/O + disk listing
  - `evaluator.py` — metric extraction and verdict logic
  - `reporting.py` — report formatting
  - `app.py` — scan orchestration
  - `cli.py` — CLI entrypoint
  - `gui.py` — Tkinter GUI
- `/tmp/workspace/Oussama-Ouaanine/quick-disk-check/tests/` — test suite
- `/tmp/workspace/Oussama-Ouaanine/quick-disk-check/.github/workflows/ci.yml` — CI workflow

## Development

Run tests:

```bash
cd /tmp/workspace/Oussama-Ouaanine/quick-disk-check
python3 -m pip install .[dev]
python3 -m pytest
```

## Notes

- Software checks SMART telemetry; it cannot detect mechanical noise.
- Review ATA error-history notes in reports for deeper diagnostics.
