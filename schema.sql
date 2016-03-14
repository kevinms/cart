CREATE TABLE IF NOT EXISTS list (
	name TEXT
);

CREATE TABLE IF NOT EXISTS barcode (
	code TEXT,
	name TEXT,
	UNIQUE(code)
);

CREATE TABLE IF NOT EXISTS item (
	fk_list INTEGER,
	fk_barcode INTEGER,
	count INTEGER DEFAULT 1,
	done INTEGER DEFAULT 0,
	FOREIGN KEY(fk_list) REFERENCES list(ROWID),
	FOREIGN KEY(fk_barcode) REFERENCES barcode(ROWID),
	UNIQUE(fk_list, fk_barcode)
);
