#! /usr/bin/python
import sys
import struct
import time

scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r',
    20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n',
    50: u'm', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 55: u'CAPS', 56: u'LALT', 100: u'RALT'
}

capscodes = {
    0: None, 1: u'ESC', 2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*',
    10: u'(', 11: u')', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':',
    40: u'\'', 41: u'~', 42: u'LSHFT', 43: u'|', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u'<', 52: u'>', 53: u'?', 54: u'RSHFT', 55: u'CAPS', 56: u'LALT', 100: u'RALT'
}

#long int, long int, unsigned short, unsigned short, unsigned int
eventFormat = 'llHHI'
eventSize = struct.calcsize(eventFormat)

kb = open('/dev/input/' + sys.argv[1], 'rb')

caps=False

while True:
	event = kb.read(eventSize)
	(tv_sec, tv_usec, etype, code, value) = struct.unpack(eventFormat, event)

	# Skip everything except key events.
	if etype != 1:
		continue

	# Caps lock.
	if code == 42 or code == 54:
		caps = False if value == 0 else True
		continue
	if code == 55 and value != 0:
		caps = not caps
		continue

	# Skip release events.
	if value == 0:
		continue

	# Skip some specific non-character codes.
	if code in (1,14,15,28,29,42,54,56,100):
		continue

	table = capscodes if caps else scancodes

	if code not in table:
		continue
		print("Event type %u, code %u, value %u at %d.%d" % \
			(etype, code, value, tv_sec, tv_usec))

	key = table[code]
	sys.stdout.write(key)
	sys.stdout.flush()

kb.close()
