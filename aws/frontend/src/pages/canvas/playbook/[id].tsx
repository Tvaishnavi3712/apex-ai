/**
 * Playbook Editor Page - Edit existing playbook
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { PlaybookEditor } from '@/components/PlaybookBuilder/PlaybookEditor';
import { Button, Badge, Card } from '@/components/common';
import { ArrowLeftIcon, CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Playbook data interface
interface PlaybookAction {
  id: string;
  name: string;
  action_id: string;
  type?: string;
  description: string;
  required: boolean;
  config?: Record<string, any>;
}

interface PlaybookData {
  playbook_id?: string;
  name: string;
  description?: string;
  version?: string;
  industry?: string;
  intent: string;
  recipe: string;
  actions: PlaybookAction[];
  triggers?: any[];
  output?: any[];
  context?: Record<string, any>;
  data_sources?: any[];
  status?: string;
  // CRE playbook specific fields
  processing_stages?: any[];
  guardrails?: any;
}

export default function EditPlaybook() {
  const router = useRouter();
  const { id } = router.query;
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [deployStatus, setDeployStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');
  const [deployMessage, setDeployMessage] = useState('');
  const [agentName, setAgentName] = useState('');

  // Playbook data state
  const [playbookData, setPlaybookData] = useState<PlaybookData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch playbook data from API
  useEffect(() => {
    async function fetchPlaybook() {
      if (!id) return;

      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE_URL}/playbooks/${id}`);

        if (res.ok) {
          const data = await res.json();
          // Transform actions to match expected format
          // Note: action_id is stored in config.action_id in the API response
          const transformedActions = (data.actions || []).map((action: any, index: number) => ({
            id: action.id || String(index + 1),
            name: action.name,
            action_id: action.config?.action_id || action.action_id || action.type || action.name,
            description: action.description || action.config?.trigger_condition || '',
            required: action.config?.required ?? action.required ?? true,
          }));

          setPlaybookData({
            ...data,
            actions: transformedActions,
            description: data.description || data.intent?.substring(0, 100) + '...',
          });
        } else if (res.status === 404) {
          // If not found in API, check if it's a local YAML playbook by name
          setError(`Playbook not found. It may need to be imported first.`);
        } else {
          const errorText = await res.text();
          setError(`Failed to load playbook: ${errorText}`);
        }
      } catch (err) {
        console.error('Error fetching playbook:', err);
        setError('Failed to connect to the API. Please ensure the backend is running.');
      } finally {
        setLoading(false);
      }
    }

    fetchPlaybook();
  }, [id]);

  // Available actions - includes general and CRE-specific actions
  const availableActions = [
    // General actions
    { id: 'bda_extract', name: 'BDA Extract', description: 'Extract data from documents' },
    { id: 'dynamodb_lookup', name: 'DynamoDB Lookup', description: 'Query database records' },
    { id: 'vendor_lookup', name: 'Vendor Lookup', description: 'Find vendor information' },
    { id: 'po_match', name: 'PO Match', description: 'Match against purchase orders' },
    { id: 'approval_route', name: 'Approval Route', description: 'Route for approval' },
    { id: 'compliance_check', name: 'Compliance Check', description: 'Validate compliance rules' },
    { id: 's3_upload', name: 'S3 Upload', description: 'Upload files to S3' },
    { id: 'notification', name: 'Notification', description: 'Send notifications' },
    // CRE Underwriting actions
    { id: 'cre.document_extract', name: 'CRE Document Extract', description: 'Extract property and submission data from documents' },
    { id: 'cre.risk_score', name: 'CRE Risk Score', description: 'Calculate risk score based on property factors' },
    { id: 'cre.premium_calculate', name: 'CRE Premium Calculate', description: 'Calculate premium using rates and adjustments' },
    { id: 'cre.loss_history', name: 'CRE Loss History', description: 'Retrieve loss history from carrier systems' },
    { id: 'cre.auto_decision', name: 'CRE Auto Decision', description: 'Apply underwriting rules to make decision' },
    { id: 'cre.cat_model', name: 'CRE CAT Model', description: 'Run catastrophe modeling for CAT-exposed properties' },
    { id: 'cre.generate_referral', name: 'CRE Generate Referral', description: 'Generate referral package for human review' },
    // Insurance Underwriting actions
    { id: 'insurance.application_extract', name: 'Application Extract', description: 'Extract data from insurance application' },
    { id: 'insurance.credit_check', name: 'Credit Check', description: 'Run credit score check' },
    { id: 'insurance.loss_history_check', name: 'Loss History Check', description: 'Check loss history records' },
    { id: 'insurance.risk_score', name: 'Risk Score', description: 'Calculate risk score' },
    { id: 'insurance.premium_calculate', name: 'Premium Calculate', description: 'Calculate premium amount' },
    { id: 'insurance.underwriter_route', name: 'Underwriter Route', description: 'Route to appropriate underwriter' },
    // Healthcare actions
    { id: 'healthcare_payers.auth_extract', name: 'Auth Extract', description: 'Extract prior authorization data' },
    { id: 'healthcare_payers.eligibility_check', name: 'Eligibility Check', description: 'Check member eligibility' },
    { id: 'healthcare_payers.claims_extract', name: 'Claims Extract', description: 'Extract claims data' },
    // Financial Services actions
    { id: 'financial.invoice_extract', name: 'Invoice Extract', description: 'Extract invoice data' },
    { id: 'financial.payment_process', name: 'Payment Process', description: 'Process payment' },
  ];

  const handleSave = async (data: any) => {
    console.log('Saving playbook:', data);
    try {
      const res = await fetch(`${API_BASE_URL}/playbooks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        alert('Playbook saved successfully!');
      }
    } catch (err) {
      console.error('Error saving playbook:', err);
    }
  };

  const handleDeploy = (data: any) => {
    // Use playbookData.name if data.name is missing
    const name = data?.name || playbookData?.name || 'NewAgent';
    setAgentName(`${name.replace(/[\s_]+/g, '')}Bot`);
    setShowDeployModal(true);
  };

  // Loading state
  if (loading) {
    return (
      <>
        <Head>
          <title>Loading Playbook | Canvas</title>
        </Head>
        <div className="h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apex-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading playbook...</p>
          </div>
        </div>
      </>
    );
  }

  // Error state
  if (error || !playbookData) {
    return (
      <>
        <Head>
          <title>Playbook Not Found | Canvas</title>
        </Head>
        <div className="h-screen flex items-center justify-center">
          <Card className="w-full max-w-md text-center p-8">
            <XMarkIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Playbook</h2>
            <p className="text-gray-600 mb-6">{error || 'Playbook data not available.'}</p>
            <div className="flex gap-3 justify-center">
              <Link href="/canvas">
                <Button variant="secondary">Back to Canvas</Button>
              </Link>
              <Button variant="primary" onClick={() => window.location.reload()}>
                Retry
              </Button>
            </div>
          </Card>
        </div>
      </>
    );
  }

  const handleConfirmDeploy = async () => {
    setDeployStatus('deploying');
    try {
      // Build instructions - ensure it's never empty
      const instructions = playbookData?.intent
        || playbookData?.recipe
        || `You are an AI agent based on the ${playbookData?.name || 'workflow'} playbook. Process work items according to the defined workflow steps.`;

      // Create an agent from the playbook
      const agentData = {
        name: agentName,
        playbook_id: playbookData?.playbook_id || id as string,
        type: 'collaborator',
        description: `Agent deployed from playbook: ${playbookData?.name || 'Unknown'}`,
        instructions: instructions,
        environment: 'development',
      };

      console.log('Deploying agent with data:', agentData);

      const res = await fetch(`${API_BASE_URL}/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentData),
      });

      if (res.ok) {
        const agent = await res.json();
        setDeployStatus('success');
        setDeployMessage(`Agent "${agentName}" created successfully! Agent ID: ${agent.agent_id}`);
      } else {
        const errorText = await res.text();
        console.error('Deploy failed:', errorText);
        setDeployStatus('error');
        setDeployMessage(`Failed to deploy: ${errorText}`);
      }
    } catch (err) {
      console.error('Deploy error:', err);
      setDeployStatus('error');
      setDeployMessage(`Error: ${err}`);
    }
  };

  const handleTest = (data: any) => {
    console.log('Testing playbook:', data);
    router.push('/testing');
  };

  return (
    <>
      <Head>
        <title>Edit Playbook | Canvas</title>
      </Head>

      <div className="h-screen flex flex-col">
        <div className="p-4 bg-white border-b border-gray-200 flex items-center gap-4">
          <Link href="/canvas">
            <Button
              variant="ghost"
              size="sm"
              icon={<ArrowLeftIcon className="h-4 w-4" />}
            >
              Back to Canvas
            </Button>
          </Link>
          <Badge variant="primary">Editing Playbook</Badge>
          <span className="text-sm text-gray-500">ID: {id}</span>
        </div>

        <div className="flex-1">
          <PlaybookEditor
            initialData={playbookData}
            availableActions={availableActions}
            onSave={handleSave}
            onDeploy={handleDeploy}
            onTest={handleTest}
          />
        </div>

        {/* Deploy Agent Modal */}
        {showDeployModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deploy Agent</h3>
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
                  <p className="text-gray-600 mb-4">
                    This will create a new agent from the playbook "{playbookData.name}".
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
                      onClick={() => setShowDeployModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={handleConfirmDeploy}
                      disabled={!agentName.trim()}
                    >
                      Deploy Agent
                    </Button>
                  </div>
                </>
              )}

              {deployStatus === 'deploying' && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apex-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">Deploying agent...</p>
                </div>
              )}

              {deployStatus === 'success' && (
                <div className="text-center py-4">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-green-600 font-medium mb-2">Agent Deployed Successfully!</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <div className="flex gap-3">
                    <Button
                      variant="secondary"
                      className="flex-1"
                      onClick={() => {
                        setShowDeployModal(false);
                        setDeployStatus('idle');
                      }}
                    >
                      Close
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
      </div>
    </>
  );
}
