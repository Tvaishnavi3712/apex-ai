/**
 * Agents Page - Manage AI Agents
 * Fetches real data from backend APIs
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Card, CardHeader, Button, StatusBadge, Badge } from '@/components/common';
import {
  CpuChipIcon,
  PlusIcon,
  PlayIcon,
  StopIcon,
  TrashIcon,
  PencilSquareIcon,
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type AgentStatus = 'running' | 'stopped' | 'error' | 'active' | 'inactive';

interface Agent {
  agent_id: string;
  name: string;
  description?: string;
  playbook_id?: string;
  status: string;
  type?: string;
  created_at?: string;
  updated_at?: string;
}

interface WorkItem {
  work_item_id: string;
  status: string;
  agent_id?: string;
  created_at?: string;
  payload?: any;
}

interface Playbook {
  playbook_id: string;
  name: string;
}

export default function Agents() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);

  // Agent state
  const [agents, setAgents] = useState<Agent[]>([]);
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);

  // Fetch data from APIs
  const fetchData = async () => {
    try {
      const [agentsRes, workItemsRes, playbooksRes] = await Promise.all([
        fetch(`${API_BASE_URL}/agents/`),
        fetch(`${API_BASE_URL}/work-items/`),
        fetch(`${API_BASE_URL}/playbooks/`),
      ]);

      const agentsData = agentsRes.ok ? await agentsRes.json() : [];
      const workItemsData = workItemsRes.ok ? await workItemsRes.json() : [];
      const playbooksData = playbooksRes.ok ? await playbooksRes.json() : [];

      setAgents(agentsData);
      setWorkItems(workItemsData);
      setPlaybooks(playbooksData);
    } catch (err) {
      console.error('Failed to fetch agents data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Helper functions
  const getPlaybookName = (playbookId?: string): string => {
    if (!playbookId) return 'No playbook';
    const playbook = playbooks.find(p => p.playbook_id === playbookId);
    return playbook?.name || playbookId;
  };

  const calculateUptime = (createdAt?: string, status?: string): string => {
    if (status !== 'active' && status !== 'running') return '-';
    if (!createdAt) return '0h 00m';
    try {
      const created = new Date(createdAt);
      const now = new Date();
      const diffMs = now.getTime() - created.getTime();
      const hours = Math.floor(diffMs / 3600000);
      const minutes = Math.floor((diffMs % 3600000) / 60000);
      return `${hours}h ${minutes.toString().padStart(2, '0')}m`;
    } catch {
      return '0h 00m';
    }
  };

  const getTasksCompleted = (agentId: string): number => {
    return workItems.filter(w => w.agent_id === agentId && w.status === 'completed').length;
  };

  const getSuccessRate = (agentId: string): number => {
    const agentTasks = workItems.filter(w => w.agent_id === agentId);
    if (agentTasks.length === 0) return 100;
    const completed = agentTasks.filter(w => w.status === 'completed').length;
    return Math.round((completed / agentTasks.length) * 1000) / 10;
  };

  const getLastActivity = (agentId: string): string => {
    const agentTasks = workItems.filter(w => w.agent_id === agentId);
    if (agentTasks.length === 0) return 'No activity';
    const sorted = agentTasks.sort((a, b) =>
      new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime()
    );
    if (!sorted[0].created_at) return 'Unknown';
    const date = new Date(sorted[0].created_at);
    const diffMs = new Date().getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const isRunning = (status: string): boolean => status === 'active' || status === 'running';
  const isError = (status: string): boolean => status === 'error';

  const stats = {
    total: agents.length,
    running: agents.filter(a => isRunning(a.status)).length,
    stopped: agents.filter(a => a.status === 'inactive' || a.status === 'stopped').length,
    error: agents.filter(a => isError(a.status)).length,
  };

  // Handle start agent (call API)
  const handleStartAgent = async (agentId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'active' }),
      });
      if (res.ok) {
        setAgents(prev => prev.map(agent => {
          if (agent.agent_id === agentId) {
            return { ...agent, status: 'active' };
          }
          return agent;
        }));
      }
    } catch (err) {
      console.error('Failed to start agent:', err);
    }
  };

  // Handle stop agent (call API)
  const handleStopAgent = async (agentId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${API_BASE_URL}/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'inactive' }),
      });
      if (res.ok) {
        setAgents(prev => prev.map(agent => {
          if (agent.agent_id === agentId) {
            return { ...agent, status: 'inactive' };
          }
          return agent;
        }));
      }
    } catch (err) {
      console.error('Failed to stop agent:', err);
    }
  };

  // Handle delete
  const handleDeleteClick = (agent: Agent, e: React.MouseEvent) => {
    e.stopPropagation();
    setAgentToDelete(agent);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!agentToDelete) return;
    try {
      const res = await fetch(`${API_BASE_URL}/agents/${agentToDelete.agent_id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setAgents(prev => prev.filter(a => a.agent_id !== agentToDelete.agent_id));
      }
    } catch (err) {
      console.error('Failed to delete agent:', err);
    }
    setShowDeleteModal(false);
    setAgentToDelete(null);
    setSelectedAgent(null);
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading agents...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Agents | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Agents</h1>
            <p className="text-gray-500 mt-1">Deploy and manage your automated agents</p>
          </div>
          <Link href="/canvas/new">
            <Button
              variant="primary"
              icon={<PlusIcon className="h-5 w-5" />}
            >
              Create Agent
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <Card className="bg-gradient-to-br from-apex-500 to-apex-600 text-white">
            <div className="flex items-center gap-3">
              <CpuChipIcon className="h-8 w-8 opacity-80" />
              <div>
                <p className="text-apex-100 text-sm">Total Agents</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <PlayIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Running</p>
                <p className="text-2xl font-bold text-gray-900">{stats.running}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <StopIcon className="h-6 w-6 text-gray-600" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Stopped</p>
                <p className="text-2xl font-bold text-gray-900">{stats.stopped}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <CpuChipIcon className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="text-gray-500 text-sm">Error</p>
                <p className="text-2xl font-bold text-gray-900">{stats.error}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Agents List */}
        <div className="space-y-4">
          {agents.length === 0 ? (
            <Card className="text-center py-8">
              <CpuChipIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No agents found</p>
              <Link href="/canvas/new">
                <Button variant="primary" size="sm" className="mt-4">
                  Create First Agent
                </Button>
              </Link>
            </Card>
          ) : (
            agents.map((agent) => (
              <Card
                key={agent.agent_id}
                hover
                className={`cursor-pointer transition-all ${
                  selectedAgent === agent.agent_id ? 'ring-2 ring-apex-500' : ''
                }`}
                onClick={() => setSelectedAgent(selectedAgent === agent.agent_id ? null : agent.agent_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${
                      isRunning(agent.status) ? 'bg-green-100' :
                      isError(agent.status) ? 'bg-red-100' : 'bg-gray-100'
                    }`}>
                      <CpuChipIcon className={`h-6 w-6 ${
                        isRunning(agent.status) ? 'text-green-600' :
                        isError(agent.status) ? 'text-red-600' : 'text-gray-600'
                      }`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-500">{agent.description || agent.type || 'AI Agent'}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <Badge variant="outline">
                          <DocumentTextIcon className="h-3 w-3 mr-1" />
                          {getPlaybookName(agent.playbook_id)}
                        </Badge>
                        <span className="text-xs text-gray-400">Last active: {getLastActivity(agent.agent_id)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Uptime</p>
                      <p className="font-medium">{calculateUptime(agent.created_at, agent.status)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Tasks</p>
                      <p className="font-medium">{getTasksCompleted(agent.agent_id)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Success</p>
                      <p className="font-medium">{getSuccessRate(agent.agent_id)}%</p>
                    </div>
                    <StatusBadge status={isRunning(agent.status) ? 'running' : isError(agent.status) ? 'error' : 'stopped'} />
                    <div className="flex items-center gap-2">
                      {isRunning(agent.status) ? (
                        <Button
                          variant="secondary"
                          size="sm"
                          icon={<StopIcon className="h-4 w-4" />}
                          onClick={(e) => handleStopAgent(agent.agent_id, e)}
                        >
                          Stop
                        </Button>
                      ) : (
                        <Button
                          variant="primary"
                          size="sm"
                          icon={<PlayIcon className="h-4 w-4" />}
                          onClick={(e) => handleStartAgent(agent.agent_id, e)}
                        >
                          Start
                        </Button>
                      )}
                      <Link href="/command-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={<ChartBarIcon className="h-4 w-4" />}
                          onClick={(e) => e.stopPropagation()}
                        >
                          Monitor
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedAgent === agent.agent_id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-3 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Configuration</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Agent ID:</span>
                            <span className="truncate max-w-[150px]">{agent.agent_id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Type:</span>
                            <span>{agent.type || 'Standard'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Status:</span>
                            <span>{agent.status}</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Recent Activity</h4>
                        <div className="space-y-2 text-sm">
                          {workItems.filter(w => w.agent_id === agent.agent_id).slice(0, 3).map((w, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${
                                w.status === 'completed' ? 'bg-green-500' :
                                w.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                              }`} />
                              <span className="truncate">{w.payload?.property_name || w.work_item_id} - {w.status}</span>
                            </div>
                          ))}
                          {workItems.filter(w => w.agent_id === agent.agent_id).length === 0 && (
                            <span className="text-gray-400">No recent activity</span>
                          )}
                        </div>
                      </div>
                      <div className="flex flex-col justify-center">
                        <div className="flex gap-2">
                          <Link href={`/canvas/playbook/${agent.playbook_id || agent.agent_id}`}>
                            <Button variant="secondary" size="sm" icon={<PencilSquareIcon className="h-4 w-4" />}>
                              Edit Playbook
                            </Button>
                          </Link>
                          <Link href="/agent-hub">
                            <Button variant="secondary" size="sm" icon={<CpuChipIcon className="h-4 w-4" />}>
                              Open Chat
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<TrashIcon className="h-4 w-4 text-red-500" />}
                            onClick={(e) => handleDeleteClick(agent, e)}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            ))
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && agentToDelete && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-md">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-red-100 rounded-xl">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">Delete Agent?</h3>
                  <p className="text-gray-500 mt-1">
                    Are you sure you want to delete <strong>{agentToDelete.name}</strong>? This action cannot be undone.
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
      </div>
    </>
  );
}
