CREATE TABLE shared_workflow (
  workflowId VARCHAR(36) NOT NULL,
  projectId VARCHAR(36) NOT NULL,
  role TEXT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (workflowId, projectId)
);