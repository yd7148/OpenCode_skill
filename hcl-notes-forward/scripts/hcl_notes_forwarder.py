#!/usr/bin/env python3
"""
HCL Notes public-notice forwarder.

This is a conservative UI automation helper for the $BySender view:
it finds unread red rows under the public-notice group, forwards one
message to one Notes group, waits for the completion dialog, then deletes
the original message only after the send is verified.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageGrab
except ImportError as exc:
    raise SystemExit("Missing dependency: Pillow. Install with `python -m pip install pillow`.") from exc


DEFAULT_RECIPIENT = "工三碳化矽專案組-03-全組(21)"
DEFAULT_NOTES_EXE = r"C:\lotus\Notes\notes.exe"
DEFAULT_OUTPUT_DIR = Path.home() / ".local" / "share" / "opencode" / "hcl-notes-forward"

USER32 = ctypes.windll.user32
SW_RESTORE = 9
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
VK_RETURN = 0x0D
VK_DELETE = 0x2E


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


@dataclass
class WindowRect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


def powershell(command: str) -> str:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def notes_process() -> tuple[int, int, str] | None:
    script = (
        "$p=Get-Process nlnotes -ErrorAction SilentlyContinue | "
        "Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1; "
        "if($p){ '{0}|{1}|{2}' -f $p.Id,$p.MainWindowHandle,$p.MainWindowTitle }"
    )
    out = powershell(script)
    if not out:
        return None
    pid, hwnd, title = out.split("|", 2)
    return int(pid), int(hwnd), title


def wait_for_notes_window(timeout: int) -> tuple[int, int, str] | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        proc = notes_process()
        if proc:
            return proc
        time.sleep(1)
    return None


def start_notes(notes_exe: str, timeout: int = 30) -> tuple[int, int, str]:
    proc = notes_process()
    if proc:
        return proc
    if not Path(notes_exe).exists():
        raise SystemExit(f"Notes executable not found: {notes_exe}")
    subprocess.Popen([notes_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc = wait_for_notes_window(timeout)
    if not proc:
        raise SystemExit("HCL Notes did not expose a main window before timeout.")
    return proc


def get_window_rect(hwnd: int) -> WindowRect:
    rect = RECT()
    if not USER32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("GetWindowRect failed.")
    return WindowRect(rect.left, rect.top, rect.right, rect.bottom)


def focus_window(hwnd: int) -> None:
    USER32.ShowWindow(hwnd, SW_RESTORE)
    time.sleep(0.2)
    USER32.SetForegroundWindow(hwnd)
    time.sleep(0.3)


def click(x: int, y: int) -> None:
    USER32.SetCursorPos(int(x), int(y))
    time.sleep(0.08)
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)


def press(vk: int) -> None:
    USER32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    USER32.keybd_event(vk, 0, 2, 0)
    time.sleep(0.2)


def screenshot_rect(rect: WindowRect) -> Image.Image:
    return ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom)).convert("RGB")


def capture_notes_window(output_dir: Path, name: str, rect: WindowRect) -> Image.Image:
    skill_dir = Path(__file__).resolve().parents[1]
    capture_script = skill_dir / "scripts" / "capture_win.ps1"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / name

    if capture_script.exists():
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(capture_script),
                "nlnotes",
                str(output_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if completed.returncode == 0 and output_path.exists():
            return Image.open(output_path).convert("RGB")

    return screenshot_rect(rect)


def screenshot_full() -> Image.Image:
    return ImageGrab.grab().convert("RGB")


def save_debug(image: Image.Image, output_dir: Path, name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    image.save(output_dir / name)


def red_black_counts(image: Image.Image, y: int) -> tuple[int, int, int]:
    red = black = blue = 0
    for yy in range(y, min(y + 20, image.height), 2):
        for x in range(300, min(1030, image.width), 3):
            r, g, b = image.getpixel((x, yy))
            if r > 150 and g < 110 and b < 110:
                red += 1
            elif r < 80 and g < 80 and b < 80:
                black += 1
            elif b > 110 and r < 90:
                blue += 1
    return red, black, blue


def find_first_unread_row(image: Image.Image, scan_start_y: int) -> tuple[int, int, int] | None:
    for y in range(scan_start_y, min(750, image.height - 20), 10):
        red, black, blue = red_black_counts(image, y)
        if red > 120 and red > black * 0.8 and blue < 120:
            return y + 10, red, black
    return None


def wait_for_completion_dialog(timeout: int, output_dir: Path, debug: bool) -> bool:
    # Completion dialog is small and OCR-hostile. The reliable visual invariant is a
    # modal dialog in the middle-bottom area with a single OK button, plus visible
    # Chinese completion text when OCR succeeds. Use OCR if rapidocr helper exists;
    # otherwise save screenshots and fall back to a simple dialog-like pixel check.
    skill_dir = Path(__file__).resolve().parents[1]
    ocr_script = skill_dir / "scripts" / "ocr_screen2.py"
    python_exe = sys.executable

    deadline = time.time() + timeout
    while time.time() < deadline:
        img = screenshot_full()
        if debug:
            save_debug(img, output_dir, "completion_probe.png")

        if ocr_script.exists():
            probe = output_dir / "completion_probe.png"
            text_file = output_dir / "completion_probe.txt"
            output_dir.mkdir(parents=True, exist_ok=True)
            img.save(probe)
            subprocess.run(
                [python_exe, str(ocr_script), str(probe), str(text_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if text_file.exists():
                text = text_file.read_text(encoding="utf-8", errors="replace")
                if any(s in text for s in ("系統已完成", "系统已完成", "完成轉", "完成转", "完成蟹送")):
                    return True

        # Fallback: observed completion dialog lives near x884-1052,y473-621.
        # Require a dense light-gray rectangle and a darker OK button area.
        crop = img.crop((880, 470, 1060, 625))
        light = dark = 0
        for pixel in crop.getdata():
            r, g, b = pixel
            if 215 <= r <= 245 and 215 <= g <= 245 and 215 <= b <= 245:
                light += 1
            if 70 <= r <= 170 and 70 <= g <= 170 and 70 <= b <= 170:
                dark += 1
        if light > 3000 and dark > 200:
            return True

        time.sleep(1)
    return False


def click_completion_ok() -> None:
    click(985, 590)


def click_recipient_dialog(recipient: str) -> None:
    # These coordinates are stable on the target workstation after Notes opens
    # the "Select Names" modal. They select the requested group, add it once,
    # and confirm the dialog. Users can override by running interactively if
    # another workstation uses a materially different DPI/layout.
    if recipient != DEFAULT_RECIPIENT:
        print("WARNING: custom recipient requested; default coordinate selection still assumes the group is visible.")
    click(974, 374)   # group row in the left list
    time.sleep(0.2)
    click(1287, 366)  # Add once
    time.sleep(0.5)
    click(1493, 525)  # OK


def delete_selected_original() -> None:
    press(VK_DELETE)
    time.sleep(0.8)
    # If a delete confirmation appears, Enter accepts the default affirmative
    # button in Notes 9/11. If no dialog appears, Enter is harmless in the list.
    press(VK_RETURN)
    time.sleep(0.8)


def ensure_bysender_tab(rect: WindowRect) -> None:
    # The $BySender tab is usually second tab after Workbench in a clean mailbox.
    click(rect.left + 215, rect.top + 96)
    time.sleep(1)


def process_visible_messages(args: argparse.Namespace) -> int:
    processed = 0
    output_dir = Path(args.output_dir)

    for index in range(args.max_messages):
        _, hwnd, _ = start_notes(args.notes_exe)
        focus_window(hwnd)
        rect = get_window_rect(hwnd)
        image = capture_notes_window(output_dir, f"list_{index:03d}.png", rect)

        row = find_first_unread_row(image, args.scan_start_y)
        if not row:
            print("No visible unread red public-notice rows remain.")
            break

        y, red, black = row
        print(f"Processing row y={y}, red={red}, black={black}")
        if args.dry_run:
            processed += 1
            continue

        click(rect.left + 520, rect.top + y)
        press(VK_RETURN)
        time.sleep(2)

        _, hwnd, _ = start_notes(args.notes_exe)
        focus_window(hwnd)
        rect = get_window_rect(hwnd)
        click(rect.left + 248, rect.top + 120)  # Direct Forward
        time.sleep(1.5)

        click_recipient_dialog(args.recipient)
        if not wait_for_completion_dialog(args.completion_timeout, output_dir, args.debug):
            print("STOP: did not see the completion dialog; original message was not deleted.")
            break

        click_completion_ok()
        time.sleep(0.6)
        processed += 1
        print("  forwarded")

        if args.delete_after_forward:
            _, hwnd, _ = start_notes(args.notes_exe)
            focus_window(hwnd)
            rect = get_window_rect(hwnd)
            ensure_bysender_tab(rect)
            delete_selected_original()
            print("  deleted original")

        if args.restart_every and processed % args.restart_every == 0:
            powershell("Get-Process nlnotes,nnotesmm,notes -ErrorAction SilentlyContinue | Stop-Process -Force")
            time.sleep(4)
            subprocess.Popen([args.notes_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(10)

    return processed


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forward unread HCL Notes public notices and delete originals after verified send.")
    parser.add_argument("--recipient", default=DEFAULT_RECIPIENT, help="Notes group to add in the Select Names dialog.")
    parser.add_argument("--notes-exe", default=DEFAULT_NOTES_EXE, help="Path to notes.exe.")
    parser.add_argument("--max-messages", type=int, default=30, help="Maximum messages to process in one run.")
    parser.add_argument("--restart-every", type=int, default=5, help="Restart Notes after this many successful messages; 0 disables.")
    parser.add_argument("--completion-timeout", type=int, default=14, help="Seconds to wait for the completion dialog.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Debug screenshot/output directory.")
    parser.add_argument("--scan-start-y", type=int, default=220, help="Window-relative y coordinate where row scanning starts.")
    parser.add_argument("--dry-run", action="store_true", help="Detect rows but do not click, send, or delete.")
    parser.add_argument("--debug", action="store_true", help="Save screenshots useful for calibration.")
    parser.add_argument("--no-delete", dest="delete_after_forward", action="store_false", help="Forward only; do not delete originals.")
    parser.set_defaults(delete_after_forward=True)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    processed = process_visible_messages(args)
    print(f"Processed {processed} message(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
