CREATE TABLE IF NOT EXISTS list (
	name TEXT
);

CREATE TABLE IF NOT EXISTS barcode (
	code TEXT,
	name TEXT
);

CREATE TABLE IF NOT EXISTS item (
	fk_list INTEGER,
	fk_barcode INTEGER,
	count INTEGER,
	FOREIGN KEY(fk_list) REFERENCES list(ROWID),
	FOREIGN KEY(fk_barcode) REFERENCES barcode(ROWID)
);
