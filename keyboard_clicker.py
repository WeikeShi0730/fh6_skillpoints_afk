import argparse
import ctypes
import time
from dataclasses import dataclass
from ctypes import wintypes


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_EXTENDEDKEY = 0x0001
SRCCOPY = 0x00CC0020
BI_RGB = 0
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
DEFAULT_TRIGGER_COLOR = (196, 248, 2)


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


class BitmapInfoHeader(ctypes.Structure):
    _fields_ = (
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    )


class RGBQuad(ctypes.Structure):
    _fields_ = (
        ("rgbBlue", wintypes.BYTE),
        ("rgbGreen", wintypes.BYTE),
        ("rgbRed", wintypes.BYTE),
        ("rgbReserved", wintypes.BYTE),
    )


class BitmapInfo(ctypes.Structure):
    _fields_ = (("bmiHeader", BitmapInfoHeader), ("bmiColors", RGBQuad * 1))


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
ctypes.windll.user32.GetSystemMetrics.argtypes = (ctypes.c_int,)
ctypes.windll.user32.GetSystemMetrics.restype = ctypes.c_int
ctypes.windll.gdi32.CreateCompatibleDC.argtypes = (wintypes.HDC,)
ctypes.windll.gdi32.CreateCompatibleDC.restype = wintypes.HDC
ctypes.windll.gdi32.CreateCompatibleBitmap.argtypes = (
    wintypes.HDC,
    ctypes.c_int,
    ctypes.c_int,
)
ctypes.windll.gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
ctypes.windll.gdi32.SelectObject.argtypes = (wintypes.HDC, wintypes.HGDIOBJ)
ctypes.windll.gdi32.SelectObject.restype = wintypes.HGDIOBJ
ctypes.windll.gdi32.BitBlt.argtypes = (
    wintypes.HDC,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HDC,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.DWORD,
)
ctypes.windll.gdi32.BitBlt.restype = wintypes.BOOL
ctypes.windll.gdi32.GetDIBits.argtypes = (
    wintypes.HDC,
    wintypes.HBITMAP,
    wintypes.UINT,
    wintypes.UINT,
    wintypes.LPVOID,
    ctypes.POINTER(BitmapInfo),
    wintypes.UINT,
)
ctypes.windll.gdi32.GetDIBits.restype = ctypes.c_int
ctypes.windll.gdi32.DeleteObject.argtypes = (wintypes.HGDIOBJ,)
ctypes.windll.gdi32.DeleteObject.restype = wintypes.BOOL
ctypes.windll.gdi32.DeleteDC.argtypes = (wintypes.HDC,)
ctypes.windll.gdi32.DeleteDC.restype = wintypes.BOOL


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
    radius: int = 0


@dataclass(frozen=True)
class ColorScanTrigger:
    red: int
    green: int
    blue: int
    tolerance: int
    poll_seconds: float
    timeout_seconds: float
    step: int
    min_matches: int
    area: tuple[float, float, float, float]


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


def read_screen_region_average(x, y, radius):
    if radius <= 0:
        return read_screen_pixel(x, y)

    hdc = ctypes.windll.user32.GetDC(None)
    if not hdc:
        raise ctypes.WinError()
    try:
        red_total = 0
        green_total = 0
        blue_total = 0
        count = 0
        for sample_y in range(y - radius, y + radius + 1):
            for sample_x in range(x - radius, x + radius + 1):
                color_ref = ctypes.windll.gdi32.GetPixel(hdc, sample_x, sample_y)
                if color_ref == 0xFFFFFFFF:
                    continue
                red_total += color_ref & 0xFF
                green_total += (color_ref >> 8) & 0xFF
                blue_total += (color_ref >> 16) & 0xFF
                count += 1

        if count == 0:
            raise RuntimeError("Could not read any pixels in the requested region.")
        return (
            round(red_total / count),
            round(green_total / count),
            round(blue_total / count),
        )
    finally:
        ctypes.windll.user32.ReleaseDC(None, hdc)


def get_virtual_screen_rect():
    left = ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    top = ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    width = ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    return left, top, width, height


def capture_screen_region(left, top, width, height):
    screen_dc = ctypes.windll.user32.GetDC(None)
    if not screen_dc:
        raise ctypes.WinError()

    memory_dc = None
    bitmap = None
    old_object = None
    try:
        memory_dc = ctypes.windll.gdi32.CreateCompatibleDC(screen_dc)
        if not memory_dc:
            raise ctypes.WinError()

        bitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(screen_dc, width, height)
        if not bitmap:
            raise ctypes.WinError()

        old_object = ctypes.windll.gdi32.SelectObject(memory_dc, bitmap)
        if not old_object:
            raise ctypes.WinError()

        if not ctypes.windll.gdi32.BitBlt(
            memory_dc,
            0,
            0,
            width,
            height,
            screen_dc,
            left,
            top,
            SRCCOPY,
        ):
            raise ctypes.WinError()

        bitmap_info = BitmapInfo()
        bitmap_info.bmiHeader.biSize = ctypes.sizeof(BitmapInfoHeader)
        bitmap_info.bmiHeader.biWidth = width
        bitmap_info.bmiHeader.biHeight = -height
        bitmap_info.bmiHeader.biPlanes = 1
        bitmap_info.bmiHeader.biBitCount = 32
        bitmap_info.bmiHeader.biCompression = BI_RGB

        buffer_size = width * height * 4
        buffer = (ctypes.c_ubyte * buffer_size)()
        scan_lines = ctypes.windll.gdi32.GetDIBits(
            memory_dc,
            bitmap,
            0,
            height,
            buffer,
            ctypes.byref(bitmap_info),
            BI_RGB,
        )
        if scan_lines == 0:
            raise ctypes.WinError()

        return buffer, width, height
    finally:
        if old_object and memory_dc:
            ctypes.windll.gdi32.SelectObject(memory_dc, old_object)
        if bitmap:
            ctypes.windll.gdi32.DeleteObject(bitmap)
        if memory_dc:
            ctypes.windll.gdi32.DeleteDC(memory_dc)
        ctypes.windll.user32.ReleaseDC(None, screen_dc)


def pixel_matches(actual, trigger):
    return all(
        abs(actual_value - target_value) <= trigger.tolerance
        for actual_value, target_value in zip(
            actual,
            (trigger.red, trigger.green, trigger.blue),
        )
    )


def color_matches(red, green, blue, trigger):
    return (
        abs(red - trigger.red) <= trigger.tolerance
        and abs(green - trigger.green) <= trigger.tolerance
        and abs(blue - trigger.blue) <= trigger.tolerance
    )


def scan_for_color(trigger):
    screen_left, screen_top, screen_width, screen_height = get_virtual_screen_rect()
    left_ratio, top_ratio, right_ratio, bottom_ratio = trigger.area
    region_left = screen_left + round(screen_width * left_ratio)
    region_top = screen_top + round(screen_height * top_ratio)
    region_right = screen_left + round(screen_width * right_ratio)
    region_bottom = screen_top + round(screen_height * bottom_ratio)
    region_width = max(1, region_right - region_left)
    region_height = max(1, region_bottom - region_top)

    buffer, width, height = capture_screen_region(
        region_left,
        region_top,
        region_width,
        region_height,
    )
    matches = 0
    first_match = None

    for y in range(0, height, trigger.step):
        row_offset = y * width * 4
        for x in range(0, width, trigger.step):
            offset = row_offset + x * 4
            blue = buffer[offset]
            green = buffer[offset + 1]
            red = buffer[offset + 2]
            if color_matches(red, green, blue, trigger):
                matches += 1
                if first_match is None:
                    first_match = (region_left + x, region_top + y)
                if matches >= trigger.min_matches:
                    return first_match, matches

    return first_match, matches


def wait_for_color_scan_trigger(trigger, dry_run=False):
    print(
        "waiting for screen color "
        f"RGB ({trigger.red}, {trigger.green}, {trigger.blue}) "
        f"+/- {trigger.tolerance}",
        flush=True,
    )
    if dry_run:
        return

    started = time.monotonic()
    while True:
        match_position, matches = scan_for_color(trigger)
        if matches >= trigger.min_matches:
            print(
                f"trigger color found near {match_position} "
                f"with {matches} sampled matches",
                flush=True,
            )
            return

        if trigger.timeout_seconds and time.monotonic() - started >= trigger.timeout_seconds:
            raise TimeoutError(
                "Timed out waiting for screen trigger color. "
                f"Found {matches} sampled matches on the last scan."
            )
        time.sleep(trigger.poll_seconds)


def wait_for_trigger(trigger, dry_run=False):
    if isinstance(trigger, ColorScanTrigger):
        wait_for_color_scan_trigger(trigger, dry_run=dry_run)
    else:
        wait_for_pixel_trigger(trigger, dry_run=dry_run)


def wait_for_pixel_trigger(trigger, dry_run=False):
    print(
        "waiting for screen region "
        f"({trigger.x}, {trigger.y}) to match RGB "
        f"({trigger.red}, {trigger.green}, {trigger.blue}) "
        f"+/- {trigger.tolerance}"
        f" with radius {trigger.radius}",
        flush=True,
    )
    if dry_run:
        return

    started = time.monotonic()
    while True:
        actual = read_screen_region_average(trigger.x, trigger.y, trigger.radius)
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
            wait_for_trigger(trigger, dry_run=dry_run)
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
            wait_for_trigger(trigger, dry_run=dry_run)
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
        "--trigger-pixel",
        nargs=5,
        type=int,
        metavar=("X", "Y", "R", "G", "B"),
        help="Wait for a screen pixel to match this RGB color before each loop.",
    )
    parser.add_argument(
        "--no-auto-trigger",
        action="store_true",
        help="Disable the default screen color trigger and run only by timing.",
    )
    parser.add_argument(
        "--trigger-color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Scan the screen for this RGB color before each loop.",
    )
    parser.add_argument(
        "--trigger-tolerance",
        type=int,
        default=12,
        help="Allowed per-channel RGB difference for screen trigger matching.",
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
        default=10.0,
        help="Seconds to wait for the trigger. Use 0 to wait forever.",
    )
    parser.add_argument(
        "--trigger-radius",
        type=int,
        default=0,
        help="Average a square region around --trigger-pixel before matching.",
    )
    parser.add_argument(
        "--trigger-step",
        type=int,
        default=4,
        help="Pixel stride when scanning for the default trigger or --trigger-color.",
    )
    parser.add_argument(
        "--trigger-min-matches",
        type=int,
        default=3,
        help="Number of sampled color matches required for scan triggers.",
    )
    parser.add_argument(
        "--trigger-area",
        nargs=4,
        type=float,
        default=(0.0, 0.0, 1.0, 1.0),
        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
        help="Fractional screen area to scan, for example: 0.25 0.25 0.75 0.75.",
    )
    return parser.parse_args()


def validate_rgb(red, green, blue):
    for value_name, value in (("R", red), ("G", green), ("B", blue)):
        if not 0 <= value <= 255:
            raise ValueError(f"{value_name} must be between 0 and 255.")


def validate_trigger_options(args):
    if args.trigger_tolerance < 0:
        raise ValueError("--trigger-tolerance must be zero or greater.")
    if args.trigger_radius < 0:
        raise ValueError("--trigger-radius must be zero or greater.")
    if args.trigger_poll <= 0:
        raise ValueError("--trigger-poll must be greater than zero.")
    if args.trigger_timeout < 0:
        raise ValueError("--trigger-timeout must be zero or greater.")
    if args.trigger_step <= 0:
        raise ValueError("--trigger-step must be greater than zero.")
    if args.trigger_min_matches <= 0:
        raise ValueError("--trigger-min-matches must be greater than zero.")

    left, top, right, bottom = args.trigger_area
    if not 0.0 <= left < right <= 1.0:
        raise ValueError("--trigger-area LEFT and RIGHT must be between 0 and 1.")
    if not 0.0 <= top < bottom <= 1.0:
        raise ValueError("--trigger-area TOP and BOTTOM must be between 0 and 1.")


def build_trigger(args):
    trigger_count = sum(1 for enabled in (args.trigger_pixel, args.trigger_color) if enabled)
    if args.no_auto_trigger and trigger_count == 0:
        return None
    if args.no_auto_trigger and trigger_count > 0:
        raise ValueError("Do not combine --no-auto-trigger with trigger options.")
    if trigger_count > 1:
        raise ValueError("Use only one of --trigger-pixel or --trigger-color.")

    validate_trigger_options(args)

    if args.trigger_color or not args.trigger_pixel:
        red, green, blue = args.trigger_color or DEFAULT_TRIGGER_COLOR
        validate_rgb(red, green, blue)
        return ColorScanTrigger(
            red=red,
            green=green,
            blue=blue,
            tolerance=args.trigger_tolerance,
            poll_seconds=args.trigger_poll,
            timeout_seconds=args.trigger_timeout,
            step=args.trigger_step,
            min_matches=args.trigger_min_matches,
            area=tuple(args.trigger_area),
        )

    x, y, red, green, blue = args.trigger_pixel
    validate_rgb(red, green, blue)

    return PixelTrigger(
        x=x,
        y=y,
        red=red,
        green=green,
        blue=blue,
        tolerance=args.trigger_tolerance,
        poll_seconds=args.trigger_poll,
        timeout_seconds=args.trigger_timeout,
        radius=args.trigger_radius,
    )


def main():
    args = parse_args()

    if args.hold < 0 or args.gap < 0 or args.start_delay < 0:
        raise ValueError("Timing values must be zero or greater.")
    if args.repeat < 0:
        raise ValueError("--repeat must be 0 or greater.")
    trigger = build_trigger(args)

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
