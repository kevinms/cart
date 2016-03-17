import os.path
from random import seed, randrange
import tornado.ioloop
import tornado.web
import sqlite3
import json
import lookup

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			# GET    - Serve main webpage.
			(r"/", MainHandler),

			# GET    - Get a list of lists.
			# POST   - Create list.
			(r"/list", ListHandler),

			# GET    - Get list.
			# DELETE - Delete list.
			(r"/list/([0-9]+)", ListHandler),

			# POST   - Create item.
			(r"/list/([0-9]+)/item", ItemHandler),

			# GET    - Get item.
			# PUT    - Update item.
			# DELETE - Delete item.
			(r"/list/([0-9]+)/item/([0-9]+)", ItemHandler),

			# GET    - Get barcode.
			(r"/barcode/(.*)", BarcodeHandler)
		]
		settings = dict(
			#template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)

		super(Application, self).__init__(handlers, **settings)

		self.db = self.initDatabase('list.db')


	def initDatabase(self, name):

		if os.path.isfile(name):
			db = sqlite3.connect(name)
			db.row_factory = sqlite3.Row
			return db

		db = sqlite3.connect(name)
		db.row_factory = sqlite3.Row
		c = db.cursor()

		schema = open('schema.sql', 'r').read()
		c.executescript(schema)

		# For testing purposes only.
		self.generateTestData(db, c)

		self.importPOD_GTINdataset(db, c)

		db.commit()

		return db

	def importPOD_GTINdataset(self, db, c):

		pod = open('data/pod_gtin-pruned.csv', 'r')

		line = pod.readline();
		for line in pod:
			line = unicode(line, "utf-8")

			array = line.split(';')
			if len(array) < 2:
				print "Not enough values:",line
				continue
			gtin = array[0]
			name = array[1]

			if len(gtin) != 13:
				print "GTIN length:",len(gtin),"Line:",line
				continue
			if gtin[0] == '0':
				gtin = gtin[1:]

			if len(name) <= 0:
				print "Name is empty:",line
				continue
			c.execute("INSERT INTO barcode VALUES (?,?)", (gtin, name))

		db.commit()

		print "Finished import of POD GTIN dataset."

	def generateTestData(self, db, c):

		c2 = db.cursor()
		c3 = db.cursor()

		c.execute("INSERT INTO list VALUES ('Shopping List')")

		barcodes = [
			('test-012800517725', 'AA Batteries'),
			('test-792828338220', 'Nutty Bars'),
			('test-792828338221', 'Toothpaste'),
			('test-792828338222', 'Frozen Pizza'),
			('test-792828338223', 'Milk'),
			('test-792828338224', 'Kelloggs Fruit and Yogurt'),
			('test-792828338225', 'Peanut Butter'),
			('test-792828338226', 'Tomatoes'),
			('test-792828338227', 'Onions'),
		]

		c.executemany("INSERT INTO barcode VALUES (?,?)", barcodes)

		seed()
		for list_row in c.execute("SELECT ROWID FROM list"):
			list_rowid = list_row["ROWID"]
			for barcode_row in c2.execute("SELECT ROWID FROM barcode"):
				barcode_rowid = barcode_row["ROWID"]
				c3.execute("INSERT INTO item VALUES(?,?,?,?)", (list_rowid, barcode_rowid, randrange(1,10), 0))

		db.commit()


class List():
	def __init__(self, db, name):
		self.db = db
		self.name = name
		self.items = None
		self.load()

	def load(self):
		c = self.db.cursor()
		c.execute('SELECT ROWID FROM list WHERE name = ?', (self.name,))
		rowid = c.fetchone()['ROWID']
		c.execute('SELECT item.ROWID as id, * FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID) WHERE fk_list = ?', (rowid,))
		self.items = c.fetchall()
		print self.items[0].keys()

class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def query(self, sql, args=(), one=False):
		c = self.db.cursor()
		c.execute(sql, args)
		r = [dict((c.description[i][0], value) for i, value in enumerate(row)) for row in c.fetchall()]
		return (r[0] if r else None) if one else r

	def rawQuery(self, sql, args=(), one=False):
		c = self.db.cursor()
		c.execute(sql, args)
		return c

	def encode(self, arg):
		return json.dumps(arg, sort_keys=True, indent=4)

class MainHandler(BaseHandler):
	def get(self):
		l = List(self.db, 'Shopping List')
		self.render("cart.html", items=l.items)

class BarcodeHandler(BaseHandler):
	def selectBarcode(self, code):
		r = self.query('''
			SELECT ROWID as id, code, name
			FROM barcode WHERE code = ?
		''', (code,), True);
		return r

	def get(self, code):
		#print code
		r = self.selectBarcode(code)

		if r is None:
			name = lookup.getBarcode(code)
			if name is not None:
				self.rawQuery("INSERT OR IGNORE INTO barcode VALUES (?,?)", (code, name))
				r = self.selectBarcode(code)

		if r is None:
			self.send_error(500)
			return

		self.db.commit()

		response = self.encode({'barcode': r})
		#print response
		self.write(response)

class ItemHandler(BaseHandler):
	def get(self, listID, itemID):
		r = self.query('''
			SELECT item.ROWID as id, count, done, code, name
			FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID)
			WHERE fk_list = ? AND item.ROWID = ?
		''', (listID, itemID,), True);
		response = self.encode({'item': r})
		self.write(response)

	def put(self, listID, itemID):
		#print self.request.body
		j = json.loads(self.request.body)
		p = j['item']

		setClause = ''
		args = ()
		if 'done' in p:
			setClause += 'done = ? '
			args += (p['done'],)
		if 'count' in p:
			setClause += ',' if len(setClause) > 0 else ''
			setClause += 'count = ? '
			args += (p['count'],)

		if len(setClause) == 0:
			self.send_error(500)
			return

		r = self.rawQuery(
			'UPDATE item SET ' + setClause + ' WHERE fk_list = ? AND ROWID = ?'
			, args + (listID, itemID,), True);
		self.db.commit()

		response = self.encode({'msg': 'Item updated.'})
		self.write(response)

	def delete(self, listID, itemID):
		r = self.rawQuery('''
			DELETE FROM item WHERE fk_list = ? AND item.ROWID = ?
		''', (listID, itemID,), True);
		self.db.commit()

		response = self.encode({'msg': 'Item deleted.'})
		self.write(response)

	def post(self, listID):
		j = json.loads(self.request.body)['item']
		#print j
		self.rawQuery("INSERT OR IGNORE INTO barcode VALUES (?,?)", (j['code'], j['name']))
		r = self.query('SELECT ROWID as id FROM barcode WHERE code = ?', (j['code'],), True)
		barcodeID = r['id']

		r2 = self.query('''
			SELECT item.ROWID as id, count, done, code, name
			FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID)
			WHERE fk_list = ? AND fk_barcode = ?
		''', (listID, barcodeID,), True);
		self.db.commit()

		if r2 is not None:
			self.set_status(500)
			response = self.encode({'error': 'Item already exists.', 'item': r2})
			return self.finish(response)

		c = self.rawQuery('''
			INSERT INTO item VALUES(?,?,?,?)
		''', (listID, barcodeID, j['count'], j['done']))
		itemID = c.lastrowid
		self.db.commit()

		response = self.encode({'msg': 'Item created.'})
		self.set_header("Location", '/list/' + str(listID) + '/item/' + str(itemID))
		self.write(response)

class ListHandler(BaseHandler):
	def get(self, listID=0):
		if listID == 0:
			r = self.query('SELECT ROWID as id, * FROM list');
			response = self.encode({'lists': r})
		else:
			r = self.query('''
				SELECT item.ROWID as id, count, done, code, name
				FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID)
				WHERE fk_list = ?
			''', (listID,))
			response = self.encode({'items': r})
		self.write(response)

	def delete(self, listID):
		r = self.rawQuery('DELETE FROM list WHERE ROWID = ?', (listID,));
		self.db.commit()

		response = self.encode({'msg': 'List removed.'})
		self.write(response)

def main():
	app = Application()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()
