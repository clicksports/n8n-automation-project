CREATE TABLE test_case_execution (
  id VARCHAR(36) NOT NULL,
  testRunId VARCHAR(36) NOT NULL,
  executionId INTEGER,
  status VARCHAR NOT NULL,
  runAt TIMESTAMP,
  completedAt TIMESTAMP,
  errorCode VARCHAR,
  errorDetails TEXT,
  metrics TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);