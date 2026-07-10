/**
 * Settings Page - Platform Configuration
 */

import React, { useState } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Button, Badge, Input } from '@/components/common';
import {
  Cog6ToothIcon,
  CloudIcon,
  KeyIcon,
  BellIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

type SettingsTab = 'general' | 'aws' | 'api' | 'notifications' | 'team' | 'security';

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const tabs = [
    { id: 'general', label: 'General', icon: Cog6ToothIcon },
    { id: 'aws', label: 'AWS Configuration', icon: CloudIcon },
    { id: 'api', label: 'API Keys', icon: KeyIcon },
    { id: 'notifications', label: 'Notifications', icon: BellIcon },
    { id: 'team', label: 'Team', icon: UserGroupIcon },
    { id: 'security', label: 'Security', icon: ShieldCheckIcon },
  ];

  return (
    <>
      <Head>
        <title>Settings | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-500 mt-1">Configure your platform settings</p>
          </div>
          {saved && (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircleIcon className="h-5 w-5" />
              <span>Settings saved</span>
            </div>
          )}
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as SettingsTab)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-apex-50 text-apex-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1">
            {activeTab === 'general' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader title="Organization" subtitle="Basic organization settings" />
                  <div className="space-y-4">
                    <Input
                      label="Organization Name"
                      defaultValue="CBTS Applied AI"
                    />
                    <Input
                      label="Environment"
                      defaultValue="Development"
                    />
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">Debug Mode</p>
                        <p className="text-sm text-gray-500">Enable detailed logging</p>
                      </div>
                      <Badge variant="success">Enabled</Badge>
                    </div>
                  </div>
                </Card>

                <Card>
                  <CardHeader title="Default Settings" subtitle="Default values for new runbooks and agents" />
                  <div className="space-y-4">
                    <Input
                      label="Default Timeout (seconds)"
                      type="number"
                      defaultValue="300"
                    />
                    <Input
                      label="Max Concurrent Tasks"
                      type="number"
                      defaultValue="10"
                    />
                    <Input
                      label="Default Industry"
                      defaultValue="Financial Services"
                    />
                  </div>
                </Card>

                <Button variant="primary" onClick={handleSave}>Save Changes</Button>
              </div>
            )}

            {activeTab === 'aws' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader title="AWS Configuration" subtitle="Connect to your AWS account" />
                  <div className="space-y-4">
                    <Input
                      label="AWS Region"
                      defaultValue="us-east-1"
                    />
                    <Input
                      label="AWS Account ID"
                      defaultValue="457795063704"
                    />
                    <Input
                      label="S3 Bucket (Blueprints)"
                      defaultValue="apex-blueprints-457795063704"
                    />
                    <Input
                      label="S3 Bucket (Documents)"
                      defaultValue="apex-documents-incoming-457795063704"
                    />
                    <Input
                      label="DynamoDB Table Prefix"
                      defaultValue="apex-ai-platform-"
                    />
                  </div>
                </Card>

                <Card>
                  <CardHeader title="Bedrock Configuration" subtitle="AI model settings" />
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">Bedrock Data Automation</p>
                        <p className="text-sm text-gray-500">Document extraction service</p>
                      </div>
                      <Badge variant="success">Connected</Badge>
                    </div>
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">Bedrock AgentCore</p>
                        <p className="text-sm text-gray-500">Agent orchestration</p>
                      </div>
                      <Badge variant="success">Connected</Badge>
                    </div>
                    <Input
                      label="Default Model (Schema Generation)"
                      defaultValue="Claude Opus 4.6 (us.anthropic.claude-opus-4-6-v1)"
                    />
                    <Input
                      label="Default Model (Agent Reasoning)"
                      defaultValue="Claude Opus 4.6 (us.anthropic.claude-opus-4-6-v1)"
                    />
                  </div>
                </Card>

                <Button variant="primary" onClick={handleSave}>Save Changes</Button>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader title="API Keys" subtitle="Manage your API access" />
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">Production Key</p>
                          <p className="text-sm text-gray-500 font-mono">apex_prod_****...****7f3d</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">Reveal</Button>
                          <Button variant="ghost" size="sm">Regenerate</Button>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">Development Key</p>
                          <p className="text-sm text-gray-500 font-mono">apex_dev_****...****2a1b</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">Reveal</Button>
                          <Button variant="ghost" size="sm">Regenerate</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>

                <Card>
                  <CardHeader title="Webhooks" subtitle="Configure webhook endpoints" />
                  <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center">
                    <p className="text-gray-500">No webhooks configured</p>
                    <Button variant="secondary" size="sm" className="mt-2">Add Webhook</Button>
                  </div>
                </Card>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader title="Email Notifications" subtitle="Configure email alerts" />
                  <div className="space-y-4">
                    {[
                      { label: 'Agent errors', description: 'When an agent encounters an error', enabled: true },
                      { label: 'Task completion', description: 'When high-priority tasks complete', enabled: false },
                      { label: 'Daily summary', description: 'Daily digest of agent activity', enabled: true },
                      { label: 'Deployment alerts', description: 'When runbooks are deployed', enabled: true },
                    ].map((item, index) => (
                      <div key={index} className="flex items-center justify-between py-2">
                        <div>
                          <p className="font-medium text-gray-900">{item.label}</p>
                          <p className="text-sm text-gray-500">{item.description}</p>
                        </div>
                        <Badge variant={item.enabled ? 'success' : 'default'}>
                          {item.enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>

                <Button variant="primary" onClick={handleSave}>Save Changes</Button>
              </div>
            )}

            {activeTab === 'team' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader
                    title="Team Members"
                    subtitle="Manage who has access"
                    action={<Button variant="primary" size="sm">Invite Member</Button>}
                  />
                  <div className="space-y-3">
                    {[
                      { name: 'Admin User', email: 'admin@cbts.com', role: 'Admin' },
                      { name: 'Developer', email: 'dev@cbts.com', role: 'Developer' },
                      { name: 'Analyst', email: 'analyst@cbts.com', role: 'Viewer' },
                    ].map((member, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-apex-100 rounded-full flex items-center justify-center">
                            <span className="text-apex-600 font-medium">
                              {member.name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{member.name}</p>
                            <p className="text-sm text-gray-500">{member.email}</p>
                          </div>
                        </div>
                        <Badge variant="outline">{member.role}</Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader title="Authentication" subtitle="Security settings" />
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                        <p className="text-sm text-gray-500">Require 2FA for all users</p>
                      </div>
                      <Badge variant="success">Enabled</Badge>
                    </div>
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">SSO Integration</p>
                        <p className="text-sm text-gray-500">Single sign-on via SAML</p>
                      </div>
                      <Badge variant="default">Not Configured</Badge>
                    </div>
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <p className="font-medium text-gray-900">Session Timeout</p>
                        <p className="text-sm text-gray-500">Auto-logout after inactivity</p>
                      </div>
                      <span className="text-gray-900">30 minutes</span>
                    </div>
                  </div>
                </Card>

                <Card>
                  <CardHeader title="Audit Log" subtitle="Recent security events" />
                  <div className="space-y-2">
                    {[
                      { action: 'Login', user: 'admin@cbts.com', time: '10 minutes ago' },
                      { action: 'API Key Regenerated', user: 'admin@cbts.com', time: '2 hours ago' },
                      { action: 'Runbook Deployed', user: 'dev@cbts.com', time: '5 hours ago' },
                    ].map((event, index) => (
                      <div key={index} className="flex items-center justify-between py-2 text-sm">
                        <span className="text-gray-900">{event.action}</span>
                        <span className="text-gray-500">{event.user}</span>
                        <span className="text-gray-400">{event.time}</span>
                      </div>
                    ))}
                  </div>
                </Card>

                <Button variant="primary" onClick={handleSave}>Save Changes</Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
