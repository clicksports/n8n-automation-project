CREATE TABLE workflow_history (
  versionId VARCHAR(36) NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  authors VARCHAR(255) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  nodes TEXT NOT NULL,
  connections TEXT NOT NULL,
  PRIMARY KEY (versionId)
);