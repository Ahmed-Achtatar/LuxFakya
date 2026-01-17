# LuxFakya

## Database Setup

### Initial Setup
To set up the database for the first time or to reset it to the initial state (WARNING: this deletes existing data):
```bash
python seed.py
```

### Troubleshooting

#### OperationalError: no such column: product.unit
If you encounter an error stating `no such column: product.unit`, it means your database schema is outdated. You can fix this by running the fix script (which preserves your data):

```bash
python fix_db.py
```

Alternatively, running `python seed.py` will also fix the issue but will reset the database and delete all existing data.
