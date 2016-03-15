import json
import httplib
from lxml import html

#012800517725

name = ''


"""
http://www.ean-search.org/
www.upcdatabase.com
http://pod.opendatasoft.com/explore/dataset/pod_gtin
http://product-open-data.com/download/
"""

while True:
	barcode = raw_input("Enter barcode: ")
	barcode.rstrip()

	c = httplib.HTTPConnection('localhost:8888')
	c.request("GET", "/barcode/" + barcode)
	r = c.getresponse()

	#
	# Do a lookup if not cached.
	#
	if r.status != 200:
		c = httplib.HTTPConnection('www.upcdatabase.com')
		c.request("GET", "/item/" + barcode)
		r = c.getresponse()
		#print r.status, r.reason
		if r.status != 200:
			continue

		data = r.read()
		tree = html.fromstring(data)
		desc = tree.xpath('//table/tr[td=\'Description\']/td/text()')
		size = tree.xpath('//table/tr[td=\'Size/Weight\']/td/text()')
		print desc, size
		name = desc[1]+' '+size[1]

	else:
		resp = r.read()
		print resp
		data = json.loads(resp)['barcode']
		name = data['name']

	#
	# Insert new item.
	#
	item = {
		'item': {
			'code': barcode,
			'name': name,
			'count': 1,
			'done': 0
		}
	}
	body = json.dumps(item, sort_keys=True, indent=4)
	print body

	c = httplib.HTTPConnection('localhost:8888')
	c.request("POST", "/list/1/item", body)
	r = c.getresponse()

	print r.status, r.reason
	if r.status == 200:
		continue

	#
	# Update existing item.
	#
	resp = r.read()
	print resp
	data = json.loads(resp)
	if data['error'] == "Item already exists.":
		item = {
			'item': {
				'count': data['item']['count'] + 1,
				'done': 0
			}
		}
		body = json.dumps(item, sort_keys=True, indent=4)
		c = httplib.HTTPConnection('localhost:8888')
		c.request("PUT", "/list/1/item/" + str(data['item']['id']), body)
		r = c.getresponse()
		print r.status, r.reason
