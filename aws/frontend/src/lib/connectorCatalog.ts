/**
 * APEX Connector & Trigger Catalog — single source of truth for the 70+
 * external systems the platform integrates with.
 *
 * Used by:
 *   • /connectors        — full grid of integration cards
 *   • Playbook detail    — "+ Add Trigger" picker (which sources can fire a run)
 *   • Settings (future)  — bulk-configure
 *
 * Each entry includes:
 *   • A stable id (kebab-case)
 *   • Display name + short tagline
 *   • Category (used to group on the Connectors page)
 *   • Color theme (matches the brand of the system where reasonable)
 *   • Capability flags — { trigger: boolean, action: boolean, sink: boolean }
 *     so the playbook picker only surfaces things that can fire a run.
 *   • A trigger-template hint (cron / webhook / event_bus / etc.) used to
 *     pre-fill the playbook trigger detail field.
 */

export type ConnectorCategory =
  | 'Object Storage'
  | 'File Sharing'
  | 'Streaming & Eventing'
  | 'Databases & CDC'
  | 'Data Warehouses'
  | 'Data Lakes & Lakehouses'
  | 'Email & Messaging'
  | 'Webhooks & APIs'
  | 'Schedule'
  | 'File Transfer'
  | 'Enterprise SaaS'
  | 'ERP'
  | 'CRM'
  | 'HRIS'
  | 'ITSM & Ops'
  | 'Document Repositories'
  | 'Identity & Auth'
  | 'Voice & Contact Center'
  | 'Industrial / OT'
  | 'Financial & Compliance'
  | 'Observability'
  | 'AWS Services'
  | 'Azure Services'
  | 'GCP Services'
  | 'AI / ML Services';

export interface ConnectorEntry {
  id: string;
  name: string;
  tagline: string;
  category: ConnectorCategory;
  /** 2-3 char badge code shown in connector card + trigger pill. */
  code: string;
  /** Background + foreground for the badge. */
  iconBg: string;
  iconColor: string;
  /** Capability flags — what this integration can do in Apex. */
  trigger: boolean;   // can fire a playbook
  action:  boolean;   // can be invoked by an action
  sink:    boolean;   // can receive write-backs
  /** Default trigger type when picked in the playbook picker. */
  triggerType?: 'event_bus' | 's3_event' | 'object_event' | 'webhook'
    | 'cron' | 'cdc_stream' | 'queue' | 'imap' | 'graphql_subscription'
    | 'file_drop' | 'kafka_topic' | 'stream' | 'connector_event';
  /** Example trigger detail string shown in the picker preview. */
  triggerExample?: string;
  /** Default-connected on the Connectors page (live demo). */
  defaultStatus?: 'connected' | 'available' | 'warning';
}

export const CONNECTOR_CATALOG: ConnectorEntry[] = [
  /* ───────────────────── Object Storage ───────────────────── */
  { id: 'aws-s3', name: 'AWS S3', tagline: 'Event-driven object storage', category: 'Object Storage', code: 'S3',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true,
    triggerType: 's3_event', triggerExample: 's3://apex-incoming-*/inbound/**',
    defaultStatus: 'connected' },
  { id: 'azure-blob', name: 'Azure Blob Storage', tagline: 'Containers + Event Grid', category: 'Object Storage', code: 'ABS',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true,
    triggerType: 'object_event', triggerExample: 'eventgrid://blob-created · container=intake',
    defaultStatus: 'connected' },
  { id: 'gcp-cloud-storage', name: 'GCP Cloud Storage', tagline: 'GCS + Pub/Sub notifications', category: 'Object Storage', code: 'GCS',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: true, action: true, sink: true,
    triggerType: 'object_event', triggerExample: 'gs://apex-prod-intake/**',
    defaultStatus: 'connected' },
  { id: 'minio', name: 'MinIO', tagline: 'S3-compatible on-prem object store', category: 'Object Storage', code: 'MIN',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true,
    triggerType: 's3_event', triggerExample: 'minio://onprem.apex.local/intake',
    defaultStatus: 'available' },
  { id: 'wasabi', name: 'Wasabi', tagline: 'Hot cloud object storage', category: 'Object Storage', code: 'WAS',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'backblaze-b2', name: 'Backblaze B2', tagline: 'Low-cost object storage', category: 'Object Storage', code: 'BB2',
    iconBg: '#fef3c7', iconColor: '#b45309',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },

  /* ───────────────────── File Sharing ───────────────────── */
  { id: 'sharepoint', name: 'Microsoft SharePoint', tagline: 'Document libraries + lists', category: 'File Sharing', code: 'SPO',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: true,
    triggerType: 'webhook', triggerExample: 'graph://sites/{site-id}/lists/{list}/items',
    defaultStatus: 'connected' },
  { id: 'box', name: 'Box', tagline: 'Content cloud', category: 'File Sharing', code: 'BOX',
    iconBg: '#dbeafe', iconColor: '#1d4ed8',
    trigger: true, action: true, sink: true,
    triggerType: 'webhook', triggerExample: 'box://folders/{folder-id}/uploads',
    defaultStatus: 'available' },
  { id: 'dropbox', name: 'Dropbox', tagline: 'File sync + sharing', category: 'File Sharing', code: 'DBX',
    iconBg: '#dbeafe', iconColor: '#0061ff',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'google-drive', name: 'Google Drive', tagline: 'Workspace shared drives', category: 'File Sharing', code: 'GDR',
    iconBg: '#ecfdf5', iconColor: '#0f9d58',
    trigger: true, action: true, sink: true,
    triggerType: 'webhook', triggerExample: 'drive://teamdrives/{drive-id}/changes',
    defaultStatus: 'available' },
  { id: 'onedrive', name: 'OneDrive for Business', tagline: 'Microsoft 365 personal + team drives', category: 'File Sharing', code: 'OD1',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'egnyte', name: 'Egnyte', tagline: 'Enterprise content platform', category: 'File Sharing', code: 'EGN',
    iconBg: '#f0fdf4', iconColor: '#15803d',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },

  /* ───────────────────── Streaming & Eventing ───────────────────── */
  { id: 'apache-kafka', name: 'Apache Kafka', tagline: 'Distributed log streaming', category: 'Streaming & Eventing', code: 'KFK',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true,
    triggerType: 'kafka_topic', triggerExample: 'kafka://broker:9092/topic-name',
    defaultStatus: 'connected' },
  { id: 'confluent-cloud', name: 'Confluent Cloud', tagline: 'Managed Kafka', category: 'Streaming & Eventing', code: 'CFC',
    iconBg: '#f5f3ff', iconColor: '#7c3aed',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'aws-kinesis', name: 'AWS Kinesis Data Streams', tagline: 'Real-time shard streams', category: 'Streaming & Eventing', code: 'KDS',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false,
    triggerType: 'stream', triggerExample: 'kinesis://us-east-1/stream/{name}',
    defaultStatus: 'connected' },
  { id: 'aws-eventbridge', name: 'AWS EventBridge', tagline: 'Event bus + rules', category: 'Streaming & Eventing', code: 'EVB',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false,
    triggerType: 'event_bus', triggerExample: 'eventbridge://default/source=apex.intake',
    defaultStatus: 'connected' },
  { id: 'azure-event-hub', name: 'Azure Event Hubs', tagline: 'Big-data streaming', category: 'Streaming & Eventing', code: 'AEH',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'azure-service-bus', name: 'Azure Service Bus', tagline: 'Enterprise messaging queues', category: 'Streaming & Eventing', code: 'ASB',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: false,
    triggerType: 'queue', triggerExample: 'servicebus://ns.servicebus.windows.net/queue',
    defaultStatus: 'available' },
  { id: 'gcp-pubsub', name: 'GCP Pub/Sub', tagline: 'Global event ingestion', category: 'Streaming & Eventing', code: 'PUB',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: true, action: true, sink: false,
    triggerType: 'queue', triggerExample: 'pubsub://projects/{p}/subscriptions/apex-feed',
    defaultStatus: 'connected' },
  { id: 'aws-sqs', name: 'AWS SQS', tagline: 'Managed message queue', category: 'Streaming & Eventing', code: 'SQS',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true,
    triggerType: 'queue', triggerExample: 'sqs://us-east-1/queue/{name}',
    defaultStatus: 'connected' },
  { id: 'rabbitmq', name: 'RabbitMQ', tagline: 'AMQP message broker', category: 'Streaming & Eventing', code: 'RMQ',
    iconBg: '#fff7ed', iconColor: '#ff6600',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },

  /* ───────────────────── Databases & CDC ───────────────────── */
  { id: 'postgres-cdc', name: 'PostgreSQL CDC', tagline: 'Logical replication / wal2json', category: 'Databases & CDC', code: 'PG',
    iconBg: '#dbeafe', iconColor: '#1d4ed8',
    trigger: true, action: true, sink: true,
    triggerType: 'cdc_stream', triggerExample: 'postgres://user@db:5432/apex · slot=apex_repl',
    defaultStatus: 'available' },
  { id: 'mysql-cdc', name: 'MySQL CDC', tagline: 'Binlog change capture', category: 'Databases & CDC', code: 'MYS',
    iconBg: '#dbeafe', iconColor: '#1d4ed8',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'mongodb', name: 'MongoDB Change Streams', tagline: 'Realtime collection events', category: 'Databases & CDC', code: 'MDB',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'dynamodb-streams', name: 'DynamoDB Streams', tagline: 'Item-level change events', category: 'Databases & CDC', code: 'DDS',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true,
    triggerType: 'stream', triggerExample: 'dynamodb-streams://table/{name}',
    defaultStatus: 'connected' },
  { id: 'cosmos-db', name: 'Azure Cosmos DB', tagline: 'Multi-model change feed', category: 'Databases & CDC', code: 'COS',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'oracle-cdc', name: 'Oracle CDC (LogMiner)', tagline: 'Enterprise database capture', category: 'Databases & CDC', code: 'ORA',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'sql-server-cdc', name: 'SQL Server CDC', tagline: 'Microsoft SQL change capture', category: 'Databases & CDC', code: 'MSS',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },

  /* ───────────────────── Data Warehouses & Lakehouses ───────────────────── */
  { id: 'snowflake', name: 'Snowflake', tagline: 'Cloud data platform', category: 'Data Warehouses', code: 'SNW',
    iconBg: '#e0f2fe', iconColor: '#29b5e8',
    trigger: true, action: true, sink: true,
    triggerType: 'cron', triggerExample: 'snowflake://acct/db/schema · poll 5m',
    defaultStatus: 'connected' },
  { id: 'databricks', name: 'Databricks', tagline: 'Lakehouse platform', category: 'Data Lakes & Lakehouses', code: 'DBR',
    iconBg: '#fef2f2', iconColor: '#ff3621',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'bigquery', name: 'BigQuery', tagline: 'Serverless data warehouse', category: 'Data Warehouses', code: 'BQ',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'redshift', name: 'Amazon Redshift', tagline: 'Petabyte-scale warehouse', category: 'Data Warehouses', code: 'RDS',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'azure-synapse', name: 'Azure Synapse', tagline: 'Analytics service', category: 'Data Warehouses', code: 'SYN',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'azure-fabric', name: 'Azure Fabric OneLake', tagline: 'Unified analytics lakehouse', category: 'Data Lakes & Lakehouses', code: 'FAB',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'aws-athena', name: 'Amazon Athena', tagline: 'Federated SQL over S3', category: 'Data Lakes & Lakehouses', code: 'ATH',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },

  /* ───────────────────── Email & Messaging ───────────────────── */
  { id: 'imap', name: 'IMAP mailbox', tagline: 'Email intake via standard IMAP', category: 'Email & Messaging', code: 'IMP',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: false, sink: false,
    triggerType: 'imap', triggerExample: 'imap://mail.acme.com/inbox · poll 60s',
    defaultStatus: 'available' },
  { id: 'outlook-graph', name: 'Outlook (Microsoft Graph)', tagline: 'Microsoft 365 mailbox events', category: 'Email & Messaging', code: 'OUT',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: false,
    triggerType: 'webhook', triggerExample: 'graph://users/{upn}/mailFolders/inbox',
    defaultStatus: 'connected' },
  { id: 'gmail-api', name: 'Gmail API', tagline: 'Google Workspace mailbox push', category: 'Email & Messaging', code: 'GML',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'slack', name: 'Slack', tagline: 'Channels + slash commands', category: 'Email & Messaging', code: 'SLK',
    iconBg: '#f5f3ff', iconColor: '#4a154b',
    trigger: true, action: true, sink: true,
    triggerType: 'webhook', triggerExample: 'slack://workspace/{ws}/channel/{ch}',
    defaultStatus: 'connected' },
  { id: 'msteams', name: 'Microsoft Teams', tagline: 'Channel posts + adaptive cards', category: 'Email & Messaging', code: 'MST',
    iconBg: '#eef2ff', iconColor: '#6264a7',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'twilio-sms', name: 'Twilio SMS', tagline: 'Inbound + outbound SMS', category: 'Email & Messaging', code: 'TWI',
    iconBg: '#fef2f2', iconColor: '#f22f46',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },

  /* ───────────────────── Webhooks & APIs ───────────────────── */
  { id: 'webhook', name: 'Generic Webhook', tagline: 'Any HTTP POST endpoint', category: 'Webhooks & APIs', code: 'WHK',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: false,
    triggerType: 'webhook', triggerExample: 'POST https://apex.example.com/hooks/{playbook-id}',
    defaultStatus: 'connected' },
  { id: 'rest-api-poll', name: 'REST API polling', tagline: 'Periodic GET against any URL', category: 'Webhooks & APIs', code: 'RST',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: false,
    triggerType: 'cron', triggerExample: 'GET https://api.example.com/changes · 5m',
    defaultStatus: 'available' },
  { id: 'graphql-sub', name: 'GraphQL subscription', tagline: 'Live data via subscriptions', category: 'Webhooks & APIs', code: 'GQL',
    iconBg: '#fdf4ff', iconColor: '#a855f7',
    trigger: true, action: true, sink: false,
    triggerType: 'graphql_subscription', triggerExample: 'ws://api.example.com/graphql',
    defaultStatus: 'available' },

  /* ───────────────────── Schedule ───────────────────── */
  { id: 'schedule-cron', name: 'Schedule (cron)', tagline: 'Recurring cron expression', category: 'Schedule', code: 'CRN',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: false, sink: false,
    triggerType: 'cron', triggerExample: '0 6 * * *  · daily 06:00 ET',
    defaultStatus: 'connected' },
  { id: 'aws-scheduler', name: 'AWS EventBridge Scheduler', tagline: 'Managed cron + rate', category: 'Schedule', code: 'SCH',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: false, sink: false, defaultStatus: 'connected' },

  /* ───────────────────── File Transfer ───────────────────── */
  { id: 'sftp', name: 'SFTP / SSH', tagline: 'Secure file transfer protocol', category: 'File Transfer', code: 'SFT',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: true,
    triggerType: 'file_drop', triggerExample: 'sftp://partner.acme.com/inbound/**',
    defaultStatus: 'available' },
  { id: 'ftps', name: 'FTPS', tagline: 'Legacy FTP over TLS', category: 'File Transfer', code: 'FTS',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'as2', name: 'AS2 (EDI)', tagline: 'Drummond-certified EDI exchange', category: 'File Transfer', code: 'AS2',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'aws-transfer-family', name: 'AWS Transfer Family', tagline: 'Managed SFTP/FTPS over S3', category: 'File Transfer', code: 'TRF',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },

  /* ───────────────────── Enterprise SaaS / CRM / ERP / HRIS ───────────────────── */
  { id: 'salesforce', name: 'Salesforce', tagline: 'CRM + platform events', category: 'CRM', code: 'SF',
    iconBg: '#eff6ff', iconColor: '#00a1e0',
    trigger: true, action: true, sink: true,
    triggerType: 'connector_event', triggerExample: 'salesforce://platformEvent/{Event__e}',
    defaultStatus: 'warning' },
  { id: 'dynamics-365', name: 'Dynamics 365', tagline: 'Microsoft Dataverse + CRM', category: 'CRM', code: 'D365',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'hubspot', name: 'HubSpot', tagline: 'Marketing + sales CRM', category: 'CRM', code: 'HUB',
    iconBg: '#fff7ed', iconColor: '#ff7a59',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'sap-s4hana', name: 'SAP S/4HANA', tagline: 'Enterprise ERP via OData', category: 'ERP', code: 'SAP',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: true,
    triggerType: 'connector_event', triggerExample: 'sap://s4.acme.internal/sap/opu/odata/sap/API_*',
    defaultStatus: 'connected' },
  { id: 'oracle-fusion', name: 'Oracle Fusion ERP', tagline: 'Cloud ERP', category: 'ERP', code: 'OFE',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'netsuite', name: 'NetSuite', tagline: 'Mid-market ERP', category: 'ERP', code: 'NS',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'workday', name: 'Workday', tagline: 'HCM + financial management', category: 'HRIS', code: 'WD',
    iconBg: '#fef2f2', iconColor: '#f38b00',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'sap-successfactors', name: 'SAP SuccessFactors', tagline: 'HCM cloud suite', category: 'HRIS', code: 'SF1',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'adp', name: 'ADP Workforce Now', tagline: 'Payroll + HR', category: 'HRIS', code: 'ADP',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },

  /* ───────────────────── ITSM / Ops ───────────────────── */
  { id: 'servicenow', name: 'ServiceNow', tagline: 'ITSM + workflow', category: 'ITSM & Ops', code: 'SVC',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'jira', name: 'Jira', tagline: 'Atlassian issue tracking', category: 'ITSM & Ops', code: 'JRA',
    iconBg: '#eff6ff', iconColor: '#0052cc',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'confluence', name: 'Confluence', tagline: 'Documentation + wiki', category: 'ITSM & Ops', code: 'CFL',
    iconBg: '#eff6ff', iconColor: '#0052cc',
    trigger: false, action: true, sink: true, defaultStatus: 'available' },
  { id: 'pagerduty', name: 'PagerDuty', tagline: 'Incident response', category: 'ITSM & Ops', code: 'PD',
    iconBg: '#f0fdf4', iconColor: '#06ac38',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'opsgenie', name: 'OpsGenie', tagline: 'Alert + on-call', category: 'ITSM & Ops', code: 'OPS',
    iconBg: '#eff6ff', iconColor: '#0052cc',
    trigger: false, action: true, sink: true, defaultStatus: 'available' },

  /* ───────────────────── Document Repositories ───────────────────── */
  { id: 'filenet', name: 'IBM FileNet', tagline: 'Enterprise content mgmt', category: 'Document Repositories', code: 'FNT',
    iconBg: '#eff6ff', iconColor: '#1d4ed8',
    trigger: true, action: true, sink: true,
    triggerType: 'connector_event', triggerExample: 'filenet://cms.acme.internal/object_store/*',
    defaultStatus: 'available' },
  { id: 'opentext', name: 'OpenText Documentum', tagline: 'Enterprise repository', category: 'Document Repositories', code: 'OTX',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'm-files', name: 'M-Files', tagline: 'Metadata-driven content', category: 'Document Repositories', code: 'MFL',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'laserfiche', name: 'Laserfiche', tagline: 'Document + records management', category: 'Document Repositories', code: 'LSF',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'alfresco', name: 'Alfresco', tagline: 'Open-source content services', category: 'Document Repositories', code: 'ALF',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },

  /* ───────────────────── Identity & Auth ───────────────────── */
  { id: 'okta', name: 'Okta', tagline: 'Identity + SSO + lifecycle events', category: 'Identity & Auth', code: 'OKT',
    iconBg: '#eef2ff', iconColor: '#007dc1',
    trigger: true, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'azure-ad', name: 'Microsoft Entra ID', tagline: 'Identity + access mgmt', category: 'Identity & Auth', code: 'EID',
    iconBg: '#eff6ff', iconColor: '#0078d4',
    trigger: true, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-iam-identity', name: 'AWS IAM Identity Center', tagline: 'SSO + role-based access', category: 'Identity & Auth', code: 'IIC',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },

  /* ───────────────────── Voice & Contact Center ───────────────────── */
  { id: 'amazon-connect', name: 'Amazon Connect', tagline: 'Cloud contact center', category: 'Voice & Contact Center', code: 'CNT',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'twilio-voice', name: 'Twilio Flex / Voice', tagline: 'Programmable voice', category: 'Voice & Contact Center', code: 'TWV',
    iconBg: '#fef2f2', iconColor: '#f22f46',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'five9', name: 'Five9', tagline: 'Cloud contact center', category: 'Voice & Contact Center', code: 'FV9',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'webex-contact-center', name: 'Cisco Webex Contact Center', tagline: 'Enterprise contact center', category: 'Voice & Contact Center', code: 'WBX',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },

  /* ───────────────────── Industrial / OT ───────────────────── */
  { id: 'osisoft-pi', name: 'OSIsoft PI System', tagline: 'Plant operations historian', category: 'Industrial / OT', code: 'PI',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false,
    triggerType: 'connector_event', triggerExample: 'pi://historian.plant.local/{tag}',
    defaultStatus: 'connected' },
  { id: 'wonderware', name: 'AVEVA Wonderware', tagline: 'Industrial SCADA', category: 'Industrial / OT', code: 'WND',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'honeywell-phd', name: 'Honeywell PHD', tagline: 'Plant history database', category: 'Industrial / OT', code: 'PHD',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'mqtt', name: 'MQTT broker', tagline: 'IoT pub/sub protocol', category: 'Industrial / OT', code: 'MQT',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: true, defaultStatus: 'available' },
  { id: 'opc-ua', name: 'OPC UA', tagline: 'Industrial interop protocol', category: 'Industrial / OT', code: 'OPC',
    iconBg: '#f3f4f6', iconColor: '#374151',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },

  /* ───────────────────── Financial / Compliance ───────────────────── */
  { id: 'fincen-bsa-efiling', name: 'FinCEN BSA E-Filing', tagline: 'SAR + CTR submission', category: 'Financial & Compliance', code: 'FCN',
    iconBg: '#eff6ff', iconColor: '#1e3a8a',
    trigger: false, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'fiserv-core', name: 'Fiserv Core Banking', tagline: 'Account + transaction events', category: 'Financial & Compliance', code: 'FSV',
    iconBg: '#eff6ff', iconColor: '#1d4ed8',
    trigger: true, action: true, sink: false,
    triggerType: 'connector_event', triggerExample: 'fiserv://core/transaction-events',
    defaultStatus: 'connected' },
  { id: 'jack-henry', name: 'Jack Henry Symitar', tagline: 'Credit-union core banking', category: 'Financial & Compliance', code: 'JHA',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: true, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'encompass-los', name: 'Encompass LOS', tagline: 'Loan origination system', category: 'Financial & Compliance', code: 'ENC',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },
  { id: 'ferc-tariff-feed', name: 'FERC Tariff Feed', tagline: 'Regulated tariff registry', category: 'Financial & Compliance', code: 'FRC',
    iconBg: '#eff6ff', iconColor: '#1e3a8a',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'worldcheck', name: 'WorldCheck One', tagline: 'PEP + sanctions screening', category: 'Financial & Compliance', code: 'WCK',
    iconBg: '#fef2f2', iconColor: '#dc2626',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'chexsystems', name: 'ChexSystems', tagline: 'Account history screening', category: 'Financial & Compliance', code: 'CHX',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },

  /* ───────────────────── Observability ───────────────────── */
  { id: 'datadog', name: 'Datadog', tagline: 'Metrics + logs + alerts', category: 'Observability', code: 'DD',
    iconBg: '#f5f3ff', iconColor: '#774aa4',
    trigger: false, action: true, sink: true, defaultStatus: 'available' },
  { id: 'splunk', name: 'Splunk', tagline: 'Machine data analytics', category: 'Observability', code: 'SPL',
    iconBg: '#f0fdf4', iconColor: '#16a34a',
    trigger: false, action: true, sink: true, defaultStatus: 'available' },
  { id: 'cloudwatch', name: 'AWS CloudWatch', tagline: 'Metrics + alarms', category: 'Observability', code: 'CW',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: true, defaultStatus: 'connected' },

  /* ───────────────────── AWS / Azure / GCP managed services ───────────────────── */
  { id: 'aws-bedrock', name: 'Amazon Bedrock', tagline: 'Managed foundation models', category: 'AWS Services', code: 'BDR',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-bda', name: 'Bedrock Data Automation', tagline: 'Document AI extraction', category: 'AWS Services', code: 'BDA',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-textract', name: 'Amazon Textract', tagline: 'OCR + key-value', category: 'AWS Services', code: 'TXT',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-comprehend', name: 'Amazon Comprehend', tagline: 'NLP + entity recognition', category: 'AWS Services', code: 'CMP',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-sagemaker', name: 'Amazon SageMaker', tagline: 'Custom ML inference', category: 'AI / ML Services', code: 'SM',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-lambda', name: 'AWS Lambda', tagline: 'Serverless compute', category: 'AWS Services', code: 'LMB',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'aws-step-functions', name: 'AWS Step Functions', tagline: 'Workflow orchestration', category: 'AWS Services', code: 'SFN',
    iconBg: '#fff7ed', iconColor: '#ea580c',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'azure-openai', name: 'Azure OpenAI Service', tagline: 'GPT models in Azure', category: 'AI / ML Services', code: 'AOI',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: false, action: true, sink: false, defaultStatus: 'available' },
  { id: 'azure-functions', name: 'Azure Functions', tagline: 'Serverless compute', category: 'Azure Services', code: 'AFN',
    iconBg: '#eef2ff', iconColor: '#4338ca',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'gcp-vertex-ai', name: 'GCP Vertex AI', tagline: 'Unified ML platform', category: 'AI / ML Services', code: 'VTX',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: false, action: true, sink: false, defaultStatus: 'available' },
  { id: 'gcp-cloud-functions', name: 'GCP Cloud Functions', tagline: 'Serverless compute', category: 'GCP Services', code: 'GCF',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: true, action: true, sink: false, defaultStatus: 'available' },
  { id: 'gcp-cloud-run', name: 'GCP Cloud Run', tagline: 'Containerized workloads', category: 'GCP Services', code: 'CRN2',
    iconBg: '#e0f2fe', iconColor: '#0284c7',
    trigger: false, action: true, sink: false, defaultStatus: 'available' },
  { id: 'anthropic-api', name: 'Anthropic API', tagline: 'Claude models', category: 'AI / ML Services', code: 'ANT',
    iconBg: '#fef3c7', iconColor: '#b45309',
    trigger: false, action: true, sink: false, defaultStatus: 'connected' },
  { id: 'openai-api', name: 'OpenAI API', tagline: 'GPT-4 + embeddings', category: 'AI / ML Services', code: 'OAI',
    iconBg: '#ecfdf5', iconColor: '#10a37f',
    trigger: false, action: true, sink: false, defaultStatus: 'available' },
];

export const TOTAL_CONNECTORS = CONNECTOR_CATALOG.length;

/** Trigger-able sources for the playbook picker. */
export const TRIGGER_SOURCES: ConnectorEntry[] = CONNECTOR_CATALOG.filter((c) => c.trigger);

/** Group connectors by category for the connectors page. */
export function groupByCategory(): Record<string, ConnectorEntry[]> {
  const out: Record<string, ConnectorEntry[]> = {};
  for (const c of CONNECTOR_CATALOG) {
    if (!out[c.category]) out[c.category] = [];
    out[c.category].push(c);
  }
  return out;
}

/** Group trigger-eligible sources by category for the playbook picker. */
export function groupTriggersByCategory(): Record<string, ConnectorEntry[]> {
  const out: Record<string, ConnectorEntry[]> = {};
  for (const c of TRIGGER_SOURCES) {
    if (!out[c.category]) out[c.category] = [];
    out[c.category].push(c);
  }
  return out;
}
