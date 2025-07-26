CREATE TABLE test_run (
  id VARCHAR(36) NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  status VARCHAR NOT NULL,
  errorCode VARCHAR,
  errorDetails TEXT,
  runAt TIMESTAMP,
  completedAt TIMESTAMP,
  metrics TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);