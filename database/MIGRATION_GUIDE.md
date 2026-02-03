# Migration from DuckDB to Neon PostgreSQL

## Overview

This guide walks through migrating your Open Datle database from DuckDB to Neon PostgreSQL.

## Prerequisites

- Neon account with project created
- DATABASE_URL configured in `app/.env`
- Python with packages: `duckdb`, `psycopg2-binary`, `python-dotenv`

## Migration Steps

### 1. Install Python Dependencies

```bash
cd database
pip install duckdb psycopg2-binary python-dotenv
```

### 2. Create Schema in Neon

Run the SQL migration script in your Neon database console or using psql:

```bash
psql $DATABASE_URL -f migrate_to_neon.sql
```

Or copy the contents of `migrate_to_neon.sql` and run it in the Neon SQL Editor.

### 3. Export Data from DuckDB

```bash
python export_from_duckdb.py
```

This creates JSON files in `database/export/`:

- `users.json`
- `datasets_meta.json`
- `data.json`
- `schedule.json`

### 4. Import Data to Neon

```bash
python import_to_neon.py
```

This reads the JSON files and loads them into your Neon database.

### 5. Verify Migration

Check that data was imported correctly:

```bash
# Connect to Neon
psql $DATABASE_URL

# Run verification queries
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM datasets_meta;
SELECT COUNT(*) FROM data;
SELECT COUNT(*) FROM schedule;
```

### 6. Test API Endpoints

Start your development server:

```bash
cd ../app
npm run dev
```

Test the endpoints:

- http://localhost:5173 - Main game
- http://localhost:5173/test-db - Database connection test
- http://localhost:5173/?id=1 - Load dataset #1

## API Changes

All API endpoints have been updated to use Neon PostgreSQL:

### Dataset API (`/api/v1/dataset`)

- **GET**: Fetch dataset by ID
- **POST**: Create new dataset
- **DELETE**: Delete dataset

### Guess APIs

- **POST** `/api/v1/guess/line`: Submit line guess
- **POST** `/api/v1/guess/order`: Submit order guess

## Schema Differences

### DuckDB → PostgreSQL Changes

1. **Sequences → SERIAL**
   - DuckDB: `CREATE SEQUENCE seq_user_id`
   - PostgreSQL: `user_id SERIAL PRIMARY KEY`

2. **Data Types**
   - `DOUBLE` → `DOUBLE PRECISION`
   - `VARCHAR` → `VARCHAR(length)`
   - `JSON` → `JSONB`

3. **Foreign Key Cascades**
   - Added `ON DELETE CASCADE` for cleaner data deletion

4. **User Guesses Table**
   - New unified table for both line and order guesses
   - Uses `guess_type` field to differentiate
   - Stores guess data in JSONB format

## Rollback Plan

If you need to rollback:

1. Keep your DuckDB file: `database/open_datle.db`
2. Revert API changes: `git checkout HEAD -- app/src/routes/api`
3. Restore DuckDB imports in API files

## Performance Notes

- PostgreSQL uses connection pooling (handled by `@neondatabase/serverless`)
- Neon auto-scales and auto-suspends (cost-efficient)
- JSONB indexes can be added for faster guess queries if needed

## Troubleshooting

### Connection Issues

- Verify `DATABASE_URL` in `.env`
- Check Neon project is not suspended
- Ensure WebSocket polyfill is installed (`ws` package)

### Data Import Errors

- Check JSON files in `database/export/`
- Verify schema was created first
- Check for constraint violations in logs

### API Errors

- Check browser console for frontend errors
- Check server logs for backend errors
- Verify database connection with `/test-db` route
