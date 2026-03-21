-- Migration: Add user_scores table
-- Date: 2026-02-09
-- Description: Creates a table to store user scores for datasets

BEGIN;

-- Create user_scores table
CREATE TABLE IF NOT EXISTS user_scores (
    score_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    dataset_id INTEGER NOT NULL,
    score_date DATE NOT NULL DEFAULT CURRENT_DATE,
    score DECIMAL(10,2) NOT NULL CHECK (score >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id) ON DELETE CASCADE,
    UNIQUE (user_id, dataset_id, score_date)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_scores_user ON user_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_user_scores_dataset ON user_scores(dataset_id);
CREATE INDEX IF NOT EXISTS idx_user_scores_date ON user_scores(score_date);

-- Add comment to table
COMMENT ON TABLE user_scores IS 'Stores user scores for datasets, allowing historical tracking';

COMMIT;