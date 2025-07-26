CREATE TABLE user (
  id VARCHAR,
  email VARCHAR,
  firstName VARCHAR,
  lastName VARCHAR,
  password TEXT,
  personalizationAnswers TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  settings TEXT,
  disabled BOOLEAN NOT NULL DEFAULT FALSE,
  mfaEnabled BOOLEAN NOT NULL DEFAULT FALSE,
  mfaSecret TEXT,
  mfaRecoveryCodes TEXT,
  role TEXT NOT NULL,
  lastActiveAt DATE,
  PRIMARY KEY (id)
);