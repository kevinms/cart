import json
from StringIO import StringIO
import gzip
import httplib, urllib
from lxml import html

# Test Data:
#
# 012800517725 AA Batteries
# 051500240908 Peanut Butter Creamy

def barcodeLookup(code):

	functions = [
		upcdatabase,
		#eansearch,
	]

	for f in functions:
		name = f(code)
		if name is not None:
			return name

	return None

def upcdatabase(code):
	c = httplib.HTTPConnection('www.upcdatabase.com')
	c.request("GET", "/item/" + code)
	r = c.getresponse()
	#print r.status, r.reason
	if r.status != 200:
		return None

	data = r.read()
	tree = html.fromstring(data)
	desc = tree.xpath('//table/tr[td=\'Description\']/td/text()')
	size = tree.xpath('//table/tr[td=\'Size/Weight\']/td/text()')
	print desc, size
	name = desc[1]+' '+size[1]

	return name

# http://www.ean-search.org/perl/ean-search.pl?q=051500240908
def eansearch(code):
	params = urllib.urlencode({'@q': code})
	headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language':'en-US,en;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Connection':'keep-alive',
		'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
		'Upgrade-Insecure-Requests': '1',
		'Connection': 'keep-alive',
		'Referer': 'http://www.ean-search.org/perl/ean-search.pl?q='+code
	}
	c = httplib.HTTPConnection('www.ean-search.org')
	c.request("GET", "/perl/ean-search.pl?q=" + code, None, headers)
	r = c.getresponse()

	print r.status, r.reason
	if r.status != 200:
		return None

	#
	# Decompress GZIP:
	#
	buf = StringIO(r.read())
	f = gzip.GzipFile(fileobj=buf)
	data = f.read()

	print data
	tree = html.fromstring(data)
	failed = tree.xpath('//table[@id=\'eanlist\']')
	print failed

	name = None
	return name


if __name__ == "__main__":
	#eansearch("05150024090892390")
	eansearch("051500240908")
