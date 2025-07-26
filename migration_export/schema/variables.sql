CREATE TABLE variables (
  id VARCHAR(36) NOT NULL,
  key TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'string',
  value TEXT,
  PRIMARY KEY (id)
);