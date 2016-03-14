import httplib

#012800517725

while True:
	barcode = raw_input("Enter barcode: ")
	barcode.rstrip()
	url = 'www.upcdatabase.com'
	print url

	c = httplib.HTTPConnection(url)
	c.request("GET", "/item/" + barcode)
	r = c.getresponse()
	print r.status, r.reason
	data = r.read()
	print data

