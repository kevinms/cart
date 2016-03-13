import os.path
from random import seed, randrange
import tornado.ioloop
import tornado.web
import sqlite3
import json

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

			# GET    - Get item.
			# PUT    - Update item.
			# POST   - Create item.
			# DELETE - Delete item.
			(r"/list/([0-9]+)/item/([0-9]+)", ItemHandler)
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

		db.commit()

		return db

	def generateTestData(self, db, c):

		c2 = db.cursor()
		c3 = db.cursor()

		c.execute("INSERT INTO list VALUES ('Shopping List')")

		barcodes = [
			('012800517725', 'AA Batteries'),
			('902139032909', 'Nutty Bars'),
			('792828338220', 'Toothpaste'),
			('792828338220', 'Frozen Pizza'),
			('792828338220', 'Milk'),
			('792828338220', 'Kelloggs Fruit and Yogurt'),
			('792828338220', 'Peanut Butter'),
			('792828338220', 'Tomatoes'),
			('792828338220', 'Onions'),
		]

		c.executemany("INSERT INTO barcode VALUES (?,?)", barcodes)

		seed()
		for list_row in c.execute("SELECT ROWID FROM list"):
			list_rowid = list_row["ROWID"]
			for barcode_row in c2.execute("SELECT ROWID FROM barcode"):
				barcode_rowid = barcode_row["ROWID"]
				c3.execute("INSERT INTO item VALUES(?,?,?)", (list_rowid, barcode_rowid, randrange(1,10)))


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

	def encode(self, arg):
		return json.dumps(arg, sort_keys=True, indent=4)

'''
	def prepare(self):
		if self.request.headers["Content-Type"].startswith("application/json"):
			self.json_args = json.loads(self.request.body)
		else:
			self.json_args = None
'''

class MainHandler(BaseHandler):
	def get(self):
		l = List(self.db, 'Shopping List')
		self.render("cart.html", items=l.items)

class ItemHandler(BaseHandler):
	def get(self, listID, itemID):
		r = self.query('''
			SELECT item.ROWID as id, count, code, name
			FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID)
			WHERE fk_list = ? AND item.ROWID = ?
		''', (listID, itemID,), True);
		response = self.encode({'item': r})
		self.write(response)

	def put(self, listID, itemID):
		print self.request.body
		j = json.loads(self.request.body)
		p = j['item']

		if 'count' not in p:
			self.send_error(500)
			return

		r = self.rawQuery('''
			UPDATE item SET count = ? WHERE fk_list = ? AND ROWID = ?
		''', (p['count'], listID, itemID,), True);
		response = self.encode({'msg': 'Item updated.'})
		self.write(response)

	def delete(self, listID, itemID):
		r = self.rawQuery('''
			DELETE FROM item WHERE fk_list = ? AND item.ROWID = ?
		''', (listID, itemID,), True);
		response = self.encode({'msg': 'Item deleted.'})
		self.write(response)

class ListHandler(BaseHandler):
	def get(self, listID=0):
		if listID == 0:
			r = self.query('SELECT ROWID as id, * FROM list');
			response = self.encode({'lists': r})
		else:
			r = self.query('''
				SELECT item.ROWID as id, count, code, name
				FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID)
				WHERE fk_list = ?
			''', (listID,))
			response = self.encode({'items': r})
		self.write(response)

	def delete(self, listID):
		r = self.rawQuery('DELETE FROM list WHERE ROWID = ?', (listID,));
		response = self.encode({'msg': 'List removed.'})
		self.write(response)

def main():
	app = Application()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()
