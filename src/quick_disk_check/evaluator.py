from datetime import datetime
from .models import DiskMetrics


def _attr_value(attributes: list[dict], attribute_name: str) -> int:
    for item in attributes:
        if item.get("name") == attribute_name:
            return int(item.get("raw", {}).get("value", 0) or 0)
    return 0


def extract_metrics(smart_json: dict, disk_path: str) -> DiskMetrics:
    attributes = smart_json.get("ata_smart_attributes", {}).get("table", [])
    data_complete = len(attributes) > 0
    passed_flag = smart_json.get("smart_status", {}).get("passed")

    if passed_flag is True:
        health = "PASSED"
    elif passed_flag is False:
        health = "FAILED"
    else:
        health = "UNKNOWN"

    ata_errors = int(
        smart_json.get("ata_smart_error_log", {}).get("extended", {}).get("count", 0) or 0
    )

    model = smart_json.get("model_name") or smart_json.get("model_family") or "Unknown"
    serial = smart_json.get("serial_number", "Unknown")
    capacity_bytes = int(smart_json.get("user_capacity", {}).get("bytes", 0) or 0)
    capacity_gb = capacity_bytes / (1000**3) if capacity_bytes else 0.0

    return DiskMetrics(
        disk=disk_path,
        model=model,
        serial=serial,
        capacity_gb=capacity_gb,
        health=health,
        power_on_hours=_attr_value(attributes, "Power_On_Hours"),
        reallocated=_attr_value(attributes, "Reallocated_Sector_Ct"),
        pending=_attr_value(attributes, "Current_Pending_Sector"),
        uncorrectable=_attr_value(attributes, "Offline_Uncorrectable"),
        ata_error_count=ata_errors,
        data_complete=data_complete,
        timestamp=datetime.now(),
    )


def evaluate(metrics: DiskMetrics) -> tuple[str, str, str, tuple[str, ...]]:
    if not metrics.data_complete:
        verdict = "INCONCLUSIVE"
        level = "warning"
        reason = "SMART data is incomplete. Run with elevated privileges (sudo/pkexec) and retry."
        notes = (
            "No reliable ATA SMART attribute table was returned.",
            "A non-privileged scan can produce incomplete data and misleading zero values.",
            "Re-run using sudo or GUI mode to get a trusted verdict.",
        )
        return verdict, level, reason, notes

    hard_fail = (
        metrics.reallocated > 0
        or metrics.pending > 0
        or metrics.uncorrectable > 0
        or metrics.health == "FAILED"
    )

    if hard_fail:
        verdict = "DO NOT BUY"
        level = "error"
        reason = (
            "One or more hard-failure SMART indicators are non-zero "
            "(Reallocated/Pending/Uncorrectable) or overall SMART health failed."
        )
    elif metrics.power_on_hours > 30000:
        verdict = "CAUTION"
        level = "warning"
        reason = "No hard-failure indicators, but usage hours are very high (>30000)."
    elif metrics.power_on_hours >= 10000:
        verdict = "GOOD (USED)"
        level = "info"
        reason = "Hard-failure indicators are clean; drive has moderate wear (10000-30000 hours)."
    else:
        verdict = "GOOD"
        level = "info"
        reason = "Hard-failure indicators are clean and usage hours are relatively low (<10000)."

    notes: list[str] = []
    if metrics.ata_error_count > 0:
        notes.append(
            f"ATA error log has {metrics.ata_error_count} historical entries; investigate with smartctl -l error."
        )
    notes.append("Acoustic/mechanical noise cannot be detected by software; physical listening test is still required.")
    notes.append("Power-On-Hours thresholds are practical guidance, not universal manufacturer pass/fail limits.")

    return verdict, level, reason, tuple(notes)
