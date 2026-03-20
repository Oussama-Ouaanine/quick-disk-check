from pathlib import Path

from .evaluator import evaluate, extract_metrics
from .models import ScanResult
from .reporting import build_report
from .smartctl_io import run_smartctl_json, save_outputs


def run_scan(disk_path: str, reports_dir: Path, use_pkexec: bool = False) -> ScanResult:
    smart_json = run_smartctl_json(disk_path=disk_path, use_pkexec=use_pkexec)
    metrics = extract_metrics(smart_json=smart_json, disk_path=disk_path)
    verdict, level, reason, notes = evaluate(metrics)
    report_text = build_report(metrics=metrics, verdict=verdict, reason=reason, notes=notes)
    report_path, raw_json_path = save_outputs(
        report_text=report_text,
        smart_json=smart_json,
        disk_path=disk_path,
        reports_dir=reports_dir,
    )

    return ScanResult(
        metrics=metrics,
        verdict=verdict,
        level=level,
        reason=reason,
        notes=notes,
        report_text=report_text,
        report_path=report_path,
        raw_json_path=raw_json_path,
    )
