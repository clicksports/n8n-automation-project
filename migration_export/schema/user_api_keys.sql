CREATE TABLE user_api_keys (
  id VARCHAR(36) NOT NULL,
  userId VARCHAR NOT NULL,
  label VARCHAR(100) NOT NULL,
  apiKey VARCHAR NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  scopes TEXT,
  PRIMARY KEY (id)
);