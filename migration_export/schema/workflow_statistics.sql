CREATE TABLE workflow_statistics (
  count INTEGER DEFAULT 0,
  latestEvent TIMESTAMP,
  name VARCHAR NOT NULL,
  workflowId VARCHAR,
  rootCount INTEGER DEFAULT 0,
  PRIMARY KEY (name, workflowId)
);