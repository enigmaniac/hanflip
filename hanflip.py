
# MicroPython Hanover Flipdot driver over RS485

from micropython import const
import framebuf
import ubinascii

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

def hexme(ba):
	return "".join("%02x " % i for i in ba)

class flip(framebuf.FrameBuffer):
	def __init__(self, width, height, id, serial): 
		self.width = width
		self.lame = 0
		self.height = height
		self.id = id #physical ID of the sign
		self.serial = serial #Serial object to write data to, eg UART
		self.pages = (self.height // 8) + 1
		self.buffer = bytearray(self.pages * self.width)
		super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
		self.init_display()

	def init_display(self):
		print("display initialized")

	def clear(self):
		self.write_cmd(CMD_CLEAR)

	def test(self):
		self.write_cmd(CMD_TEST)
		
	def echo(self):
		self.write_cmd(CMD_ECHO)

	def show(self):
		self.write_data(self.buffer)
		
	def write_cmd(self, cmd):
		check = self.checksum(cmd)
		req = bytearray(b'\x02')
		req.append(cmd)
		req.extend(str(self.id))
		req.append(0x03)
		req.extend(self.checksum(cmd))
		print(hexme(req))
		#serial.write(req)
		
	def write_data(self, buf):
		print("To implement")
	
	# Write a preformatted string, resetting ID if needed
	def write_preform(self, hex):
		print("To implement")
		
	def checksum(self, cmd):
		payload= bytearray()
		check = 255 - ((2 + ord(str(self.id)) + cmd + sum(payload))%256)
		print("%0.2X" % check) #Checksum is actually passed as the ascii characters of the hex checksum. So we take the checksum, and convert to hex characters
		return "%0.2X" % check


