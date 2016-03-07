import os.path
from random import seed, randrange
import tornado.ioloop
import sqlite3
import tornado.web

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/list", ListHandler),
			(r"/item/([0-9]+)", ItemHandler),
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
		c2 = db.cursor()
		c3 = db.cursor()

		c.execute('CREATE TABLE IF NOT EXISTS list (name TEXT)')
		c.execute('CREATE TABLE IF NOT EXISTS barcode (code TEXT, name TEXT)')
		c.execute('CREATE TABLE IF NOT EXISTS item (fk_list INTEGER, fk_barcode INTEGER, count INTEGER, FOREIGN KEY(fk_list) REFERENCES list(ROWID), FOREIGN KEY(fk_barcode) REFERENCES barcode(ROWID))')

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

		db.commit()

		return db

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
		c.execute('SELECT * FROM item JOIN barcode ON (item.fk_barcode = barcode.ROWID) WHERE fk_list = ?', (rowid,))
		self.items = c.fetchall()
		print self.items[0].keys()

class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

class MainHandler(BaseHandler):
	def get(self):
		l = List(self.db, 'Shopping List')
		self.render("cart.html", items=l.items)

class ItemHandler(BaseHandler):
	def get(self, itemID):
		self.write("item: %s" % itemID)

class ListHandler(BaseHandler):
	def get(self):
		c = self.db.cursor()
		for row in c.execute('SELECT * FROM list'):
			self.write('<p>' + row[0] + '</p>')
			print row
			
		self.write("List")

def main():
	app = Application()
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
	main()
