import sqlite3
import os
import sys

# Define expected schemas (CREATE TABLE statements)
SCHEMAS = {
    'product': """
CREATE TABLE product (
	id INTEGER NOT NULL,
	name VARCHAR(150) NOT NULL,
	description TEXT,
	price FLOAT NOT NULL,
	unit VARCHAR(50) DEFAULT 'pcs' NOT NULL,
	category_id INTEGER NOT NULL,
	image_url VARCHAR(500),
	is_hidden BOOLEAN DEFAULT 0,
	is_out_of_stock BOOLEAN DEFAULT 0,
	PRIMARY KEY (id),
	FOREIGN KEY(category_id) REFERENCES category (id)
)
""",
    'product_pricing': """
CREATE TABLE product_pricing (
	id INTEGER NOT NULL,
	product_id INTEGER NOT NULL,
	quantity FLOAT NOT NULL,
	price FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(product_id) REFERENCES product (id)
)
""",
    'order': """
CREATE TABLE "order" (
	id INTEGER NOT NULL,
	user_id INTEGER,
	customer_name VARCHAR(150) NOT NULL,
	customer_email VARCHAR(150),
	customer_phone VARCHAR(50),
	customer_address VARCHAR(255),
	customer_city VARCHAR(100),
	total_amount FLOAT NOT NULL,
	status VARCHAR(50) DEFAULT 'Pending',
	created_at DATETIME,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES user (id)
)
""",
    'order_item': """
CREATE TABLE order_item (
	id INTEGER NOT NULL,
	order_id INTEGER NOT NULL,
	product_id INTEGER,
	product_name VARCHAR(150) NOT NULL,
	quantity FLOAT NOT NULL,
	unit VARCHAR(50) NOT NULL,
	price_at_purchase FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(order_id) REFERENCES "order" (id),
	FOREIGN KEY(product_id) REFERENCES product (id) ON DELETE SET NULL
)
"""
}

# Define columns that might be missing and need adding
MISSING_COLUMNS = {
    'product': [
        ('unit', "VARCHAR(50) DEFAULT 'pcs' NOT NULL"),
        ('is_hidden', "BOOLEAN DEFAULT 0 NOT NULL"),
        ('is_out_of_stock', "BOOLEAN DEFAULT 0 NOT NULL")
    ]
}

def get_db_path():
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Check instance folder first
    if os.path.exists('instance/luxfakia.db'):
        return 'instance/luxfakia.db'
    if os.path.exists('luxfakia.db'):
        return 'luxfakia.db'

    return 'instance/luxfakia.db'

def check_and_add_columns(conn, cursor):
    print("Checking for missing columns...")
    for table, columns in MISSING_COLUMNS.items():
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Table '{table}' does not exist. Skipping column checks.")
            continue

        # Quote table name for PRAGMA
        safe_table = f'"{table}"' if table == 'order' else table
        cursor.execute(f"PRAGMA table_info({safe_table})")
        existing_cols = [col[1] for col in cursor.fetchall()]

        for col_name, col_def in columns:
            if col_name not in existing_cols:
                print(f"Column '{col_name}' missing in '{table}'. Adding it...")
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                    print(f"Column '{col_name}' added successfully.")
                except Exception as e:
                    print(f"Error adding column {col_name}: {e}")
            else:
                print(f"Column '{col_name}' already exists in '{table}'.")
    conn.commit()

def ensure_foreign_keys(conn, cursor):
    print("\nChecking foreign keys...")

    tables_to_check = ['product', 'order', 'product_pricing', 'order_item']

    for table_name in tables_to_check:
        print(f"Processing table '{table_name}'...")
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"Table '{table_name}' does not exist. Skipping.")
            continue

        safe_table_name = f'"{table_name}"' if table_name == 'order' else table_name
        cursor.execute(f"PRAGMA foreign_key_list({safe_table_name})")
        fks = cursor.fetchall()

        needs_rebuild = False
        if table_name == 'product' and len(fks) < 1:
            needs_rebuild = True
        elif table_name == 'order' and len(fks) < 1:
            needs_rebuild = True
        elif table_name == 'product_pricing' and len(fks) < 1:
            needs_rebuild = True
        elif table_name == 'order_item' and len(fks) < 2:
            needs_rebuild = True

        if needs_rebuild:
            print(f"Foreign keys missing or incomplete for '{table_name}'. Rebuilding table...")
            rebuild_table(conn, cursor, table_name, SCHEMAS[table_name])
        else:
            print(f"Table '{table_name}' seems to have foreign keys ({len(fks)} found). Skipping rebuild.")

def rebuild_table(conn, cursor, table_name, create_sql):
    try:
        safe_table_name = f'"{table_name}"' if table_name == 'order' else table_name

        cursor.execute(f"PRAGMA table_info({safe_table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        columns_str = ", ".join(columns)

        print(f"  - Disabling foreign keys")
        cursor.execute("PRAGMA foreign_keys=OFF")

        print(f"  - Renaming old table to {table_name}_old")
        cursor.execute(f"ALTER TABLE {safe_table_name} RENAME TO {table_name}_old")

        print(f"  - Creating new table {table_name}")
        cursor.execute(create_sql)

        print(f"  - Copying data")
        cursor.execute(f"INSERT INTO {safe_table_name} ({columns_str}) SELECT {columns_str} FROM {table_name}_old")

        print(f"  - Dropping old table")
        cursor.execute(f"DROP TABLE {table_name}_old")

        conn.commit()

        print(f"  - Re-enabling foreign keys")
        cursor.execute("PRAGMA foreign_keys=ON")

        print(f"Table '{table_name}' rebuilt successfully.")

    except Exception as e:
        print(f"Error rebuilding table {table_name}: {e}")
        conn.rollback()
        print("CRITICAL: Manual intervention might be required.")

def main():
    db_path = get_db_path()
    print(f"Targeting database: {db_path}")

    if not os.path.exists(db_path):
        print("Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    check_and_add_columns(conn, cursor)
    ensure_foreign_keys(conn, cursor)

    conn.close()
    print("Database update complete.")

if __name__ == '__main__':
    main()
