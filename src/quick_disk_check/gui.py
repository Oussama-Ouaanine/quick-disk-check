from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import subprocess

from .app import run_scan
from .smartctl_io import list_disks, SmartctlError


def _show_result_dialog(
    parent: tk.Tk,
    title: str,
    level: str,
    verdict: str,
    text: str,
    report_path: Path,
    json_path: Path,
) -> None:
    color_map = {
        "error": ("#7f1d1d", "#fee2e2"),
        "warning": ("#78350f", "#fef3c7"),
        "info": ("#0f172a", "#dbeafe"),
    }
    accent, background = color_map.get(level, ("#0f172a", "#e2e8f0"))

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("860x620")
    win.minsize(760, 520)
    win.transient(parent)
    win.grab_set()

    header = tk.Frame(win, bg=background, padx=16, pady=12)
    header.pack(fill="x")
    tk.Label(
        header,
        text=f"Verdict: {verdict}",
        font=("Arial", 15, "bold"),
        bg=background,
        fg=accent,
        anchor="w",
    ).pack(fill="x")
    tk.Label(
        header,
        text=f"Report: {report_path.name}",
        font=("Arial", 10),
        bg=background,
        fg="#334155",
        anchor="w",
    ).pack(fill="x", pady=(4, 0))

    body = scrolledtext.ScrolledText(
        win,
        wrap="word",
        font=("Consolas", 10),
        padx=12,
        pady=10,
    )
    body.pack(fill="both", expand=True, padx=12, pady=12)
    body.insert("1.0", text)
    body.config(state="disabled")

    actions = tk.Frame(win, padx=12, pady=10)
    actions.pack(fill="x")

    def copy_report() -> None:
        parent.clipboard_clear()
        parent.clipboard_append(text)
        messagebox.showinfo("Copied", "Report copied to clipboard.")

    def open_reports_folder() -> None:
        try:
            subprocess.Popen(["xdg-open", str(report_path.parent)])
        except Exception as exc:
            messagebox.showerror("Open Failed", f"Could not open folder:\n{exc}")

    tk.Button(actions, text="Copy Report", command=copy_report).pack(side="left")
    tk.Button(actions, text="Open Reports Folder", command=open_reports_folder).pack(side="left", padx=8)
    tk.Button(actions, text="Close", command=win.destroy, width=12).pack(side="right")

    path_row = tk.Frame(win, padx=12, pady=0)
    path_row.pack(fill="x", pady=(0, 10))
    tk.Label(path_row, text=f"TXT:  {report_path}", anchor="w", fg="#475569").pack(fill="x")
    tk.Label(path_row, text=f"JSON: {json_path}", anchor="w", fg="#475569").pack(fill="x")


def create_gui() -> None:
    root = tk.Tk()
    root.title("Quick Disk Buyer's Check")
    root.geometry("560x220")
    root.eval("tk::PlaceWindow . center")

    tk.Label(root, text="Quick Disk Buyer's Check", font=("Arial", 14, "bold")).pack(pady=(14, 4))
    tk.Label(root, text="Select a drive and run a SMART safety check.", fg="#475569").pack(pady=(0, 10))

    try:
        disks = list_disks()
    except Exception as exc:
        disks = [f"Error getting disks: {exc}"]

    combo = ttk.Combobox(root, values=disks, state="readonly", width=48)
    combo.pack(pady=5)
    if disks:
        combo.current(0)

    def on_scan() -> None:
        selection = combo.get()
        if not selection or selection.startswith("Error getting disks"):
            messagebox.showerror("Error", "Please select a valid disk first.")
            return

        disk_path = selection.split(" - ")[0]
        try:
            result = run_scan(disk_path=disk_path, reports_dir=Path.cwd() / "reports", use_pkexec=True)
        except SmartctlError as exc:
            messagebox.showerror("Error", f"smartctl failed:\n{exc}")
            return
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to scan disk:\n{exc}")
            return

        body = (
            result.report_text
            + f"\n\nSaved Report: {result.report_path}"
            + f"\nSaved Raw JSON: {result.raw_json_path}"
        )

        title = "Disk Results"
        if result.level == "error":
            title = "Disk Results: DO NOT BUY"
        elif result.level == "warning":
            title = "Disk Results: CAUTION"
        _show_result_dialog(
            parent=root,
            title=title,
            level=result.level,
            verdict=result.verdict,
            text=body,
            report_path=result.report_path,
            json_path=result.raw_json_path,
        )

    tk.Button(
        root,
        text="Scan & Check Condition",
        font=("Arial", 10, "bold"),
        command=on_scan,
    ).pack(pady=14)

    root.mainloop()
