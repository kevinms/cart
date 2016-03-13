CREATE TABLE IF NOT EXISTS list (
	name TEXT
);

CREATE TABLE IF NOT EXISTS barcode (
	code TEXT,
	name TEXT
);

CREATE TABLE IF NOT EXISTS item (
	fk_list INTEGER, FOREIGN KEY(fk_list) REFERENCES list(ROWID)
	fk_barcode INTEGER, FOREIGN KEY(fk_barcode) REFERENCES barcode(ROWID))
	count INTEGER,
	UNIQUE(fk_list, fk_barcode)
);
