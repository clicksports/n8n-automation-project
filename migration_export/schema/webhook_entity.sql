CREATE TABLE webhook_entity (
  workflowId VARCHAR(36) NOT NULL,
  webhookPath VARCHAR NOT NULL,
  method VARCHAR NOT NULL,
  node VARCHAR NOT NULL,
  webhookId VARCHAR,
  pathLength INTEGER,
  PRIMARY KEY (webhookPath, method)
);