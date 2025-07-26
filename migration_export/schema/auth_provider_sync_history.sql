CREATE TABLE auth_provider_sync_history (
  id INTEGER,
  providerType VARCHAR NOT NULL,
  runMode TEXT NOT NULL,
  status TEXT NOT NULL,
  startedAt TIMESTAMP NOT NULL,
  endedAt TIMESTAMP NOT NULL,
  scanned INTEGER NOT NULL,
  created INTEGER NOT NULL,
  updated INTEGER NOT NULL,
  disabled INTEGER NOT NULL,
  error TEXT,
  PRIMARY KEY (id)
);