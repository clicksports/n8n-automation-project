CREATE TABLE event_destinations (
  id VARCHAR(36) NOT NULL,
  destination TEXT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  updatedAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  PRIMARY KEY (id)
);