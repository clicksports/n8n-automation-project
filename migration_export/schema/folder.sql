CREATE TABLE folder (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  parentFolderId VARCHAR(36),
  projectId VARCHAR(36) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);