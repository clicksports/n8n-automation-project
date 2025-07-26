CREATE TABLE execution_entity (
  id INTEGER NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  finished BOOLEAN NOT NULL,
  mode VARCHAR NOT NULL,
  retryOf VARCHAR,
  retrySuccessId VARCHAR,
  startedAt TIMESTAMP,
  stoppedAt TIMESTAMP,
  waitTill TIMESTAMP,
  status VARCHAR NOT NULL,
  deletedAt TIMESTAMP,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);