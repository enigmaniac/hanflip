
# MicroPython Hanover Flipdot driver over RS485

from micropython import const
import framebuf
import ubinascii

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html

# id: hardware address of sign (set using selector in sign)
# serial: pointer to a serial stream object, eg uart
# Uart config: 	baud: 4800, data bits: 8, Parity: NONE, stop bits: 1

#Constants for commands

CMD_TEST = const(0x33)
CMD_CLEAR = const(0x34)
CMD_IMG = const(0x31)
CMD_ECHO = const(0x32)
CMD_ASCII = const(0x36)

def hexme(ba, delim = " "):
	f = "%02X" + delim
	return "".join(f % i for i in ba)

class flip(framebuf.FrameBuffer):
	def __init__(self, width, height, id, serial): 
		self.width = width
		self.lame = 0
		self.height = height
		self.id = id #physical ID of the sign
		self.debug = False
		self.serial = serial #Serial object to write data to, eg UART
		self.pages = (self.height // 8)
		self.buffer = bytearray(self.pages * self.width)
		super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
		self.init_display()

	def init_display(self):
		print("display initialized")
	
	def debug(self):
		self.debug = True

	def clear(self):
		self.fill(0)
		self.write_cmd(CMD_CLEAR)

	def test(self):
		self.write_cmd(CMD_TEST)
		
	def echo(self):
		self.write_cmd(CMD_ECHO)

	def show(self):
		self.write_data(self.buffer)
		
	def showtext(self, text):
		#Not working (?)
		self.write_cmd(CMD_ASCII, bytearray(text))
		
	def write_cmd(self, cmd, payload = bytearray()):
		check = self.checksum(cmd, payload)
		req = bytearray(b'\x02') #start with a 0x02
		req.append(cmd) #Command (as ASCII number)
		req.extend(str(self.id)) #Sign ID (as ASCII number)
		req.extend(payload)
		req.append(0x03) #Closure
		req.extend(check) #Checksum
		if(self.debug): print(hexme(req))
		self.serial.write(req)
		
	def write_data(self, payload):
		if(self.debug): print(payload)		
		#Split and recombine , since framebuf writes the full width of 8 vertical pixels, followed by next row of 8 vertical pixels. Hanflip expects 2 bytes of vertical pixels
		payload = bytearray(a for b in zip(payload[0:len(payload)//2], payload[-len(payload)//2:len(payload)]) for a in b)
		#                              interweave    1st row of 8 px    2nd row of 8 px                        flatten
		payload = bytearray(hexme(payload, "")) #Convert bytes to ASCII hex representation (hanflip uses ASCII chars for hex)
		payload = bytearray("%0.2X" % (self.width * self.height // 8)) + payload #prepend size of display, formatted to hex
		if(self.debug): print(payload)
		self.write_cmd(CMD_IMG, payload)
		print("Screen refreshing")
		
	
	# Write a preformatted string, resetting ID if needed
	def write_preform(self, hex):
		print("To implement")
		
	def checksum(self, cmd, payload=bytearray()):
		if(self.debug): print(payload)
		check = 255 - ((2 + ord(str(self.id)) + cmd + sum(payload))%256)
		if(self.debug): print("%0.2X" % check) #Checksum is actually passed as the ascii characters of the hex checksum. So we take the checksum, and convert to hex characters
		return "%0.2X" % check


