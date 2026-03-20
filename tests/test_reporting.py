from quick_disk_check.evaluator import evaluate, extract_metrics
from quick_disk_check.reporting import build_report


def test_report_contains_core_fields() -> None:
    smart_json = {
        "smart_status": {"passed": True},
        "model_name": "DriveX",
        "serial_number": "SN42",
        "user_capacity": {"bytes": 500_000_000_000},
        "ata_smart_error_log": {"extended": {"count": 0}},
        "ata_smart_attributes": {
            "table": [
                {"name": "Reallocated_Sector_Ct", "raw": {"value": 0}},
                {"name": "Current_Pending_Sector", "raw": {"value": 0}},
                {"name": "Offline_Uncorrectable", "raw": {"value": 0}},
                {"name": "Power_On_Hours", "raw": {"value": 1234}},
            ]
        },
    }

    metrics = extract_metrics(smart_json, "/dev/sdx")
    verdict, _, reason, notes = evaluate(metrics)
    report = build_report(metrics, verdict, reason, notes)

    assert "--- Disk: /dev/sdx ---" in report
    assert "Overall Health: PASSED" in report
    assert "Power On Hours: 1234" in report
    assert "VERDICT: GOOD" in report
