CREATE TABLE settings (
  key TEXT NOT NULL,
  value TEXT NOT NULL DEFAULT '',
  loadOnStartup BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (key)
);