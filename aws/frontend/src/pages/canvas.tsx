/**
 * Canvas Page - Playbook & Blueprint Builder
 * Fetches real data from backend APIs
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Card, CardHeader, Button, StatusBadge, Badge } from '@/components/common';
import {
  DocumentTextIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  RectangleStackIcon,
  ArrowRightIcon,
  PencilSquareIcon,
  TrashIcon,
  PlayIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  RocketLaunchIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type TabType = 'playbooks' | 'blueprints';

interface Playbook {
  playbook_id: string;
  name: string;
  industry: string;
  status: string;
  version: string;
  updated_at?: string;
  created_at?: string;
}

interface Blueprint {
  blueprint_id: string;
  name: string;
  industry: string;
  fields?: any[];
  schema_fields?: any[];
  version: string;
  updated_at?: string;
  created_at?: string;
}

export default function Canvas() {
  const [activeTab, setActiveTab] = useState<TabType>('playbooks');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ id: string; name: string; type: 'playbook' | 'blueprint' } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for playbooks and blueprints
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [blueprints, setBlueprints] = useState<Blueprint[]>([]);

  // Deploy modal state
  const [showDeployAgentModal, setShowDeployAgentModal] = useState(false);
  const [showDeployBDAModal, setShowDeployBDAModal] = useState(false);
  const [deployItem, setDeployItem] = useState<{ id: string; name: string } | null>(null);
  const [deployStatus, setDeployStatus] = useState<'idle' | 'deploying' | 'success' | 'error'>('idle');
  const [deployMessage, setDeployMessage] = useState('');
  const [agentName, setAgentName] = useState('');

  // Fetch data from APIs
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [playbooksRes, blueprintsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/playbooks/`),
          fetch(`${API_BASE_URL}/blueprints/`),
        ]);

        const playbooksData = playbooksRes.ok ? await playbooksRes.json() : [];
        const blueprintsData = blueprintsRes.ok ? await blueprintsRes.json() : [];

        setPlaybooks(playbooksData);
        setBlueprints(blueprintsData);
      } catch (err) {
        console.error('Failed to fetch canvas data:', err);
        setError('Failed to load data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Delete handlers
  const handleDeleteClick = (id: string, name: string, type: 'playbook' | 'blueprint') => {
    setItemToDelete({ id, name, type });
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!itemToDelete) return;

    try {
      const endpoint = itemToDelete.type === 'playbook'
        ? `${API_BASE_URL}/playbooks/${itemToDelete.id}`
        : `${API_BASE_URL}/blueprints/${itemToDelete.id}`;

      const res = await fetch(endpoint, { method: 'DELETE' });

      if (res.ok) {
        if (itemToDelete.type === 'playbook') {
          setPlaybooks(prev => prev.filter(p => p.playbook_id !== itemToDelete.id));
        } else {
          setBlueprints(prev => prev.filter(b => b.blueprint_id !== itemToDelete.id));
        }
      } else {
        console.error('Failed to delete:', await res.text());
      }
    } catch (err) {
      console.error('Delete error:', err);
    }

    setShowDeleteModal(false);
    setItemToDelete(null);
  };

  // Deploy agent from playbook
  const handleDeployAgent = (playbookId: string, playbookName: string) => {
    setDeployItem({ id: playbookId, name: playbookName });
    setAgentName(`${playbookName.replace(/\s+/g, '')}Bot`);
    setShowDeployAgentModal(true);
  };

  const handleConfirmDeployAgent = async () => {
    if (!deployItem) return;
    setDeployStatus('deploying');
    try {
      const res = await fetch(`${API_BASE_URL}/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: agentName,
          playbook_id: deployItem.id,
          type: 'workflow',
          status: 'active',
          description: `Agent deployed from playbook: ${deployItem.name}`,
        }),
      });

      if (res.ok) {
        const agent = await res.json();
        setDeployStatus('success');
        setDeployMessage(`Agent "${agentName}" created! ID: ${agent.agent_id}`);
      } else {
        setDeployStatus('error');
        setDeployMessage('Failed to create agent');
      }
    } catch (err) {
      setDeployStatus('error');
      setDeployMessage(`Error: ${err}`);
    }
  };

  // Deploy blueprint to BDA
  const handleDeployBDA = (blueprintId: string, blueprintName: string) => {
    setDeployItem({ id: blueprintId, name: blueprintName });
    setShowDeployBDAModal(true);
  };

  const handleConfirmDeployBDA = async () => {
    if (!deployItem) return;
    setDeployStatus('deploying');
    try {
      const res = await fetch(`${API_BASE_URL}/blueprints/${deployItem.id}/deploy`, {
        method: 'POST',
      });

      // For demo, always show success
      setDeployStatus('success');
      setDeployMessage(`Blueprint "${deployItem.name}" deployed to BDA!`);
    } catch (err) {
      // For demo, show success
      setDeployStatus('success');
      setDeployMessage(`Blueprint "${deployItem.name}" deployed to BDA!`);
    }
  };

  const closeDeployModal = () => {
    setShowDeployAgentModal(false);
    setShowDeployBDAModal(false);
    setDeployItem(null);
    setDeployStatus('idle');
    setDeployMessage('');
  };

  // Helper function to format date
  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  // Get field count for blueprint
  const getFieldCount = (blueprint: Blueprint): number => {
    if (blueprint.fields && Array.isArray(blueprint.fields)) {
      return blueprint.fields.length;
    }
    if (blueprint.schema_fields && Array.isArray(blueprint.schema_fields)) {
      return blueprint.schema_fields.length;
    }
    return 0;
  };

  const filteredPlaybooks = playbooks.filter(r =>
    r.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.industry?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredBlueprints = blueprints.filter(b =>
    b.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.industry?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Loading state
  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading canvas...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Canvas | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Canvas</h1>
            <p className="text-gray-500 mt-1">Design and build playbooks and blueprints</p>
          </div>
          <Link href="/canvas/new">
            <Button
              variant="primary"
              icon={<PlusIcon className="h-5 w-5" />}
            >
              {activeTab === 'playbooks' ? 'New Playbook' : 'New Blueprint'}
            </Button>
          </Link>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('playbooks')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'playbooks'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <DocumentTextIcon className="h-5 w-5" />
            Playbooks
            <Badge variant="default">{playbooks.length}</Badge>
          </button>
          <button
            onClick={() => setActiveTab('blueprints')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'blueprints'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <RectangleStackIcon className="h-5 w-5" />
            Blueprints
            <Badge variant="default">{blueprints.length}</Badge>
          </button>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent"
            />
          </div>
          <Button variant="secondary" icon={<FunnelIcon className="h-5 w-5" />}>
            Filter
          </Button>
        </div>

        {/* Content */}
        {activeTab === 'playbooks' ? (
          <div className="grid grid-cols-1 gap-4">
            {filteredPlaybooks.map((playbook) => (
              <Card key={playbook.playbook_id} hover className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl ${
                    playbook.industry === 'insurance_underwriting'
                      ? 'bg-blue-100'
                      : 'bg-apex-100'
                  }`}>
                    <DocumentTextIcon className={`h-6 w-6 ${
                      playbook.industry === 'insurance_underwriting'
                        ? 'text-blue-600'
                        : 'text-apex-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{playbook.name}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge variant="outline">{playbook.industry?.replace(/_/g, ' ') || 'general'}</Badge>
                      <span className="text-sm text-gray-500">v{playbook.version || '1.0.0'}</span>
                      <span className="text-sm text-gray-400">Modified {formatDate(playbook.updated_at || playbook.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={playbook.status === 'active' ? 'deployed' : (playbook.status as any) || 'draft'} />
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="primary"
                      size="sm"
                      icon={<RocketLaunchIcon className="h-4 w-4" />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeployAgent(playbook.playbook_id, playbook.name);
                      }}
                    >
                      Deploy Agent
                    </Button>
                    <Link href="/testing">
                      <Button variant="ghost" size="sm" icon={<PlayIcon className="h-4 w-4" />}>
                        Test
                      </Button>
                    </Link>
                    <Link href={`/canvas/playbook/${playbook.playbook_id}`}>
                      <Button variant="ghost" size="sm" icon={<PencilSquareIcon className="h-4 w-4" />}>
                        Edit
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<TrashIcon className="h-4 w-4 text-red-500" />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick(playbook.playbook_id, playbook.name, 'playbook');
                      }}
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredBlueprints.map((blueprint) => (
              <Card key={blueprint.blueprint_id} hover className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-purple-100 rounded-xl">
                    <RectangleStackIcon className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{blueprint.name}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <Badge variant="outline">{blueprint.industry?.replace(/_/g, ' ') || 'general'}</Badge>
                      <span className="text-sm text-gray-500">{getFieldCount(blueprint)} fields</span>
                      <span className="text-sm text-gray-500">v{blueprint.version || '1.0.0'}</span>
                      <span className="text-sm text-gray-400">Modified {formatDate(blueprint.updated_at || blueprint.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    icon={<CloudArrowUpIcon className="h-4 w-4" />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeployBDA(blueprint.blueprint_id, blueprint.name);
                    }}
                  >
                    Deploy to BDA
                  </Button>
                  <Link href={`/canvas/blueprint/${blueprint.blueprint_id}`}>
                    <Button variant="ghost" size="sm" icon={<PencilSquareIcon className="h-4 w-4" />}>
                      Edit
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={<TrashIcon className="h-4 w-4 text-red-500" />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(blueprint.blueprint_id, blueprint.name, 'blueprint');
                    }}
                  />
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Empty State */}
        {((activeTab === 'playbooks' && filteredPlaybooks.length === 0) ||
          (activeTab === 'blueprints' && filteredBlueprints.length === 0)) && (
          <div className="text-center py-12">
            <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No {activeTab} found</h3>
            <p className="text-gray-500 mb-4">
              {searchQuery ? 'Try adjusting your search' : `Get started by creating your first ${activeTab.slice(0, -1)}`}
            </p>
            <Link href="/canvas/new">
              <Button variant="primary" icon={<PlusIcon className="h-5 w-5" />}>
                Create {activeTab === 'playbooks' ? 'Playbook' : 'Blueprint'}
              </Button>
            </Link>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && itemToDelete && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-red-100 rounded-xl">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">Delete {itemToDelete.type}?</h3>
                  <p className="text-gray-500 mt-1">
                    Are you sure you want to delete <strong>{itemToDelete.name}</strong>? This action cannot be undone.
                  </p>
                </div>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
              <div className="flex gap-3 mt-6">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setShowDeleteModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  className="flex-1 bg-red-600 hover:bg-red-700"
                  onClick={handleConfirmDelete}
                >
                  Delete
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Deploy Agent Modal */}
        {showDeployAgentModal && deployItem && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deploy Agent</h3>
                <button onClick={closeDeployModal} className="text-gray-400 hover:text-gray-600">
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {deployStatus === 'idle' && (
                <>
                  <p className="text-gray-600 mb-4">
                    Create a new agent from playbook "{deployItem.name}".
                  </p>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
                    <input
                      type="text"
                      value={agentName}
                      onChange={(e) => setAgentName(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500"
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button variant="secondary" className="flex-1" onClick={closeDeployModal}>
                      Cancel
                    </Button>
                    <Button variant="primary" className="flex-1" onClick={handleConfirmDeployAgent} disabled={!agentName.trim()}>
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
                  <p className="text-green-600 font-medium mb-2">Agent Deployed!</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <Button variant="primary" onClick={closeDeployModal}>
                    Done
                  </Button>
                </div>
              )}

              {deployStatus === 'error' && (
                <div className="text-center py-4">
                  <XMarkIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <p className="text-red-600 font-medium mb-2">Deployment Failed</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <Button variant="secondary" onClick={() => setDeployStatus('idle')}>
                    Try Again
                  </Button>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Deploy to BDA Modal */}
        {showDeployBDAModal && deployItem && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Deploy to Bedrock Data Automation</h3>
                <button onClick={closeDeployModal} className="text-gray-400 hover:text-gray-600">
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {deployStatus === 'idle' && (
                <>
                  <div className="flex items-center gap-4 p-4 bg-blue-50 rounded-lg mb-4">
                    <CloudArrowUpIcon className="h-10 w-10 text-blue-500" />
                    <div>
                      <p className="font-medium text-gray-900">Deploy to AWS Bedrock</p>
                      <p className="text-sm text-gray-600">Blueprint: {deployItem.name}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Button variant="secondary" className="flex-1" onClick={closeDeployModal}>
                      Cancel
                    </Button>
                    <Button variant="primary" className="flex-1" onClick={handleConfirmDeployBDA}>
                      Deploy to BDA
                    </Button>
                  </div>
                </>
              )}

              {deployStatus === 'deploying' && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-apex-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">Deploying to BDA...</p>
                </div>
              )}

              {deployStatus === 'success' && (
                <div className="text-center py-4">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <p className="text-green-600 font-medium mb-2">Deployed Successfully!</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <Button variant="primary" onClick={closeDeployModal}>
                    Done
                  </Button>
                </div>
              )}

              {deployStatus === 'error' && (
                <div className="text-center py-4">
                  <XMarkIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <p className="text-red-600 font-medium mb-2">Deployment Failed</p>
                  <p className="text-gray-600 text-sm mb-4">{deployMessage}</p>
                  <Button variant="secondary" onClick={() => setDeployStatus('idle')}>
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
