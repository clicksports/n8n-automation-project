CREATE TABLE workflow_entity (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  active BOOLEAN NOT NULL,
  nodes TEXT,
  connections TEXT,
  settings TEXT,
  staticData TEXT,
  pinData TEXT,
  versionId VARCHAR(36),
  triggerCount INTEGER DEFAULT 0,
  meta TEXT,
  parentFolderId VARCHAR(36),
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  isArchived BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id)
);