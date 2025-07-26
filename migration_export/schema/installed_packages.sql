CREATE TABLE installed_packages (
  packageName CHAR(214) NOT NULL,
  installedVersion CHAR(50) NOT NULL,
  authorName CHAR(70),
  authorEmail CHAR(70),
  createdAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  updatedAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  PRIMARY KEY (packageName)
);