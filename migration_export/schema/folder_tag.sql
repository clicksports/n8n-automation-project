CREATE TABLE folder_tag (
  folderId VARCHAR(36) NOT NULL,
  tagId VARCHAR(36) NOT NULL,
  PRIMARY KEY (folderId, tagId)
);