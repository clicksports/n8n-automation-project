CREATE TABLE project_relation (
  projectId VARCHAR(36) NOT NULL,
  userId VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (projectId, userId)
);