import argparse
from pathlib import Path

from .app import run_scan


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick Disk Buyer's Check")
    parser.add_argument("--test", metavar="DISK", help="Run CLI scan, e.g. --test /dev/sda")
    parser.add_argument(
        "--reports-dir",
        default=str(Path.cwd() / "reports"),
        help="Directory where report files will be saved",
    )
    args = parser.parse_args()

    if not args.test:
        parser.error("CLI mode requires --test DISK. Use GUI by running quick_disk_check.py without args.")

    result = run_scan(disk_path=args.test, reports_dir=Path(args.reports_dir), use_pkexec=False)
    print(result.report_text)
    print(f"\nSaved Report: {result.report_path}")
    print(f"Saved Raw JSON: {result.raw_json_path}")


if __name__ == "__main__":
    main()
