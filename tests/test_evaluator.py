from quick_disk_check.evaluator import evaluate, extract_metrics


def _smart_json(reallocated: int, pending: int, uncorrectable: int, hours: int, passed: bool = True) -> dict:
    return {
        "smart_status": {"passed": passed},
        "model_name": "SampleDrive",
        "serial_number": "ABC123",
        "user_capacity": {"bytes": 1000204886016},
        "ata_smart_error_log": {"extended": {"count": 1}},
        "ata_smart_attributes": {
            "table": [
                {"name": "Reallocated_Sector_Ct", "raw": {"value": reallocated}},
                {"name": "Current_Pending_Sector", "raw": {"value": pending}},
                {"name": "Offline_Uncorrectable", "raw": {"value": uncorrectable}},
                {"name": "Power_On_Hours", "raw": {"value": hours}},
            ]
        },
    }


def test_extract_metrics_fields() -> None:
    metrics = extract_metrics(_smart_json(0, 0, 0, 5000), "/dev/sdz")
    assert metrics.disk == "/dev/sdz"
    assert metrics.health == "PASSED"
    assert metrics.power_on_hours == 5000
    assert metrics.reallocated == 0
    assert metrics.pending == 0
    assert metrics.uncorrectable == 0
    assert metrics.data_complete is True


def test_verdict_do_not_buy_on_bad_sector() -> None:
    metrics = extract_metrics(_smart_json(1, 0, 0, 1000), "/dev/sdz")
    verdict, level, reason, _ = evaluate(metrics)
    assert verdict == "DO NOT BUY"
    assert level == "error"
    assert "hard-failure" in reason


def test_verdict_caution_on_high_hours() -> None:
    metrics = extract_metrics(_smart_json(0, 0, 0, 35000), "/dev/sdz")
    verdict, level, _, _ = evaluate(metrics)
    assert verdict == "CAUTION"
    assert level == "warning"


def test_verdict_good_used_on_mid_hours() -> None:
    metrics = extract_metrics(_smart_json(0, 0, 0, 15000), "/dev/sdz")
    verdict, level, _, _ = evaluate(metrics)
    assert verdict == "GOOD (USED)"
    assert level == "info"


def test_verdict_good_on_low_hours() -> None:
    metrics = extract_metrics(_smart_json(0, 0, 0, 2000), "/dev/sdz")
    verdict, level, _, notes = evaluate(metrics)
    assert verdict == "GOOD"
    assert level == "info"
    assert any("ATA error log" in note for note in notes)


def test_verdict_inconclusive_when_data_missing() -> None:
    smart_json = {
        "smart_status": {"passed": None},
        "model_name": "UnknownDrive",
    }
    metrics = extract_metrics(smart_json, "/dev/sdz")
    verdict, level, reason, _ = evaluate(metrics)
    assert verdict == "INCONCLUSIVE"
    assert level == "warning"
    assert "incomplete" in reason.lower()
