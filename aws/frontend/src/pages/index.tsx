/**
 * Dashboard Page - Home
 * Fetches real data from backend APIs
 */

import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Card, CardHeader, Button, StatusBadge, Badge } from '@/components/common';
import {
  DocumentTextIcon,
  CpuChipIcon,
  InboxStackIcon,
  ChartBarIcon,
  ArrowRightIcon,
  PlusIcon,
  SparklesIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DashboardStats {
  playbooks: { total: number; deployed: number };
  agents: { total: number; running: number };
  workItems: { pending: number; completed: number };
  blueprints: { total: number };
}

interface Playbook {
  playbook_id: string;
  name: string;
  status: string;
  industry: string;
}

interface WorkItem {
  work_item_id: string;
  status: string;
  payload?: {
    property_name?: string;
    submission_id?: string;
  };
  created_at: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    playbooks: { total: 0, deployed: 0 },
    agents: { total: 0, running: 0 },
    workItems: { pending: 0, completed: 0 },
    blueprints: { total: 0 },
  });
  const [recentPlaybooks, setRecentPlaybooks] = useState<Playbook[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch all data in parallel
        const [playbooksRes, agentsRes, workItemsRes, blueprintsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/playbooks/`),
          fetch(`${API_BASE_URL}/agents/`),
          fetch(`${API_BASE_URL}/work-items/`),
          fetch(`${API_BASE_URL}/blueprints/`),
        ]);

        // Parse responses
        const playbooks = playbooksRes.ok ? await playbooksRes.json() : [];
        const agents = agentsRes.ok ? await agentsRes.json() : [];
        const workItems = workItemsRes.ok ? await workItemsRes.json() : [];
        const blueprints = blueprintsRes.ok ? await blueprintsRes.json() : [];

        // Calculate stats
        const deployedPlaybooks = playbooks.filter((p: any) => p.status === 'active').length;
        const runningAgents = agents.filter((a: any) => a.status === 'active').length;
        const pendingWorkItems = workItems.filter((w: any) => w.status === 'pending').length;
        const completedWorkItems = workItems.filter((w: any) => w.status === 'completed').length;

        setStats({
          playbooks: { total: playbooks.length, deployed: deployedPlaybooks },
          agents: { total: agents.length, running: runningAgents },
          workItems: { pending: pendingWorkItems, completed: completedWorkItems },
          blueprints: { total: blueprints.length },
        });

        // Get recent playbooks (last 5, sorted by name for consistency)
        const sortedPlaybooks = playbooks
          .sort((a: any, b: any) => {
            // Prioritize insurance_underwriting
            if (a.industry === 'insurance_underwriting' && b.industry !== 'insurance_underwriting') return -1;
            if (b.industry === 'insurance_underwriting' && a.industry !== 'insurance_underwriting') return 1;
            return a.name.localeCompare(b.name);
          })
          .slice(0, 5);
        setRecentPlaybooks(sortedPlaybooks);

        // Build recent activity from work items
        const activity = workItems
          .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 5)
          .map((w: any) => ({
            type: w.status === 'completed' ? 'success' : w.status === 'pending' ? 'info' : 'warning',
            message: `${w.payload?.property_name || w.payload?.submission_id || w.work_item_id} - ${w.status}`,
            time: formatTimeAgo(new Date(w.created_at)),
          }));

        // Add agent activity
        agents.forEach((agent: any) => {
          if (agent.status === 'active') {
            activity.unshift({
              type: 'success',
              message: `${agent.name} is active and processing`,
              time: 'Now',
            });
          }
        });

        setRecentActivity(activity.slice(0, 5));

      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data. Please check if the backend is running.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Helper function to format time ago
  const formatTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Dashboard | APEX AI Platform</title>
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
            <h1 className="text-3xl font-bold text-gray-900">Welcome back</h1>
            <p className="text-gray-500 mt-1">Here's what's happening with your AI agents today.</p>
          </div>
          <Link href="/canvas/new">
            <Button
              variant="primary"
              icon={<PlusIcon className="h-5 w-5" />}
            >
              New Playbook
            </Button>
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <Link href="/canvas">
            <Card className="bg-gradient-to-br from-apex-500 to-apex-600 text-white cursor-pointer hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/20 rounded-xl">
                  <DocumentTextIcon className="h-7 w-7" />
                </div>
                <div>
                  <p className="text-apex-100">Playbooks</p>
                  <p className="text-3xl font-bold">{stats.playbooks.total}</p>
                  <p className="text-sm text-apex-200">{stats.playbooks.deployed} active</p>
                </div>
              </div>
            </Card>
          </Link>

          <Link href="/agents">
            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white cursor-pointer hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/20 rounded-xl">
                  <CpuChipIcon className="h-7 w-7" />
                </div>
                <div>
                  <p className="text-purple-100">Agents</p>
                  <p className="text-3xl font-bold">{stats.agents.total}</p>
                  <p className="text-sm text-purple-200">{stats.agents.running} active</p>
                </div>
              </div>
            </Card>
          </Link>

          <Link href="/agent-hub">
            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white cursor-pointer hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/20 rounded-xl">
                  <InboxStackIcon className="h-7 w-7" />
                </div>
                <div>
                  <p className="text-green-100">Work Items</p>
                  <p className="text-3xl font-bold">{stats.workItems.pending}</p>
                  <p className="text-sm text-green-200">pending review</p>
                </div>
              </div>
            </Card>
          </Link>

          <Link href="/canvas">
            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white cursor-pointer hover:shadow-lg transition-shadow">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/20 rounded-xl">
                  <ChartBarIcon className="h-7 w-7" />
                </div>
                <div>
                  <p className="text-amber-100">Blueprints</p>
                  <p className="text-3xl font-bold">{stats.blueprints.total}</p>
                  <p className="text-sm text-amber-200">document schemas</p>
                </div>
              </div>
            </Card>
          </Link>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-3 gap-6">
          {/* Recent Playbooks */}
          <Card className="col-span-2">
            <CardHeader
              title="Recent Playbooks"
              subtitle={`${stats.playbooks.total} total playbooks`}
              action={
                <Link href="/canvas">
                  <Button variant="ghost" size="sm" icon={<ArrowRightIcon className="h-4 w-4" />} iconPosition="right">
                    View All
                  </Button>
                </Link>
              }
            />
            <div className="space-y-3">
              {recentPlaybooks.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <DocumentTextIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>No playbooks found</p>
                  <Link href="/canvas/new">
                    <Button variant="primary" size="sm" className="mt-2">
                      Create First Playbook
                    </Button>
                  </Link>
                </div>
              ) : (
                recentPlaybooks.map((playbook) => (
                  <Link key={playbook.playbook_id} href={`/canvas?playbook=${playbook.playbook_id}`}>
                    <div
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-lg ${
                          playbook.industry === 'insurance_underwriting'
                            ? 'bg-blue-100'
                            : 'bg-apex-100'
                        }`}>
                          <DocumentTextIcon className={`h-5 w-5 ${
                            playbook.industry === 'insurance_underwriting'
                              ? 'text-blue-600'
                              : 'text-apex-600'
                          }`} />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{playbook.name}</p>
                          <p className="text-sm text-gray-500">
                            {playbook.industry?.replace(/_/g, ' ') || 'general'}
                          </p>
                        </div>
                      </div>
                      <StatusBadge status={playbook.status === 'active' ? 'deployed' : 'draft'} />
                    </div>
                  </Link>
                ))
              )}
            </div>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader title="Recent Activity" />
            <div className="space-y-4">
              {recentActivity.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No recent activity</p>
                </div>
              ) : (
                recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      activity.type === 'success' ? 'bg-green-500' :
                      activity.type === 'warning' ? 'bg-amber-500' :
                      'bg-blue-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700">{activity.message}</p>
                      <p className="text-xs text-gray-400">{activity.time}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-4">
            <Link href="/canvas/new">
              <Card hover className="text-center py-6">
                <DocumentTextIcon className="h-8 w-8 text-apex-500 mx-auto mb-2" />
                <p className="font-medium text-gray-900">Create Playbook</p>
                <p className="text-sm text-gray-500">Build a new workflow</p>
              </Card>
            </Link>
            <Link href="/agent-hub">
              <Card hover className="text-center py-6">
                <SparklesIcon className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                <p className="font-medium text-gray-900">AI Copilot</p>
                <p className="text-sm text-gray-500">Chat with your agent</p>
              </Card>
            </Link>
            <Link href="/command-center">
              <Card hover className="text-center py-6">
                <ChartBarIcon className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="font-medium text-gray-900">View Metrics</p>
                <p className="text-sm text-gray-500">Monitor performance</p>
              </Card>
            </Link>
            <Link href="/testing">
              <Card hover className="text-center py-6">
                <CpuChipIcon className="h-8 w-8 text-amber-500 mx-auto mb-2" />
                <p className="font-medium text-gray-900">Test Agent</p>
                <p className="text-sm text-gray-500">Run in sandbox</p>
              </Card>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
