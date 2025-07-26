CREATE TABLE installed_nodes (
  name CHAR(200) NOT NULL,
  type CHAR(200) NOT NULL,
  latestVersion INTEGER DEFAULT 1,
  package CHAR(214) NOT NULL,
  PRIMARY KEY (name)
);