import sqlite3
import os

def fix_database():
    # Database path
    db_path = 'instance/luxfakia.db'

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Run 'python seed.py' to create and seed the database.")
        return

    print(f"Checking database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product'")
        if not cursor.fetchone():
            print("Table 'product' does not exist.")
            return

        # Get columns
        cursor.execute("PRAGMA table_info(product)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'unit' not in columns:
            print("Column 'unit' missing. Adding it...")
            # SQLite supports ADD COLUMN.
            # We set a default value 'pcs' because existing rows need a value.
            cursor.execute("ALTER TABLE product ADD COLUMN unit VARCHAR(50) DEFAULT 'pcs' NOT NULL")
            conn.commit()
            print("Column 'unit' added successfully.")
        else:
            print("Column 'unit' already exists.")

        if 'is_hidden' not in columns:
            print("Column 'is_hidden' missing. Adding it...")
            cursor.execute("ALTER TABLE product ADD COLUMN is_hidden BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("Column 'is_hidden' added successfully.")
        else:
            print("Column 'is_hidden' already exists.")

        if 'is_out_of_stock' not in columns:
            print("Column 'is_out_of_stock' missing. Adding it...")
            cursor.execute("ALTER TABLE product ADD COLUMN is_out_of_stock BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("Column 'is_out_of_stock' added successfully.")
        else:
            print("Column 'is_out_of_stock' already exists.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_database()
