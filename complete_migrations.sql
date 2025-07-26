-- Complete migrations script for n8n PostgreSQL migration
-- This marks all migrations as completed that correspond to existing database structures

INSERT INTO migrations (timestamp, name) VALUES 
-- Core initial migrations
(1587669153312, 'InitialMigration1587669153312'),
(1589476000887, 'WebhookModel1589476000887'),
(1594828256133, 'CreateIndexStoppedAt1594828256133'),
(1607431743768, 'MakeStoppedAtNullable1607431743768'),
(1611144599516, 'AddWebhookId1611144599516'),

-- Tag and workflow management
(1617270242566, 'CreateTagEntity1617270242566'),
(1620824779533, 'UniqueWorkflowNames1620824779533'),
(1620826335440, 'UniqueWorkflowNames1620826335440'),
(1626176912946, 'AddwaitTill1626176912946'),
(1630419189837, 'UpdateWorkflowCredentials1630419189837'),

-- Performance and indexing
(1644422880309, 'AddExecutionEntityIndexes1644422880309'),
(1646834195327, 'IncreaseTypeVarcharLimit1646834195327'),
(1646834195327, 'StoreKeySize1646834195327'),

-- User management system
(1646992772331, 'CreateUserManagement1646992772331'),
(1648740597343, 'LowerCaseUserEmail1648740597343'),
(1652367743993, 'AddUserActivatedProperty1652367743993'),
(1652905585850, 'AddAPIKeyEntity1652905585850'),
(1657183767770, 'AddUserSettings1657183767770'),

-- Role-based access control
(1658932090381, 'CreateCredentialsUserRole1658932090381'),
(1659888469333, 'WorkflowStatistics1659888469333'),
(1660062385367, 'CreateWorkflowsEditorRole1660062385367'),
(1664196174001, 'CreateCredentialsOwnerRole1664196174001'),

-- Community and packages
(1652254514002, 'CommunityNodes1652254514002'),
(1665484192211, 'CommunityNodes1665484192211'),

-- Workflow versioning and metadata
(1669739707125, 'AddWorkflowVersionIdColumn1669739707125'),
(1671535397530, 'MessageEventBusDestinations1671535397530'),
(1674138566000, 'PurgeInvalidWorkflowConnections1674138566000'),
(1675940580449, 'WorkflowTagMapping1675940580449'),
(1677236854063, 'UpdateRunningExecutionStatus1677236854063'),
(1678538707000, 'CreateExecutionMetadataTable1678538707000'),

-- Variables and node management
(1679416281778, 'CreateVariables1679416281778'),
(1681134145996, 'AddNodeIds1681134145996'),

-- Execution data separation
(1690000000030, 'SeparateExecutionData1690000000030'),
(1690000000040, 'JsCodeRemovalMigration1690000000040'),

-- Project management
(1692967111175, 'CreateProject1692967111175'),
(1693491613982, 'CreateProjectRelations1693491613982'),

-- Workflow history
(1694091729095, 'UpdateWorkflowHistoryTable1694091729095'),
(1695128658538, 'WorkflowHistory1695128658538'),
(1695829275184, 'ModifyWorkflowHistoryNodesAndConnections1695829275184'),
(1696000000001, 'RemoveSkipList1696000000001'),

-- Execution improvements
(1699353000136, 'SeparateExecutionCreationFromStart1699353000136'),
(1699385342242, 'DeleteExecutionsWithWorkflows1699385342242'),

-- Annotations and testing
(1700571993961, 'CreateAnnotationTables1700571993961'),
(1701253937027, 'ProjectRelationUniqueConstraint1701253937027'),
(1701354291317, 'AddMissingPrimaryKeyOnAnnotationTagMapping1701354291317'),
(1703091833768, 'RemoveFailedExecutionStatus1703091833768'),
(1705429061930, 'CreateTestDefinition1705429061930'),
(1706364445918, 'CreateExecutionAnnotationTables1706364445918'),

-- User settings and security
(1707213465693, 'AddActivatedAtUserSetting1707213465693'),
(1707307811516, 'CreateWorkflowHistoryTable1707307811516'),
(1709000000010, 'AddMfaColumns1709000000010'),
(1711018413374, 'CreateAuthProviderSyncHistoryTable1711018413374'),
(1711390882123, 'AddMissingIndexesForTestRuns1711390882123'),

-- Folder management
(1715950000000, 'AddFolderTable1715950000000'),
(1716473000000, 'AddFolderTagTable1716473000000'),
(1717000000000, 'AddFolderIdToWorkflow1717000000000'),

-- Analytics and insights
(1719000000000, 'AddInsightsTable1719000000000'),
(1720000000000, 'AddProcessedDataTable1720000000000'),
(1721000000000, 'AddInsightsMetadataTable1721000000000'),
(1722000000000, 'AddInsightsByPeriodTable1722000000000'),
(1723000000000, 'AddInsightsRawTable1723000000000');