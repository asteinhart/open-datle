-- Migration script: DuckDB to Neon PostgreSQL
-- Run this script in your Neon database to create the schema

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create datasets_meta table
CREATE TABLE IF NOT EXISTS datasets_meta (
    dataset_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('line', 'order')),
    city VARCHAR(100) NOT NULL,
    subtitle VARCHAR(255),
    y_min DOUBLE PRECISION,
    y_max DOUBLE PRECISION,
    source VARCHAR(500),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create data table
CREATE TABLE IF NOT EXISTS data (
    data_id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL,
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    sort_order INTEGER NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id) ON DELETE CASCADE
);

-- Create index on data table
CREATE INDEX IF NOT EXISTS idx_data_dataset ON data(dataset_id, sort_order);

-- Create schedule table
CREATE TABLE IF NOT EXISTS schedule (
    schedule_id SERIAL PRIMARY KEY,
    day DATE UNIQUE NOT NULL,
    dataset_id INTEGER NOT NULL,
    FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id) ON DELETE CASCADE
);

-- Create index on schedule table
CREATE INDEX IF NOT EXISTS idx_schedule_day ON schedule(day);

-- Create user_guesses table (for storing user line/order guesses)
CREATE TABLE IF NOT EXISTS user_guesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    dataset_id INTEGER NOT NULL,
    guess_data JSONB NOT NULL,
    guess_type VARCHAR(20) NOT NULL CHECK (guess_type IN ('line', 'order')),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id) ON DELETE CASCADE,
    UNIQUE (user_id, dataset_id)
);

-- Create indexes on user_guesses table
CREATE INDEX IF NOT EXISTS idx_user_guesses_user ON user_guesses(user_id);
CREATE INDEX IF NOT EXISTS idx_user_guesses_dataset ON user_guesses(dataset_id);
