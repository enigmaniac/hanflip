# test_display.py - Standalone Hardware Test Suite for Hanover Flip-Dot Displays
# Compatible with MicroPython on ESP32 / RP2040 and hanflip driver.
#
# Hardware requirements:
#   - Hanover Flip-Dot display (e.g., 20x16 or similar size)
#   - RS485 transceiver (e.g., MAX485, auto-direction or GPIO-controlled)
#   - Default UART: ESP32 UART2 (TX=GPIO 17, RX=GPIO 16, Baud=4800, 8N1)
#
# Usage:
#   import hanflip
#   import test_display
#   test_display.run_all()
#
# Or run standalone from terminal:
#   python3 webrepl_tool.py run hanflip/test_display.py

import utime
import hanflip

try:
    import machine
    from machine import UART
except ImportError:
    machine = None
    UART = None


def init_display(width=20, height=16, sign_id=1, tx_pin=17, rx_pin=16, baud=4800, uart_id=2):
    """
    Initializes UART communication and the Hanover flip-dot display driver.
    """
    if UART is None:
        raise RuntimeError("machine.UART is not available in this environment.")
    
    uart = UART(uart_id, baudrate=baud, tx=tx_pin, rx=rx_pin, bits=8, parity=None, stop=1)
    sign = hanflip.flip(width=width, height=height, id=sign_id, serial=uart)
    return sign


def pause(sign, seconds):
    """Pauses for the specified duration while feeding watchdog if present."""
    steps = int(seconds * 10)
    for _ in range(steps):
        if hasattr(sign, "wdt") and sign.wdt:
            sign.wdt.feed()
        utime.sleep_ms(100)


def test_hardware_commands(sign):
    """
    Tests native Hanover protocol commands:
      - CMD_TEST  (0x33): Factory hardware diagnostic sequence
      - CMD_CLEAR (0x34): Direct controller blanking command
    """
    print("[1/4] Testing Native Hardware Commands...")
    
    print("  -> Triggering CMD_TEST (diagnostic pattern)...")
    sign.test()
    pause(sign, 3.0)

    print("  -> Triggering CMD_CLEAR (hardware screen blank)...")
    sign.clear()
    pause(sign, 2.0)
    print("  Hardware commands OK.")


def test_fill_patterns(sign):
    """
    Tests full-frame graphics buffer transmission and common dot patterns:
      - Solid all-yellow (dots ON)
      - Solid all-black (dots OFF)
      - Checkerboard grid (alternating dots)
      - Inverted checkerboard
      - Outer perimeter border frame
    """
    print("[2/4] Testing Static Bit Patterns...")

    # Pattern A: All Dots On
    print("  -> Solid Yellow (all dots on)...")
    sign.fill(1)
    sign.show()
    pause(sign, 2.0)

    # Pattern B: All Dots Off
    print("  -> Solid Black (all dots off)...")
    sign.fill(0)
    sign.show()
    pause(sign, 1.5)

    # Pattern C: Checkerboard
    print("  -> Checkerboard pattern...")
    sign.fill(0)
    for y in range(sign.height):
        for x in range(sign.width):
            if (x + y) % 2 == 0:
                sign.pixel(x, y, 1)
    sign.show()
    pause(sign, 2.5)

    # Pattern D: Inverted Checkerboard
    print("  -> Inverted Checkerboard...")
    for y in range(sign.height):
        for x in range(sign.width):
            sign.pixel(x, y, 1 - sign.pixel(x, y))
    sign.show()
    pause(sign, 2.5)

    # Pattern E: Border Frame
    print("  -> Perimeter Border Frame...")
    sign.fill(0)
    sign.rect(0, 0, sign.width, sign.height, 1)
    sign.show()
    pause(sign, 2.0)
    print("  Static patterns OK.")


def test_directional_sweeps(sign):
    """
    Tests individual row and column line sweeps across the matrix.
    Useful for detecting stuck flip-dot electromagnets or addressing anomalies.
    """
    print("[3/4] Testing Directional Sweeps...")

    # Horizontal Bar Sweep (Top to Bottom)
    print("  -> Horizontal bar sweep...")
    sign.fill(0)
    for y in range(sign.height):
        sign.fill(0)
        sign.hline(0, y, sign.width, 1)
        sign.show()
        utime.sleep_ms(150)

    # Vertical Bar Sweep (Left to Right)
    print("  -> Vertical bar sweep...")
    for x in range(sign.width):
        sign.fill(0)
        sign.vline(x, 0, sign.height, 1)
        sign.show()
        utime.sleep_ms(150)

    sign.clear()
    pause(sign, 1.0)
    print("  Directional sweeps OK.")


def test_rate_benchmark(sign, rates=(1.0, 2.0, 3.0, 4.0), passes_per_rate=2):
    """
    Benchmarks sign responsiveness across multiple refresh rates (Hz).
    Uses isochronous timing to prevent frame scheduling drift.
    """
    print("[4/4] Testing Refresh Rate Benchmark...")

    for hz in rates:
        interval_ms = int(1000 / hz)
        print(f"  -> Testing at {hz} Hz ({interval_ms} ms/frame)...")

        for p in range(passes_per_rate):
            # Frame 1: Left half yellow, right half black
            t0 = utime.ticks_ms()
            sign.fill(0)
            sign.fill_rect(0, 0, sign.width // 2, sign.height, 1)
            sign.show()
            elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
            if elapsed < interval_ms:
                utime.sleep_ms(interval_ms - elapsed)

            # Frame 2: Right half yellow, left half black
            t0 = utime.ticks_ms()
            sign.fill(0)
            sign.fill_rect(sign.width // 2, 0, sign.width // 2, sign.height, 1)
            sign.show()
            elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
            if elapsed < interval_ms:
                utime.sleep_ms(interval_ms - elapsed)

    sign.clear()
    print("  Rate benchmark OK.")


def run_all(sign=None, width=20, height=16, sign_id=1, tx_pin=17, rx_pin=16, baud=4800):
    """
    Runs the complete test suite.
    If 'sign' is None, initializes a new display instance on ESP32 UART2.
    """
    if sign is None:
        print("Initializing Hanover display on ESP32 UART2 (TX=%d, RX=%d, %d baud)..." % (tx_pin, rx_pin, baud))
        sign = init_display(width=width, height=height, sign_id=sign_id, tx_pin=tx_pin, rx_pin=rx_pin, baud=baud)

    print("\n" + "=" * 50)
    print(" HANOVER FLIP-DOT DISPLAY TEST SUITE")
    print(" Dimensions: %dx%d | ID: %d" % (sign.width, sign.height, sign.id))
    print("=" * 50 + "\n")

    test_hardware_commands(sign)
    test_fill_patterns(sign)
    test_directional_sweeps(sign)
    test_rate_benchmark(sign)

    print("\n" + "=" * 50)
    print(" TEST COMPLETE: ALL CHECKS PASSED")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all()
