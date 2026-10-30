# hanflip

MicroPython device driver for **Hanover Displays** flip-dot destination signs over RS485.

The driver inherits from MicroPython's standard [`framebuf.FrameBuffer`](http://docs.micropython.org/en/latest/library/framebuf.html), giving you access to graphics primitives including `pixel()`, `line()`, `hline()`, `vline()`, `rect()`, `fill_rect()`, `text()`, `fill()`, and `blit()`.

---

## Hardware & Wiring

Hanover flip-dot displays communicate over a half-duplex RS485 serial bus at **4800 baud, 8 data bits, no parity, 1 stop bit (8N1)**.

### Pinout (typical ESP32 connection via MAX485)

| MAX485 Module | ESP32 Pin | Hanover Sign (RS485) |
|---|---|---|
| **VCC** | 3.3V or 5V | — |
| **GND** | GND | Common GND |
| **DI** (Driver In) | GPIO 17 (UART2 TX) | — |
| **RO** (Receiver Out) | GPIO 16 (UART2 RX) | — |
| **DE / RE** | Auto-direction or GPIO | — |
| **A (+)** | — | RS485 Data A |
| **B (-)** | — | RS485 Data B |

*Note: Sign ID is set via the rotary address switch on the Hanover display controller board (typically address `1`).*

---

## Quickstart

```python
from machine import UART
import hanflip

# Initialize UART2 at 4800 baud on ESP32
uart = UART(2, baudrate=4800, tx=17, rx=16, bits=8, parity=None, stop=1)

# Initialize display: width=20, height=16, sign_id=1
sign = hanflip.flip(width=20, height=16, id=1, serial=uart)

# Clear display (all dots black)
sign.clear()

# Draw graphics primitives using framebuf
sign.fill(0)
sign.rect(0, 0, 20, 16, 1)          # Outer border
sign.line(2, 2, 17, 13, 1)          # Diagonal line
sign.show()                         # Transmit frame to sign

# Native controller commands
sign.test()                         # Built-in diagnostic test sequence
sign.clear()                        # Hardware blanking command
```

---

## Hardware Test Suite (`test_display.py`)

A standalone hardware test suite is provided in `test_display.py` to verify wiring, serial communication, and electromagnet dot actuation:

### Running on Device

```python
import test_display
test_display.run_all()
```

Or from your host machine over WebREPL / mpremote:

```bash
python3 webrepl_tool.py run hanflip/test_display.py
```

### Tests Included

1. **Hardware Commands:** Exercises `CMD_TEST` (diagnostic flip pattern) and `CMD_CLEAR` (hardware controller blanking).
2. **Static Patterns:** All-on (solid yellow), all-off (solid black), checkerboard, inverted checkerboard, and perimeter border frame.
3. **Directional Sweeps:** Top-to-bottom horizontal scan lines and left-to-right vertical scan lines to diagnose any stuck flip-dot electromagnets.
4. **Rate Benchmark:** Tests display responsiveness and timing stability across 1.0 Hz, 2.0 Hz, 3.0 Hz, and 4.0 Hz refresh rates.

---

## Protocol Reference

Packets are framed as follows:

| Byte | Value | Description |
|---|---|---|
| 0 | `0x02` (STX) | Start of transmission |
| 1 | ASCII Char | Command code (e.g. `'1'` = Image data, `'3'` = Test, `'4'` = Clear) |
| 2.. | ASCII String | Sign physical address (e.g. `'1'`) |
| .. | ASCII Hex | Image payload (length prefix + vertical byte pairs in ASCII hex) |
| .. | `0x03` (ETX) | End of transmission |
| .. | 2 Bytes ASCII | Two-character checksum: `255 - ((2 + id + cmd + payload_sum) % 256)` |
