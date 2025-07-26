-- n8n PostgreSQL Schema
-- Generated from SQLite database

-- Table: migrations
CREATE TABLE migrations (
  id INTEGER NOT NULL,
  timestamp BIGINT NOT NULL,
  name VARCHAR NOT NULL,
  PRIMARY KEY (id)
);

-- Table: settings
CREATE TABLE settings (
  key TEXT NOT NULL,
  value TEXT NOT NULL DEFAULT '',
  loadOnStartup BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (key)
);

-- Table: installed_packages
CREATE TABLE installed_packages (
  packageName CHAR(214) NOT NULL,
  installedVersion CHAR(50) NOT NULL,
  authorName CHAR(70),
  authorEmail CHAR(70),
  createdAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  updatedAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  PRIMARY KEY (packageName)
);

-- Table: installed_nodes
CREATE TABLE installed_nodes (
  name CHAR(200) NOT NULL,
  type CHAR(200) NOT NULL,
  latestVersion INTEGER DEFAULT 1,
  package CHAR(214) NOT NULL,
  PRIMARY KEY (name)
);

-- Table: event_destinations
CREATE TABLE event_destinations (
  id VARCHAR(36) NOT NULL,
  destination TEXT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  updatedAt TIMESTAMP NOT NULL DEFAULT 'STRFTIME(''%Y-%m-%d %H:%M:%f'', ''NOW'')',
  PRIMARY KEY (id)
);

-- Table: auth_identity
CREATE TABLE auth_identity (
  userId VARCHAR,
  providerId VARCHAR NOT NULL,
  providerType VARCHAR NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (providerId, providerType)
);

-- Table: auth_provider_sync_history
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

-- Table: tag_entity
CREATE TABLE tag_entity (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(24) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: workflows_tags
CREATE TABLE workflows_tags (
  workflowId VARCHAR(36) NOT NULL,
  tagId INTEGER NOT NULL,
  PRIMARY KEY (workflowId, tagId)
);

-- Table: workflow_statistics
CREATE TABLE workflow_statistics (
  count INTEGER DEFAULT 0,
  latestEvent TIMESTAMP,
  name VARCHAR NOT NULL,
  workflowId VARCHAR,
  rootCount INTEGER DEFAULT 0,
  PRIMARY KEY (name, workflowId)
);

-- Table: webhook_entity
CREATE TABLE webhook_entity (
  workflowId VARCHAR(36) NOT NULL,
  webhookPath VARCHAR NOT NULL,
  method VARCHAR NOT NULL,
  node VARCHAR NOT NULL,
  webhookId VARCHAR,
  pathLength INTEGER,
  PRIMARY KEY (webhookPath, method)
);

-- Table: variables
CREATE TABLE variables (
  id VARCHAR(36) NOT NULL,
  key TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'string',
  value TEXT,
  PRIMARY KEY (id)
);

-- Table: execution_data
CREATE TABLE execution_data (
  executionId INT NOT NULL,
  workflowData TEXT NOT NULL,
  data TEXT NOT NULL,
  PRIMARY KEY (executionId)
);

-- Table: workflow_history
CREATE TABLE workflow_history (
  versionId VARCHAR(36) NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  authors VARCHAR(255) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  nodes TEXT NOT NULL,
  connections TEXT NOT NULL,
  PRIMARY KEY (versionId)
);

-- Table: credentials_entity
CREATE TABLE credentials_entity (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  data TEXT NOT NULL,
  type VARCHAR(32) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  isManaged BOOLEAN NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
);

-- Table: project_relation
CREATE TABLE project_relation (
  projectId VARCHAR(36) NOT NULL,
  userId VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (projectId, userId)
);

-- Table: shared_credentials
CREATE TABLE shared_credentials (
  credentialsId VARCHAR(36) NOT NULL,
  projectId VARCHAR(36) NOT NULL,
  role TEXT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (credentialsId, projectId)
);

-- Table: shared_workflow
CREATE TABLE shared_workflow (
  workflowId VARCHAR(36) NOT NULL,
  projectId VARCHAR(36) NOT NULL,
  role TEXT NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (workflowId, projectId)
);

-- Table: execution_metadata
CREATE TABLE execution_metadata (
  id INTEGER NOT NULL,
  executionId INTEGER NOT NULL,
  key VARCHAR(255) NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (id)
);

-- Table: invalid_auth_token
CREATE TABLE invalid_auth_token (
  token VARCHAR(512) NOT NULL,
  expiresAt TIMESTAMP NOT NULL,
  PRIMARY KEY (token)
);

-- Table: execution_annotations
CREATE TABLE execution_annotations (
  id INTEGER NOT NULL,
  executionId INTEGER NOT NULL,
  vote VARCHAR(6),
  note TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: annotation_tag_entity
CREATE TABLE annotation_tag_entity (
  id VARCHAR(16) NOT NULL,
  name VARCHAR(24) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: execution_annotation_tags
CREATE TABLE execution_annotation_tags (
  annotationId INTEGER NOT NULL,
  tagId VARCHAR(24) NOT NULL,
  PRIMARY KEY (annotationId, tagId)
);

-- Table: user
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

-- Table: execution_entity
CREATE TABLE execution_entity (
  id INTEGER NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  finished BOOLEAN NOT NULL,
  mode VARCHAR NOT NULL,
  retryOf VARCHAR,
  retrySuccessId VARCHAR,
  startedAt TIMESTAMP,
  stoppedAt TIMESTAMP,
  waitTill TIMESTAMP,
  status VARCHAR NOT NULL,
  deletedAt TIMESTAMP,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: processed_data
CREATE TABLE processed_data (
  workflowId VARCHAR(36) NOT NULL,
  context VARCHAR(255) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  value TEXT NOT NULL,
  PRIMARY KEY (workflowId, context)
);

-- Table: project
CREATE TABLE project (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(36) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  icon TEXT,
  description VARCHAR,
  PRIMARY KEY (id)
);

-- Table: folder
CREATE TABLE folder (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  parentFolderId VARCHAR(36),
  projectId VARCHAR(36) NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: folder_tag
CREATE TABLE folder_tag (
  folderId VARCHAR(36) NOT NULL,
  tagId VARCHAR(36) NOT NULL,
  PRIMARY KEY (folderId, tagId)
);

-- Table: workflow_entity
CREATE TABLE workflow_entity (
  id VARCHAR(36) NOT NULL,
  name VARCHAR(128) NOT NULL,
  active BOOLEAN NOT NULL,
  nodes TEXT,
  connections TEXT,
  settings TEXT,
  staticData TEXT,
  pinData TEXT,
  versionId VARCHAR(36),
  triggerCount INTEGER DEFAULT 0,
  meta TEXT,
  parentFolderId VARCHAR(36),
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  isArchived BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id)
);

-- Table: insights_metadata
CREATE TABLE insights_metadata (
  metaId INTEGER NOT NULL,
  workflowId VARCHAR(16),
  projectId VARCHAR(36),
  workflowName VARCHAR(128) NOT NULL,
  projectName VARCHAR(255) NOT NULL,
  PRIMARY KEY (metaId)
);

-- Table: insights_raw
CREATE TABLE insights_raw (
  id INTEGER NOT NULL,
  metaId INTEGER NOT NULL,
  type INTEGER NOT NULL,
  value INTEGER NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

-- Table: insights_by_period
CREATE TABLE insights_by_period (
  id INTEGER NOT NULL,
  metaId INTEGER NOT NULL,
  type INTEGER NOT NULL,
  value INTEGER NOT NULL,
  periodUnit INTEGER NOT NULL,
  periodStart TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

-- Table: user_api_keys
CREATE TABLE user_api_keys (
  id VARCHAR(36) NOT NULL,
  userId VARCHAR NOT NULL,
  label VARCHAR(100) NOT NULL,
  apiKey VARCHAR NOT NULL,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  scopes TEXT,
  PRIMARY KEY (id)
);

-- Table: test_run
CREATE TABLE test_run (
  id VARCHAR(36) NOT NULL,
  workflowId VARCHAR(36) NOT NULL,
  status VARCHAR NOT NULL,
  errorCode VARCHAR,
  errorDetails TEXT,
  runAt TIMESTAMP,
  completedAt TIMESTAMP,
  metrics TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

-- Table: test_case_execution
CREATE TABLE test_case_execution (
  id VARCHAR(36) NOT NULL,
  testRunId VARCHAR(36) NOT NULL,
  executionId INTEGER,
  status VARCHAR NOT NULL,
  runAt TIMESTAMP,
  completedAt TIMESTAMP,
  errorCode VARCHAR,
  errorDetails TEXT,
  metrics TEXT,
  createdAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  updatedAt TIMESTAMP NOT NULL DEFAULT STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
  PRIMARY KEY (id)
);

