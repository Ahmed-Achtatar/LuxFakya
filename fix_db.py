import sqlite3
import os
import sys

def fix_database():
    # Database path
    db_path = 'instance/luxfakia.db'

# Define columns that might be missing and need adding
# Note: FALSE is compatible with both SQLite (as 0) and PostgreSQL (as boolean)
MISSING_COLUMNS = {
    'product': [
        ('unit', "VARCHAR(50) DEFAULT 'pcs' NOT NULL"),
        ('is_hidden', "BOOLEAN DEFAULT FALSE NOT NULL"),
        ('is_out_of_stock', "BOOLEAN DEFAULT FALSE NOT NULL")
    ],
    'category': [
        ('image_url', "VARCHAR(500)")
    ],
    'product_pricing': [
        ('display_unit', "VARCHAR(20) DEFAULT 'Kg'")
    ],
    'user': [
        ('can_manage_orders', "BOOLEAN DEFAULT FALSE NOT NULL"),
        ('can_manage_products', "BOOLEAN DEFAULT FALSE NOT NULL"),
        ('can_manage_users', "BOOLEAN DEFAULT FALSE NOT NULL"),
        ('can_manage_content', "BOOLEAN DEFAULT FALSE NOT NULL")
    ]
}

# Placeholder for table schemas if full rebuild is needed (currently unused/incomplete)
SCHEMAS = {}

def get_default_sqlite_path():
    # Check instance folder first
    if os.path.exists('instance/luxfakia.db'):
        return 'instance/luxfakia.db'
    if os.path.exists('luxfakia.db'):
        return 'luxfakia.db'
    return 'instance/luxfakia.db'

def fix_sqlite(db_path):
    print(f"Targeting SQLite database: {db_path}")
    if not os.path.exists(db_path):
        print("Database file not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    check_and_add_columns_sqlite(conn, cursor)
    ensure_foreign_keys_sqlite(conn, cursor)

    conn.close()
    print("SQLite update complete.")

def check_and_add_columns_sqlite(conn, cursor):
    print("Checking for missing columns (SQLite)...")
    for table, columns in MISSING_COLUMNS.items():
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Table '{table}' does not exist. Skipping column checks.")
            continue

        safe_table = f'"{table}"' if table in ['order', 'user'] else table
        cursor.execute(f"PRAGMA table_info({safe_table})")
        existing_cols = [col[1] for col in cursor.fetchall()]

        for col_name, col_def in columns:
            if col_name not in existing_cols:
                print(f"Column '{col_name}' missing in '{table}'. Adding it...")
                try:
                    cursor.execute(f"ALTER TABLE {safe_table} ADD COLUMN {col_name} {col_def}")
                    print(f"Column '{col_name}' added successfully.")
                except Exception as e:
                    print(f"Error adding column {col_name}: {e}")
            else:
                print(f"Column '{col_name}' already exists in '{table}'.")
    conn.commit()

def ensure_foreign_keys_sqlite(conn, cursor):
    print("\nChecking foreign keys (SQLite)...")
    tables_to_check = ['product', 'order', 'product_pricing', 'order_item']

    for table_name in tables_to_check:
        print(f"Processing table '{table_name}'...")
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"Table '{table_name}' does not exist. Skipping.")
            continue

        safe_table_name = f'"{table_name}"' if table_name in ['order', 'user'] else table_name
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
            if table_name in SCHEMAS:
                print(f"Foreign keys missing or incomplete for '{table_name}'. Rebuilding table...")
                rebuild_table_sqlite(conn, cursor, table_name, SCHEMAS[table_name])
            else:
                print(f"Foreign keys missing for '{table_name}', but no schema definition found. Skipping rebuild.")
        else:
            print(f"Table '{table_name}' seems to have foreign keys ({len(fks)} found). Skipping rebuild.")

def rebuild_table_sqlite(conn, cursor, table_name, create_sql):
    try:
        # Not fully implemented for all tables, but preserved for existing logic
        safe_table_name = f'"{table_name}"' if table_name in ['order', 'user'] else table_name

        # Get columns
        cursor.execute("PRAGMA table_info(product)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'unit' not in columns:
            print("Column 'unit' missing. Adding it...")
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
        print(f"Error rebuilding table {table_name}: {e}")
        conn.rollback()
        print("CRITICAL: Manual intervention might be required.")

def fix_postgres(db_url):
    print("Detected PostgreSQL database.")

    try:
        import psycopg2
    except ImportError:
        print("Error: psycopg2 module not found. Please install requirements.txt.")
        return

    # Fix postgres:// schema if necessary
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()

        check_and_add_columns_postgres(conn, cursor)
        ensure_foreign_keys_postgres(conn, cursor)

        conn.close()
        print("PostgreSQL update complete.")
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")

def check_and_add_columns_postgres(conn, cursor):
    print("Checking for missing columns (PostgreSQL)...")

    for table, columns in MISSING_COLUMNS.items():
        # Check if table exists
        # to_regclass handles unquoted identifiers by lowercasing them, so 'user' matches 'user' or '"user"' table
        cursor.execute("SELECT to_regclass(%s)", (table,))
        if not cursor.fetchone()[0]:
             print(f"Table '{table}' does not exist. Skipping.")
             continue

        # Get existing columns
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table,))
        existing_cols = [row[0] for row in cursor.fetchall()]

        safe_table = f'"{table}"' if table in ['order', 'user'] else table

        for col_name, col_def in columns:
            if col_name not in existing_cols:
                print(f"Column '{col_name}' missing in '{table}'. Adding it...")
                try:
                    cursor.execute(f"ALTER TABLE {safe_table} ADD COLUMN {col_name} {col_def}")
                    print(f"Column '{col_name}' added successfully.")
                except Exception as e:
                     print(f"Error adding column {col_name}: {e}")
            else:
                 print(f"Column '{col_name}' already exists.")

def ensure_foreign_keys_postgres(conn, cursor):
    print("\nChecking foreign keys (PostgreSQL)...")

    # Map table to expected FK definitions (target_table, column)
    expected_fks = {
        'product': [('category_id', 'category', 'id')],
        'product_pricing': [('product_id', 'product', 'id')],
        'order': [('user_id', '"user"', 'id')],
        'order_item': [
             ('order_id', '"order"', 'id'),
             ('product_id', 'product', 'id')
        ]
    }

    for table, fks in expected_fks.items():
        # Check if table exists
        cursor.execute("SELECT to_regclass(%s)", (table if table != 'order' else '"order"',))
        if not cursor.fetchone()[0]:
             continue

        print(f"Checking table '{table}'...")

        # Get existing constraints
        cursor.execute("""
            SELECT kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
        """, (table,))

        existing_constraints = cursor.fetchall() # list of (col, fk_table, fk_col)

        safe_table = f'"{table}"' if table in ['order', 'user'] else table

        for col, target_table, target_col in fks:
            # Handle "order" and "user" quoting in logic for target table check
            target_table_clean = target_table.replace('"', '')

            found = False
            for ex_col, ex_table, ex_target_col in existing_constraints:
                if ex_col == col and ex_table == target_table_clean and ex_target_col == target_col:
                    found = True
                    break

            if not found:
                print(f"Missing FK on {table}.{col} -> {target_table}.{target_col}. Adding...")
                constraint_name = f"fk_{table}_{col}"

                alter_sql = f"""
                    ALTER TABLE {safe_table}
                    ADD CONSTRAINT {constraint_name}
                    FOREIGN KEY ({col}) REFERENCES {target_table} ({target_col})
                """

                if table == 'order_item' and col == 'product_id':
                    alter_sql += " ON DELETE SET NULL"

                try:
                    cursor.execute(alter_sql)
                    print(f"Constraint {constraint_name} added.")
                except Exception as e:
                    print(f"Error adding constraint: {e}")
            else:
                print(f"FK on {table}.{col} exists.")

def run_db_fix(db_uri):
    """
    Analyzes the DB URI and runs the appropriate fix function.
    """
    if not db_uri:
        # Default to SQLite if no URI provided
        fix_sqlite(get_default_sqlite_path())
        return

    if db_uri.startswith('postgres'):
        fix_postgres(db_uri)
    elif db_uri.startswith('sqlite:'):
        # Extract path from sqlite:///path/to/db
        # Handle sqlite:/// (3 slashes) for relative/absolute paths
        if db_uri.startswith('sqlite:///'):
            path = db_uri[10:] # remove sqlite:///
        elif db_uri.startswith('sqlite://'):
             path = db_uri[9:]
        else:
             path = db_uri[7:]

        # If path is empty (e.g. in-memory sqlite:///:memory: or just sqlite://)
        if not path or path == ':memory:':
            print("Skipping fix for in-memory SQLite database.")
            return

        fix_sqlite(path)
    else:
        # Fallback: Treat as a file path (for backward compatibility with direct path args)
        fix_sqlite(db_uri)

def main():
    arg_path = sys.argv[1] if len(sys.argv) > 1 else None

    if arg_path:
        # Explicit path provided, treat as URI or file path
        run_db_fix(arg_path)
    else:
        # Use env var
        run_db_fix(os.environ.get('DATABASE_URL'))

if __name__ == '__main__':
    main()
