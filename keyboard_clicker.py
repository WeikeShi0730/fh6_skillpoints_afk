import argparse
import ctypes
import time
from dataclasses import dataclass
from ctypes import wintypes


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001


SCAN_CODES = {
    "esc": 0x01,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0A,
    "0": 0x0B,
    "q": 0x10,
    "w": 0x11,
    "e": 0x12,
    "r": 0x13,
    "t": 0x14,
    "y": 0x15,
    "u": 0x16,
    "i": 0x17,
    "o": 0x18,
    "p": 0x19,
    "a": 0x1E,
    "s": 0x1F,
    "d": 0x20,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    "z": 0x2C,
    "x": 0x2D,
    "c": 0x2E,
    "v": 0x2F,
    "b": 0x30,
    "n": 0x31,
    "m": 0x32,
    "space": 0x39,
    "enter": 0x1C,
    "tab": 0x0F,
    "shift": 0x2A,
    "ctrl": 0x1D,
    "alt": 0x38,
    "up": 0x48,
    "left": 0x4B,
    "right": 0x4D,
    "down": 0x50,
}

EXTENDED_KEYS = {"up", "left", "right", "down"}
ULONG_PTR = wintypes.WPARAM


class MouseInput(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class KeyboardInput(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class HardwareInput(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )


class InputUnion(ctypes.Union):
    _fields_ = (
        ("mi", MouseInput),
        ("ki", KeyboardInput),
        ("hi", HardwareInput),
    )


class Input(ctypes.Structure):
    _fields_ = (("type", wintypes.DWORD), ("union", InputUnion))


ctypes.windll.user32.SendInput.argtypes = (
    wintypes.UINT,
    ctypes.POINTER(Input),
    ctypes.c_int,
)
ctypes.windll.user32.SendInput.restype = wintypes.UINT
ctypes.windll.user32.GetDC.argtypes = (wintypes.HWND,)
ctypes.windll.user32.GetDC.restype = wintypes.HDC
ctypes.windll.user32.ReleaseDC.argtypes = (wintypes.HWND, wintypes.HDC)
ctypes.windll.user32.ReleaseDC.restype = ctypes.c_int
ctypes.windll.gdi32.GetPixel.argtypes = (wintypes.HDC, ctypes.c_int, ctypes.c_int)
ctypes.windll.gdi32.GetPixel.restype = wintypes.COLORREF
ctypes.windll.user32.GetCursorPos.argtypes = (ctypes.POINTER(wintypes.POINT),)
ctypes.windll.user32.GetCursorPos.restype = wintypes.BOOL


@dataclass(frozen=True)
class PixelTrigger:
    x: int
    y: int
    red: int
    green: int
    blue: int
    tolerance: int
    poll_seconds: float
    timeout_seconds: float


def _send_scan_code(scan_code, key_up=False, extended=False):
    flags = KEYEVENTF_SCANCODE
    if key_up:
        flags |= KEYEVENTF_KEYUP
    if extended:
        flags |= KEYEVENTF_EXTENDEDKEY

    event = Input(
        type=INPUT_KEYBOARD,
        union=InputUnion(ki=KeyboardInput(0, scan_code, flags, 0, 0)),
    )
    sent = ctypes.windll.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(event))
    if sent != 1:
        raise ctypes.WinError()


def press_key(key, hold_seconds, dry_run=False):
    key = key.lower()
    if key not in SCAN_CODES:
        supported = ", ".join(sorted(SCAN_CODES))
        raise ValueError(f"Unsupported key '{key}'. Supported keys: {supported}")

    print(f"pressing {key.upper()} for {hold_seconds:.2f}s", flush=True)
    if dry_run:
        return

    scan_code = SCAN_CODES[key]
    extended = key in EXTENDED_KEYS
    _send_scan_code(scan_code, key_up=False, extended=extended)
    time.sleep(hold_seconds)
    _send_scan_code(scan_code, key_up=True, extended=extended)


def sleep_or_print(seconds, dry_run=False):
    print(f"sleeping for {seconds:.2f}s", flush=True)
    if dry_run:
        return
    time.sleep(seconds)


def read_screen_pixel(x, y):
    hdc = ctypes.windll.user32.GetDC(None)
    if not hdc:
        raise ctypes.WinError()
    try:
        color_ref = ctypes.windll.gdi32.GetPixel(hdc, x, y)
        if color_ref == 0xFFFFFFFF:
            raise ctypes.WinError()
        return color_ref & 0xFF, (color_ref >> 8) & 0xFF, (color_ref >> 16) & 0xFF
    finally:
        ctypes.windll.user32.ReleaseDC(None, hdc)


def read_cursor_pixel():
    point = wintypes.POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(point)):
        raise ctypes.WinError()
    red, green, blue = read_screen_pixel(point.x, point.y)
    print(f"cursor at ({point.x}, {point.y}) has RGB ({red}, {green}, {blue})")


def pixel_matches(actual, trigger):
    return all(
        abs(actual_value - target_value) <= trigger.tolerance
        for actual_value, target_value in zip(
            actual,
            (trigger.red, trigger.green, trigger.blue),
        )
    )


def wait_for_pixel_trigger(trigger, dry_run=False):
    print(
        "waiting for screen pixel "
        f"({trigger.x}, {trigger.y}) to match RGB "
        f"({trigger.red}, {trigger.green}, {trigger.blue}) "
        f"+/- {trigger.tolerance}",
        flush=True,
    )
    if dry_run:
        return

    started = time.monotonic()
    while True:
        actual = read_screen_pixel(trigger.x, trigger.y)
        if pixel_matches(actual, trigger):
            print(f"trigger matched with RGB {actual}", flush=True)
            return

        if trigger.timeout_seconds and time.monotonic() - started >= trigger.timeout_seconds:
            raise TimeoutError(
                "Timed out waiting for screen trigger. "
                f"Last RGB at ({trigger.x}, {trigger.y}) was {actual}."
            )
        time.sleep(trigger.poll_seconds)


def run_sequence(keys, hold_seconds, gap_seconds, repeat_count, trigger=None, dry_run=False):
    completed = 0
    while repeat_count == 0 or completed < repeat_count:
        if trigger:
            wait_for_pixel_trigger(trigger, dry_run=dry_run)
        print(f"loop {completed + 1} started", flush=True)
        for key in keys:
            press_key(key, hold_seconds, dry_run=dry_run)
            sleep_or_print(gap_seconds, dry_run=dry_run)
        print(f"loop {completed + 1} completed", flush=True)
        completed += 1


def run_game_loop(repeat_count, trigger=None, dry_run=False):
    completed = 0
    while repeat_count == 0 or completed < repeat_count:
        if trigger:
            wait_for_pixel_trigger(trigger, dry_run=dry_run)
        print(f"loop {completed + 1} started", flush=True)
        press_key("enter", 0.08, dry_run=dry_run)
        sleep_or_print(4.0, dry_run=dry_run)
        press_key("w", 26.0, dry_run=dry_run)
        sleep_or_print(7.0, dry_run=dry_run)
        press_key("x", 0.08, dry_run=dry_run)
        sleep_or_print(1.0, dry_run=dry_run)
        press_key("enter", 0.08, dry_run=dry_run)
        sleep_or_print(7.0, dry_run=dry_run)
        print(f"loop {completed + 1} completed", flush=True)
        completed += 1


def parse_args():
    parser = argparse.ArgumentParser(
        description="Press a configurable keyboard sequence using Windows SendInput."
    )
    parser.add_argument(
        "--preset",
        choices=["game-loop", "custom"],
        default="game-loop",

        help="Use the built-in game loop or a custom --keys sequence.",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        default=["w"],
        help="Keys to press in order, for example: --keys w space 1",
    )
    parser.add_argument(
        "--hold",
        type=float,
        default=0.08,
        help="Seconds to hold each key down.",
    )
    parser.add_argument(
        "--gap",
        type=float,
        default=0.25,
        help="Seconds to wait between key presses.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=0,
        help="Number of times to run the sequence. Use 0 to repeat until Ctrl+C.",
    )
    parser.add_argument(
        "--start-delay",
        type=float,
        default=5.0,
        help="Seconds to wait before the first key press so you can focus the game.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without pressing keys.",
    )
    parser.add_argument(
        "--sample-cursor",
        action="store_true",
        help="Print the cursor screen position and RGB color, then exit.",
    )
    parser.add_argument(
        "--trigger-pixel",
        nargs=5,
        type=int,
        metavar=("X", "Y", "R", "G", "B"),
        help="Wait for a screen pixel to match this RGB color before each loop.",
    )
    parser.add_argument(
        "--trigger-tolerance",
        type=int,
        default=8,
        help="Allowed per-channel RGB difference for --trigger-pixel.",
    )
    parser.add_argument(
        "--trigger-poll",
        type=float,
        default=0.1,
        help="Seconds between screen trigger checks.",
    )
    parser.add_argument(
        "--trigger-timeout",
        type=float,
        default=0.0,
        help="Seconds to wait for the trigger. Use 0 to wait forever.",
    )
    return parser.parse_args()


def build_pixel_trigger(args):
    if not args.trigger_pixel:
        return None

    x, y, red, green, blue = args.trigger_pixel
    for value_name, value in (("R", red), ("G", green), ("B", blue)):
        if not 0 <= value <= 255:
            raise ValueError(f"{value_name} must be between 0 and 255.")
    if args.trigger_tolerance < 0:
        raise ValueError("--trigger-tolerance must be zero or greater.")
    if args.trigger_poll <= 0:
        raise ValueError("--trigger-poll must be greater than zero.")
    if args.trigger_timeout < 0:
        raise ValueError("--trigger-timeout must be zero or greater.")

    return PixelTrigger(
        x=x,
        y=y,
        red=red,
        green=green,
        blue=blue,
        tolerance=args.trigger_tolerance,
        poll_seconds=args.trigger_poll,
        timeout_seconds=args.trigger_timeout,
    )


def main():
    args = parse_args()

    if args.sample_cursor:
        read_cursor_pixel()
        return

    if args.hold < 0 or args.gap < 0 or args.start_delay < 0:
        raise ValueError("Timing values must be zero or greater.")
    if args.repeat < 0:
        raise ValueError("--repeat must be 0 or greater.")
    trigger = build_pixel_trigger(args)

    print(f"Starting in {args.start_delay:.1f}s. Focus the game window now.")
    print("Press Ctrl+C in this terminal to stop.")
    time.sleep(args.start_delay)

    try:
        if args.preset == "game-loop":
            run_game_loop(args.repeat, trigger=trigger, dry_run=args.dry_run)
        else:
            run_sequence(
                args.keys,
                args.hold,
                args.gap,
                args.repeat,
                trigger=trigger,
                dry_run=args.dry_run,
            )
    except TimeoutError as error:
        print(f"\n{error}")
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
