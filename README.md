# Quick Disk Check

`quick-disk-check` is a fast Linux disk screening tool powered by SMART (`smartctl -x -j`).
It provides both a GUI flow for quick checks and a CLI flow for automation and logging.

## Why this project is useful

- Uses structured SMART JSON (no fragile text parsing)
- Applies clear buy/no-buy rules for core failure indicators
- Produces human report + raw JSON for auditability
- Includes unit tests and CI for reliability

## Decision rules

Hard-failure indicators (must be zero for a healthy used drive):

- `Reallocated_Sector_Ct`
- `Current_Pending_Sector`
- `Offline_Uncorrectable`

SMART overall health must not be `FAILED`.

Power-on hours are wear guidance, not universal pass/fail:

- `< 10000`: low wear
- `10000-30000`: moderate wear
- `> 30000`: high wear (`CAUTION`)

## Verdicts

- `DO NOT BUY`: hard-failure indicator non-zero or SMART health failed
- `CAUTION`: hard indicators clean, but very high hours
- `GOOD (USED)`: hard indicators clean with moderate hours
- `GOOD`: hard indicators clean with low hours
- `INCONCLUSIVE`: SMART data incomplete (usually permissions), rerun with sudo/pkexec

## Project layout

- `quick_disk_check.py`: backward-compatible launcher (GUI by default)
- `src/quick_disk_check/`: package code
	- `smartctl_io.py`: disk listing + SMART JSON I/O
	- `evaluator.py`: metrics extraction + verdict engine
	- `reporting.py`: text report builder
	- `app.py`: orchestration pipeline
	- `cli.py`: CLI entrypoint
	- `gui.py`: Tkinter GUI
- `tests/`: pytest suite
- `.github/workflows/ci.yml`: CI test workflow

## Requirements

- Linux
- Python `>=3.10`
- `smartmontools` (`smartctl`)
- GUI mode uses `pkexec` for privilege elevation

## Quick start

Run GUI:

```bash
python3 /home/ergo/Desktop/project/quick_disk_check.py
```

Run CLI scan:

```bash
sudo python3 /home/ergo/Desktop/project/quick_disk_check.py --test /dev/sda
```

Using `sudo` is recommended for CLI scans so SMART attributes are complete.

Or install as a package and run command:

```bash
cd /home/ergo/Desktop/project
python3 -m pip install .[dev]
quick-disk-check --test /dev/sda
```

## Output artifacts

Each scan writes into `reports/`:

- `disk_report_<disk>_<timestamp>.txt`
- `disk_report_<disk>_<timestamp>.json`

## Local tests

```bash
cd /home/ergo/Desktop/project
python3 -m pip install .[dev]
python3 -m pytest
```

## Notes

- Software cannot detect mechanical noise; a physical listening test is still recommended.
- ATA error log history is surfaced in notes for deeper investigation.
