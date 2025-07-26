CREATE TABLE insights_metadata (
  metaId INTEGER NOT NULL,
  workflowId VARCHAR(16),
  projectId VARCHAR(36),
  workflowName VARCHAR(128) NOT NULL,
  projectName VARCHAR(255) NOT NULL,
  PRIMARY KEY (metaId)
);