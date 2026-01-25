# LuxFakya

## Database Setup

### Initial Setup
To set up the database for the first time or to ensure the admin user and default categories exist:
```bash
python seed.py
```
*Note: This script checks if the admin user exists and creates it if missing. It does NOT delete existing data.*

### Troubleshooting

#### OperationalError: no such column: product.unit
If you encounter an error stating `no such column: product.unit`, it means your database schema is outdated. You can fix this by running the fix script (which preserves your data):

```bash
python fix_db.py
```

Alternatively, running `python seed.py` will ensure default data exists, but `fix_db.py` is recommended for schema updates.
