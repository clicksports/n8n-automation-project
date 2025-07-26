CREATE TABLE invalid_auth_token (
  token VARCHAR(512) NOT NULL,
  expiresAt TIMESTAMP NOT NULL,
  PRIMARY KEY (token)
);