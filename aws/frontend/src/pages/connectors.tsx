/**
 * Data Connectors Page - Manage integrations and data sources
 */

import React, { useState } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Button, Badge } from '@/components/common';
import {
  CircleStackIcon,
  CloudIcon,
  ServerIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  PlusIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  Cog6ToothIcon,
  TrashIcon,
  LinkIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

interface Connector {
  id: string;
  name: string;
  type: string;
  provider: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync?: string;
  config: Record<string, string>;
  icon: any;
  description: string;
}

export default function Connectors() {
  const [selectedConnector, setSelectedConnector] = useState<Connector | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const connectors: Connector[] = [
    {
      id: 's3',
      name: 'Amazon S3',
      type: 'Storage',
      provider: 'AWS',
      status: 'connected',
      lastSync: '2 minutes ago',
      config: { bucket: 'apex-documents-dev', region: 'us-east-1' },
      icon: CloudIcon,
      description: 'Cloud storage for documents and files',
    },
    {
      id: 'dynamodb',
      name: 'Amazon DynamoDB',
      type: 'Database',
      provider: 'AWS',
      status: 'connected',
      lastSync: '1 minute ago',
      config: { tablePrefix: 'apex-', region: 'us-east-1' },
      icon: CircleStackIcon,
      description: 'NoSQL database for structured data',
    },
    {
      id: 'bedrock',
      name: 'Amazon Bedrock',
      type: 'AI/ML',
      provider: 'AWS',
      status: 'connected',
      lastSync: 'Real-time',
      config: { model: 'anthropic.claude-3-sonnet', region: 'us-east-1' },
      icon: ServerIcon,
      description: 'Foundation models for AI processing',
    },
    {
      id: 'bda',
      name: 'Bedrock Data Automation',
      type: 'Document AI',
      provider: 'AWS',
      status: 'connected',
      lastSync: 'Real-time',
      config: { projectId: 'apex-bda-project' },
      icon: DocumentTextIcon,
      description: 'Intelligent document processing',
    },
    {
      id: 'ses',
      name: 'Amazon SES',
      type: 'Email',
      provider: 'AWS',
      status: 'connected',
      lastSync: '5 minutes ago',
      config: { domain: 'apex.cbts.com', region: 'us-east-1' },
      icon: EnvelopeIcon,
      description: 'Email sending and notifications',
    },
    {
      id: 'slack',
      name: 'Slack',
      type: 'Communication',
      provider: 'Slack',
      status: 'connected',
      lastSync: 'Real-time',
      config: { workspace: 'cbts-apex', channel: '#apex-alerts' },
      icon: ChatBubbleLeftRightIcon,
      description: 'Team notifications and alerts',
    },
  ];

  const availableConnectors = [
    { id: 'salesforce', name: 'Salesforce', type: 'CRM', icon: CloudIcon, description: 'Customer relationship management' },
    { id: 'servicenow', name: 'ServiceNow', type: 'ITSM', icon: ServerIcon, description: 'IT service management' },
    { id: 'sap', name: 'SAP', type: 'ERP', icon: CircleStackIcon, description: 'Enterprise resource planning' },
    { id: 'workday', name: 'Workday', type: 'HCM', icon: ServerIcon, description: 'Human capital management' },
    { id: 'snowflake', name: 'Snowflake', type: 'Data Warehouse', icon: CircleStackIcon, description: 'Cloud data warehouse' },
    { id: 'postgresql', name: 'PostgreSQL', type: 'Database', icon: CircleStackIcon, description: 'Relational database' },
    { id: 'mongodb', name: 'MongoDB', type: 'Database', icon: CircleStackIcon, description: 'Document database' },
    { id: 'sharepoint', name: 'SharePoint', type: 'Document', icon: DocumentTextIcon, description: 'Document management' },
  ];

  const connectorsByType = connectors.reduce((acc, connector) => {
    if (!acc[connector.type]) {
      acc[connector.type] = [];
    }
    acc[connector.type].push(connector);
    return acc;
  }, {} as Record<string, Connector[]>);

  return (
    <>
      <Head>
        <title>Connectors | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Data Connectors</h1>
            <p className="text-gray-500 mt-1">Connect to external systems and data sources</p>
          </div>
          <Button
            variant="primary"
            icon={<PlusIcon className="h-5 w-5" />}
            onClick={() => setShowAddModal(true)}
          >
            Add Connector
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-apex-100 rounded-xl">
                <LinkIcon className="h-6 w-6 text-apex-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Connectors</p>
                <p className="text-2xl font-bold text-gray-900">{connectors.length}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-xl">
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Connected</p>
                <p className="text-2xl font-bold text-gray-900">
                  {connectors.filter(c => c.status === 'connected').length}
                </p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-xl">
                <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Issues</p>
                <p className="text-2xl font-bold text-gray-900">
                  {connectors.filter(c => c.status === 'error').length}
                </p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-xl">
                <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Secure</p>
                <p className="text-2xl font-bold text-gray-900">100%</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Connectors by Type */}
        {Object.entries(connectorsByType).map(([type, typeConnectors]) => (
          <div key={type} className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">{type}</h2>
            <div className="grid grid-cols-3 gap-4">
              {typeConnectors.map((connector) => (
                <Card
                  key={connector.id}
                  hover
                  className="cursor-pointer"
                  onClick={() => setSelectedConnector(connector)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`p-3 rounded-xl ${
                        connector.status === 'connected' ? 'bg-green-100' :
                        connector.status === 'error' ? 'bg-red-100' : 'bg-gray-100'
                      }`}>
                        <connector.icon className={`h-6 w-6 ${
                          connector.status === 'connected' ? 'text-green-600' :
                          connector.status === 'error' ? 'text-red-600' : 'text-gray-600'
                        }`} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{connector.name}</h3>
                        <p className="text-sm text-gray-500">{connector.description}</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <Badge variant="outline">{connector.provider}</Badge>
                    <div className="flex items-center gap-2">
                      {connector.status === 'connected' && (
                        <>
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                          <span className="text-xs text-gray-500">Synced {connector.lastSync}</span>
                        </>
                      )}
                      {connector.status === 'error' && (
                        <Badge variant="danger" size="sm">Error</Badge>
                      )}
                      {connector.status === 'disconnected' && (
                        <Badge variant="default" size="sm">Disconnected</Badge>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}

        {/* Connector Detail Modal */}
        {selectedConnector && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-lg">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl ${
                    selectedConnector.status === 'connected' ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    <selectedConnector.icon className={`h-8 w-8 ${
                      selectedConnector.status === 'connected' ? 'text-green-600' : 'text-gray-600'
                    }`} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{selectedConnector.name}</h2>
                    <p className="text-gray-500">{selectedConnector.description}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <Badge variant={selectedConnector.status === 'connected' ? 'success' : 'default'}>
                        {selectedConnector.status}
                      </Badge>
                      <Badge variant="outline">{selectedConnector.provider}</Badge>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedConnector(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Configuration</h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    {Object.entries(selectedConnector.config).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-500">{key}</span>
                        <span className="font-mono text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Status</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {selectedConnector.status === 'connected' && (
                          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                        )}
                        <span className="text-sm">
                          {selectedConnector.status === 'connected' ? 'Connected and healthy' : 'Not connected'}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">Last sync: {selectedConnector.lastSync}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-4 border-t">
                  <Button variant="secondary" icon={<ArrowPathIcon className="h-4 w-4" />}>
                    Test Connection
                  </Button>
                  <Button variant="secondary" icon={<Cog6ToothIcon className="h-4 w-4" />}>
                    Configure
                  </Button>
                  <Button variant="ghost" icon={<TrashIcon className="h-4 w-4 text-red-500" />}>
                    Remove
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Add Connector Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-3xl max-h-[80vh] overflow-auto">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Add Connector</h2>
                  <p className="text-gray-500">Choose a connector to integrate with your platform</p>
                </div>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {availableConnectors.map((connector) => (
                  <button
                    key={connector.id}
                    className="p-4 border border-gray-200 rounded-xl hover:border-apex-500 hover:bg-apex-50 transition-colors text-left flex items-start gap-3"
                  >
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <connector.icon className="h-6 w-6 text-gray-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{connector.name}</h3>
                      <p className="text-sm text-gray-500">{connector.description}</p>
                      <Badge variant="outline" size="sm" className="mt-2">{connector.type}</Badge>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500 text-center">
                  Don't see what you need? <button className="text-apex-600 font-medium">Request a connector</button>
                </p>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}
