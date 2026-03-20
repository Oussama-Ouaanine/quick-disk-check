from .models import DiskMetrics


def build_report(metrics: DiskMetrics, verdict: str, reason: str, notes: tuple[str, ...]) -> str:
    hours = metrics.power_on_hours
    lines = [
        f"--- Disk: {metrics.disk} ---",
        "",
        f"Scan Time: {metrics.timestamp.isoformat(timespec='seconds')}",
        "Data Source: smartctl JSON (-x -j)",
        f"Model: {metrics.model}",
        f"Serial: {metrics.serial}",
        f"Capacity: {metrics.capacity_gb:.2f} GB",
        "",
        f"Overall Health: {metrics.health}",
        f"Data Complete: {'YES' if metrics.data_complete else 'NO'}",
        f"Power On Hours: {hours} (~{hours // 24} days)",
        f"Reallocated Sectors: {metrics.reallocated}",
        f"Pending Sectors: {metrics.pending}",
        f"Uncorrectable Sectors: {metrics.uncorrectable}",
        f"Internal ATA Error Log Count: {metrics.ata_error_count}",
        "",
        f"VERDICT: {verdict}",
        f"Reason: {reason}",
        "",
        "Rules Applied:",
        "- Hard-failure indicators (Reallocated/Pending/Uncorrectable) must be 0.",
        "- SMART overall health must not be FAILED.",
        "- If SMART data is incomplete, verdict is INCONCLUSIVE (not GOOD).",
        "- Power-On-Hours are wear guidance only (<10k low, 10k-30k moderate, >30k high).",
        "",
        "Notes:",
    ]
    lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines)
