CREATE TABLE processed_data (
  workflowId VARCHAR(36) NOT NULL,
  context VARCHAR(255) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  value TEXT NOT NULL,
  PRIMARY KEY (workflowId, context)
);