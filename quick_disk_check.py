#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from importlib import import_module

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def main() -> None:
    parser = argparse.ArgumentParser(description="Quick Disk Buyer's Check")
    parser.add_argument("--test", metavar="DISK", help="Run CLI scan without GUI, e.g. --test /dev/sda")
    args = parser.parse_args()

    cli_main = import_module("quick_disk_check.cli").main
    create_gui = import_module("quick_disk_check.gui").create_gui

    if args.test:
        sys.argv = [sys.argv[0], "--test", args.test]
        cli_main()
        return
    create_gui()


if __name__ == "__main__":
    main()