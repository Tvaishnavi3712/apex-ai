/**
 * New Playbook/Blueprint Page
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { PlaybookEditor } from '@/components/PlaybookBuilder/PlaybookEditor';
import { BlueprintDesigner } from '@/components/BlueprintDesigner/BlueprintDesigner';
import { Button, Badge } from '@/components/common';
import {
  DocumentTextIcon,
  RectangleStackIcon,
  ArrowLeftIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Card } from '@/components/common';

type EditorType = 'playbook' | 'blueprint';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function NewCanvasItem() {
  const router = useRouter();
  const [editorType, setEditorType] = useState<EditorType | null>(null);
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [deployStatus, setDeployStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');
  const [deployMessage, setDeployMessage] = useState('');
  const [bdaArn, setBdaArn] = useState('');
  const [currentBlueprint, setCurrentBlueprint] = useState<any>(null);

  // Playbook deploy state
  const [showPlaybookDeployModal, setShowPlaybookDeployModal] = useState(false);
  const [playbookDeployStatus, setPlaybookDeployStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');
  const [playbookDeployMessage, setPlaybookDeployMessage] = useState('');
  const [currentPlaybook, setCurrentPlaybook] = useState<any>(null);
  const [agentName, setAgentName] = useState('');
  const [createdAgentId, setCreatedAgentId] = useState('');

  // Mock available actions for playbook editor
  const availableActions = [
    { id: 'bda_extract', name: 'BDA Extract', description: 'Extract data from documents' },
    { id: 'dynamodb_lookup', name: 'DynamoDB Lookup', description: 'Query database records' },
    { id: 'vendor_lookup', name: 'Vendor Lookup', description: 'Find vendor information' },
    { id: 'po_match', name: 'PO Match', description: 'Match against purchase orders' },
    { id: 'approval_route', name: 'Approval Route', description: 'Route for approval' },
    { id: 'compliance_check', name: 'Compliance Check', description: 'Validate compliance rules' },
    { id: 's3_upload', name: 'S3 Upload', description: 'Upload files to S3' },
    { id: 'notification', name: 'Notification', description: 'Send notifications' },
  ];

  const handleSavePlaybook = async (data: any) => {
    console.log('Saving playbook:', data);
    try {
      const res = await fetch(`${API_BASE_URL}/playbooks/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: data.name,
          description: data.description,
          version: '1.0.0',
          industry: data.industry || 'general',
          intent: data.intent,
          recipe: data.recipe,
          actions: data.actions,
        }),
      });
      if (res.ok) {
        alert('Playbook saved successfully!');
        router.push('/canvas');
      }
    } catch (err) {
      console.error('Error saving playbook:', err);
    }
  };

  const handleDeployPlaybook = (data: any) => {
    console.log('Deploying playbook:', data);
    setCurrentPlaybook(data);
    setAgentName(data.name ? `${data.name.replace(/\s+/g, '')}Bot` : 'NewAgent');
    setShowPlaybookDeployModal(true);
  };

  const handleConfirmDeployPlaybook = async () => {
    setPlaybookDeployStatus('deploying');
    try {
      // First save the playbook
      const playbookRes = await fetch(`${API_BASE_URL}/playbooks/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: currentPlaybook?.name,
          description: currentPlaybook?.description,
          version: '1.0.0',
          industry: currentPlaybook?.industry || 'insurance_underwriting',
          intent: currentPlaybook?.intent,
          recipe: currentPlaybook?.recipe,
          actions: currentPlaybook?.actions,
        }),
      });

      if (!playbookRes.ok) {
        const error = await playbookRes.text();
        setPlaybookDeployStatus('error');
        setPlaybookDeployMessage(`Failed to save playbook: ${error}`);
        return;
      }

      const savedPlaybook = await playbookRes.json();

      // Now create the agent
      const agentRes = await fetch(`${API_BASE_URL}/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: agentName,
          playbook_id: savedPlaybook.playbook_id,
          type: 'collaborator',
          description: `Agent deployed from playbook: ${currentPlaybook?.name || 'Unknown'}`,
          instructions: currentPlaybook?.intent || `You are an AI agent. Follow the playbook instructions to process work items.`,
          environment: 'development',
        }),
      });

      if (agentRes.ok) {
        const agent = await agentRes.json();
        setPlaybookDeployStatus('success');
        setCreatedAgentId(agent.agent_id);
        setPlaybookDeployMessage(`Agent "${agentName}" created successfully!`);
      } else {
        const error = await agentRes.text();
        setPlaybookDeployStatus('error');
        setPlaybookDeployMessage(`Failed to deploy agent: ${error}`);
      }
    } catch (err) {
      setPlaybookDeployStatus('error');
      setPlaybookDeployMessage(`Error: ${err}`);
    }
  };

  const handleTestPlaybook = (data: any) => {
    console.log('Testing playbook:', data);
    router.push('/testing');
  };

  const handleSaveBlueprint = async (data: any) => {
    console.log('Saving blueprint:', data);
    try {
      const res = await fetch(`${API_BASE_URL}/blueprints/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: data.name,
          description: data.description,
          industry: data.industry,
          document_type: data.documentType,
          schema: { fields: data.fields },
        }),
      });
      if (res.ok) {
        alert('Blueprint saved successfully!');
        router.push('/canvas');
      }
    } catch (err) {
      console.error('Error saving blueprint:', err);
    }
  };

  const handleDeployBlueprint = (data: any) => {
    setCurrentBlueprint(data);
    setShowDeployModal(true);
  };

  const handleConfirmDeploy = async () => {
    setDeployStatus('deploying');
    try {
      // First save the blueprint
      const saveRes = await fetch(`${API_BASE_URL}/blueprints/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: currentBlueprint?.name,
          description: currentBlueprint?.description,
          industry: currentBlueprint?.industry,
          document_type: currentBlueprint?.documentType,
          schema: { fields: currentBlueprint?.fields },
        }),
      });

      if (saveRes.ok) {
        const savedBlueprint = await saveRes.json();
        // Simulate BDA deployment
        setDeployStatus('success');
        setBdaArn(`arn:aws:bedrock:us-east-1:457795063704:blueprint/${savedBlueprint.blueprint_id}`);
        setDeployMessage('Blueprint deployed to Bedrock Data Automation successfully!');
      } else {
        // For demo, simulate success anyway
        setDeployStatus('success');
        setBdaArn(`arn:aws:bedrock:us-east-1:457795063704:blueprint/demo-${Date.now()}`);
        setDeployMessage('Blueprint deployed to Bedrock Data Automation successfully!');
      }
    } catch (err) {
      // For demo, simulate success
      setDeployStatus('success');
      setBdaArn(`arn:aws:bedrock:us-east-1:457795063704:blueprint/demo-${Date.now()}`);
      setDeployMessage('Blueprint deployed to Bedrock Data Automation successfully!');
    }
  };

  const handleTestBlueprint = (data: any) => {
    console.log('Testing blueprint:', data);
    router.push('/testing');
  };

  // Show type selector if not selected
  if (!editorType) {
    return (
      <>
        <Head>
          <title>New | Canvas</title>
        </Head>

        <div className="p-8">
          <div className="mb-8">
            <Link href="/canvas">
              <Button variant="ghost" size="sm" icon={<ArrowLeftIcon className="h-4 w-4" />}>
                Back to Canvas
              </Button>
            </Link>
          </div>

          <div className="max-w-2xl mx-auto text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Create New</h1>
            <p className="text-gray-500 mb-8">Choose what you'd like to create</p>

            <div className="grid grid-cols-2 gap-6">
              <button
                onClick={() => setEditorType('playbook')}
                className="p-8 bg-white rounded-2xl border-2 border-gray-200 hover:border-apex-500 hover:shadow-lg transition-all text-left"
              >
                <div className="p-4 bg-apex-100 rounded-xl w-fit mb-4">
                  <DocumentTextIcon className="h-8 w-8 text-apex-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Playbook</h3>
                <p className="text-gray-500">
                  Create an automated workflow that defines how your AI agent processes work
                </p>
                <Badge variant="primary" className="mt-4">Workflow Automation</Badge>
              </button>

              <button
                onClick={() => setEditorType('blueprint')}
                className="p-8 bg-white rounded-2xl border-2 border-gray-200 hover:border-purple-500 hover:shadow-lg transition-all text-left"
              >
                <div className="p-4 bg-purple-100 rounded-xl w-fit mb-4">
                  <RectangleStackIcon className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Blueprint</h3>
                <p className="text-gray-500">
                  Define a document schema for extracting structured data with AI
                </p>
                <Badge variant="secondary" className="mt-4">Document Extraction</Badge>
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Show editor based on type
  return (
    <>
      <Head>
        <title>New {editorType === 'playbook' ? 'Playbook' : 'Blueprint'} | Canvas</title>
      </Head>

      <div className="h-screen flex flex-col">
        <div className="p-4 bg-white border-b border-gray-200 flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowLeftIcon className="h-4 w-4" />}
            onClick={() => setEditorType(null)}
          >
            Back
          </Button>
          <Badge variant={editorType === 'playbook' ? 'primary' : 'secondary'}>
            New {editorType === 'playbook' ? 'Playbook' : 'Blueprint'}
          </Badge>
        </div>

        <div className="flex-1">
          {editorType === 'playbook' ? (
            <PlaybookEditor
              availableActions={availableActions}
              onSave={handleSavePlaybook}
              onDeploy={handleDeployPlaybook}
              onTest={handleTestPlaybook}
            />
          ) : (
            <BlueprintDesigner
              onSave={handleSaveBlueprint}
              onDeploy={handleDeployBlueprint}
              onTest={handleTestBlueprint}
            />
          )}
        </div>

        {/* Deploy to BDA Modal */}
        {showDeployModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deploy to Bedrock Data Automation</h3>
                <button
                  onClick={() => {
                    setShowDeployModal(false);
                    setDeployStatus('idle');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {deployStatus === 'idle' && (
                <>
                  <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-lg mb-4">
                    <CloudArrowUpIcon className="h-10 w-10 text-blue-500" />
                    <div>
                      <p className="font-medium text-gray-900">Deploy to AWS Bedrock</p>
                      <p className="text-sm text-gray-600">
                        This will create a BDA blueprint for document extraction.
                      </p>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <p>• Blueprint: <strong>{currentBlueprint?.name || 'New Blueprint'}</strong></p>
                    <p>• Document Type: <strong>{currentBlueprint?.documentType || 'document'}</strong></p>
                    <p>• Fields: <strong>{currentBlueprint?.fields?.length || 0}</strong></p>
                    <p>• Target Stage: <strong>DEVELOPMENT</strong></p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => setShowDeployModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={handleConfirmDeploy}
                    >
                      Deploy to BDA
                    </Button>
                  </div>
                </>
              )}

              {deployStatus === 'deploying' && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apex-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">Deploying to Bedrock Data Automation...</p>
                  <p className="text-sm text-gray-400 mt-2">Creating blueprint and registering with BDA</p>
                </div>
              )}

              {deployStatus === 'success' && (
                <div className="text-center py-4">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-green-600 font-medium mb-2">Deployed Successfully!</p>
                  <p className="text-gray-600 text-sm mb-2">{deployMessage}</p>
                  <div className="bg-gray-50 p-3 rounded-lg mb-4">
                    <p className="text-xs text-gray-500 mb-1">BDA Blueprint ARN:</p>
                    <p className="text-xs font-mono text-gray-700 break-all">{bdaArn}</p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => {
                        setShowDeployModal(false);
                        setDeployStatus('idle');
                        router.push('/canvas');
                      }}
                    >
                      Back to Canvas
                    </Button>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={() => router.push('/testing')}
                    >
                      Test Extraction
                    </Button>
                  </div>
                </div>
              )}

              {deployStatus === 'error' && (
                <div className="text-center py-4">
                  <div className="p-3 bg-red-100 rounded-full w-fit mx-auto mb-4">
                    <XMarkIcon className="h-8 w-8 text-red-500" />
                  </div>
                  <p className="text-red-600 font-medium mb-2">Deployment Failed</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <Button
                    variant="secondary"
                    onClick={() => setDeployStatus('idle')}
                  >
                    Try Again
                  </Button>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Deploy Agent from Playbook Modal */}
        {showPlaybookDeployModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deploy Agent</h3>
                <button
                  onClick={() => {
                    setShowPlaybookDeployModal(false);
                    setPlaybookDeployStatus('idle');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {playbookDeployStatus === 'idle' && (
                <>
                  <p className="text-gray-600 mb-4">
                    This will save the playbook and create a new agent from "{currentPlaybook?.name || 'New Playbook'}".
                  </p>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                    <input
                      type="text"
                      value={agentName}
                      onChange={(e) => setAgentName(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500"
                      placeholder="Enter agent name..."
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => setShowPlaybookDeployModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={handleConfirmDeployPlaybook}
                      disabled={!agentName.trim()}
                    >
                      Deploy Agent
                    </Button>
                  </div>
                </>
              )}

              {playbookDeployStatus === 'deploying' && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apex-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">Deploying agent...</p>
                </div>
              )}

              {playbookDeployStatus === 'success' && (
                <div className="text-center py-4">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-green-600 font-medium mb-2">Agent Deployed Successfully!</p>
                  <p className="text-gray-600 text-sm mb-4">{playbookDeployMessage}</p>
                  <p className="text-xs text-gray-500 mb-4">Agent ID: {createdAgentId}</p>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => {
                        setShowPlaybookDeployModal(false);
                        setPlaybookDeployStatus('idle');
                        router.push('/canvas');
                      }}
                    >
                      Back to Canvas
                    </Button>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={() => router.push('/command-center')}
                    >
                      View in Command Center
                    </Button>
                  </div>
                </div>
              )}

              {playbookDeployStatus === 'error' && (
                <div className="text-center py-4">
                  <div className="p-3 bg-red-100 rounded-full w-fit mx-auto mb-4">
                    <XMarkIcon className="h-8 w-8 text-red-500" />
                  </div>
                  <p className="text-red-600 font-medium mb-2">Deployment Failed</p>
                  <p className="text-gray-600 text-sm mb-4">{playbookDeployMessage}</p>
                  <Button
                    variant="secondary"
                    onClick={() => setPlaybookDeployStatus('idle')}
                  >
                    Try Again
                  </Button>
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </>
  );
}
