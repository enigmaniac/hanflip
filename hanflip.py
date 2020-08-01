
# MicroPython Hanover Flipdot driver over RS485

from micropython import const
import framebuf

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
# id: hardware address of sign (set using selector in sign)
# serial: pointer to a serial stream object, eg uart

#Constants for commands

CMD_TEST = const(0x33)
CMD_CLEAR = const(0x34)
CMD_IMG = const(0x31)
CMD_ECHO = const(0x32)
CMD_ASCII = const(0x36)


class hanflip(framebuf.FrameBuffer):
    def __init__(self, width, height, id, serial): 
        self.width = width
        self.height = height
        self.id = id #physical ID of the sign
		self.serial = serial #Serial object to write data to, eg UART
        self.pages = (self.height // 8) + 1
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        self.show()

    def clear(self):
        self.write_cmd(CMD_CLEAR)

    def test(self):
        self.write_cmd(CMD_TEST)
		
    def echo(self):
        self.write_cmd(CMD_ECHO)

    def show(self):
        self.write_data(self.buffer)
		
	def write_cmd(self, cmd)
		check = self.checksum(cmd)
		req = bytearray.fromhex("02 3" + self.id) #Initial string is ASCII 02 [STX] + Code of ID, shortcut using 30 + id as hex text
		req.append(cmd)
		req.append(0x03)
		req.append(self._checksum(cmd)
		print(req.hex(" ")
		serial.write(req)
		
	def write_data(self, buf)
		print("To implement")
	
	# Write a preformatted string, resetting ID if needed
	def write_preform(self, hex)
		print("To implement")
		
	def _checksum(self, cmd, payload=[0])
		checksum = 255 - ((2 + self.id.ord() + cmd + payload.sum())%256)
		print(checksum)
		return checksum


