from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

VerdictLevel = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class DiskMetrics:
    disk: str
    model: str
    serial: str
    capacity_gb: float
    health: str
    power_on_hours: int
    reallocated: int
    pending: int
    uncorrectable: int
    ata_error_count: int
    data_complete: bool
    timestamp: datetime


@dataclass(frozen=True)
class ScanResult:
    metrics: DiskMetrics
    verdict: str
    level: VerdictLevel
    reason: str
    notes: tuple[str, ...]
    report_text: str
    report_path: Path
    raw_json_path: Path
