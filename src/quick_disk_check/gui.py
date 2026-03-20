from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from .app import run_scan
from .smartctl_io import list_disks, SmartctlError


def _show_result_message(title: str, text: str, level: str) -> None:
    if level == "error":
        messagebox.showerror(title, text)
    elif level == "warning":
        messagebox.showwarning(title, text)
    else:
        messagebox.showinfo(title, text)


def create_gui() -> None:
    root = tk.Tk()
    root.title("Quick Disk Buyer's Check")
    root.geometry("500x180")
    root.eval("tk::PlaceWindow . center")

    tk.Label(root, text="Select a drive to scan quickly:").pack(pady=10)

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
        _show_result_message(title=title, text=body, level=result.level)

    tk.Button(
        root,
        text="Scan & Check Condition",
        font=("Arial", 10, "bold"),
        command=on_scan,
    ).pack(pady=14)

    root.mainloop()
