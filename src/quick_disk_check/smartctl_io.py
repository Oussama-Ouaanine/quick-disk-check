import json
import subprocess
from pathlib import Path


class SmartctlError(RuntimeError):
    pass


def list_disks() -> list[str]:
    output = subprocess.check_output(
        ["lsblk", "-d", "-n", "-o", "NAME,TYPE,MODEL,SIZE"], text=True
    )
    disks: list[str] = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        name, dev_type = parts[0], parts[1]
        if dev_type != "disk" or name.startswith("loop"):
            continue
        pretty = " ".join(parts[2:]) if len(parts) > 2 else ""
        disks.append(f"/dev/{name} - {pretty}".strip())
    return disks


def run_smartctl_json(disk_path: str, use_pkexec: bool = False) -> dict:
    command = ["smartctl", "-x", "-j", disk_path]
    if use_pkexec:
        command = ["pkexec"] + command

    result = subprocess.run(command, text=True, capture_output=True)

    if result.returncode in (126, 127):
        raise SmartctlError((result.stdout + result.stderr).strip() or "smartctl invocation failed")

    if not result.stdout.strip():
        raise SmartctlError("smartctl returned no output")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SmartctlError(f"Invalid smartctl JSON output: {exc}") from exc


def save_outputs(report_text: str, smart_json: dict, disk_path: str, reports_dir: Path) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    disk_name = Path(disk_path).name
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = reports_dir / f"disk_report_{disk_name}_{timestamp}.txt"
    raw_json_path = reports_dir / f"disk_report_{disk_name}_{timestamp}.json"

    report_path.write_text(report_text + "\n", encoding="utf-8")
    raw_json_path.write_text(json.dumps(smart_json, indent=2), encoding="utf-8")

    return report_path, raw_json_path
