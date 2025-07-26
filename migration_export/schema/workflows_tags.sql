CREATE TABLE workflows_tags (
  workflowId VARCHAR(36) NOT NULL,
  tagId INTEGER NOT NULL,
  PRIMARY KEY (workflowId, tagId)
);