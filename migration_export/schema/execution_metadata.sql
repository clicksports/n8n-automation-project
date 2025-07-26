CREATE TABLE execution_metadata (
  id INTEGER NOT NULL,
  executionId INTEGER NOT NULL,
  key VARCHAR(255) NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (id)
);