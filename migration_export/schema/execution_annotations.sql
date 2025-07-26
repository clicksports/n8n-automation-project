CREATE TABLE execution_annotations (
  id INTEGER NOT NULL,
  executionId INTEGER NOT NULL,
  vote VARCHAR(6),
  note TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);