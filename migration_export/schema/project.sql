CREATE TABLE project (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(36) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  icon TEXT,
  description VARCHAR,
  PRIMARY KEY (id)
);