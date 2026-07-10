/**
 * Agent Monitor - Real-time agent status and metrics
 */

import React from 'react';
import { Card, CardHeader, Badge, StatusBadge, Button } from '../common';
import {
  PlayIcon,
  StopIcon,
  ArrowPathIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface Agent {
  id: string;
  name: string;
  type: 'supervisor' | 'worker' | 'collaborator';
  status: 'idle' | 'running' | 'error' | 'stopped';
  runbookId: string;
  runbookName: string;
  currentTask?: string;
  metrics: {
    tasksCompleted: number;
    tasksFailed: number;
    successRate: number;
    avgDuration: number;
    uptime: number;
  };
  lastActivity: string;
}

interface AgentMonitorProps {
  agents: Agent[];
  onStartAgent: (agentId: string) => void;
  onStopAgent: (agentId: string) => void;
  onRestartAgent: (agentId: string) => void;
  onViewAgent: (agent: Agent) => void;
}

const typeColors = {
  supervisor: 'purple',
  worker: 'info',
  collaborator: 'warning',
};

export const AgentMonitor: React.FC<AgentMonitorProps> = ({
  agents,
  onStartAgent,
  onStopAgent,
  onRestartAgent,
  onViewAgent,
}) => {
  const runningAgents = agents.filter((a) => a.status === 'running').length;
  const errorAgents = agents.filter((a) => a.status === 'error').length;
  const totalTasks = agents.reduce((sum, a) => sum + a.metrics.tasksCompleted, 0);
  const avgSuccessRate = agents.length > 0
    ? agents.reduce((sum, a) => sum + a.metrics.successRate, 0) / agents.length
    : 0;

  return (
    <div className="h-full flex flex-col">
      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 p-4 bg-white border-b border-gray-200">
        <Card padding="sm" className="bg-apex-50 border-apex-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-apex-100 rounded-lg">
              <CpuChipIcon className="h-5 w-5 text-apex-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-apex-700">{runningAgents}</p>
              <p className="text-sm text-apex-600">Running Agents</p>
            </div>
          </div>
        </Card>

        <Card padding="sm" className={clsx(
          errorAgents > 0 ? 'bg-danger-50 border-danger-200' : 'bg-gray-50'
        )}>
          <div className="flex items-center gap-3">
            <div className={clsx(
              'p-2 rounded-lg',
              errorAgents > 0 ? 'bg-danger-100' : 'bg-gray-100'
            )}>
              <ExclamationTriangleIcon className={clsx(
                'h-5 w-5',
                errorAgents > 0 ? 'text-danger-600' : 'text-gray-400'
              )} />
            </div>
            <div>
              <p className={clsx(
                'text-2xl font-bold',
                errorAgents > 0 ? 'text-danger-700' : 'text-gray-700'
              )}>{errorAgents}</p>
              <p className={clsx(
                'text-sm',
                errorAgents > 0 ? 'text-danger-600' : 'text-gray-500'
              )}>Errors</p>
            </div>
          </div>
        </Card>

        <Card padding="sm" className="bg-success-50 border-success-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-success-100 rounded-lg">
              <CheckCircleIcon className="h-5 w-5 text-success-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-success-700">{totalTasks}</p>
              <p className="text-sm text-success-600">Tasks Completed</p>
            </div>
          </div>
        </Card>

        <Card padding="sm" className="bg-purple-50 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <ClockIcon className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-700">{avgSuccessRate.toFixed(1)}%</p>
              <p className="text-sm text-purple-600">Success Rate</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {agents.map((agent) => (
            <Card
              key={agent.id}
              hover
              onClick={() => onViewAgent(agent)}
              className="cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={clsx(
                    'w-3 h-3 rounded-full',
                    agent.status === 'running' && 'bg-success-500 animate-pulse',
                    agent.status === 'idle' && 'bg-gray-300',
                    agent.status === 'error' && 'bg-danger-500',
                    agent.status === 'stopped' && 'bg-warning-500'
                  )} />
                  <div>
                    <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                    <p className="text-sm text-gray-500">{agent.runbookName}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={typeColors[agent.type] as any} size="sm">
                    {agent.type}
                  </Badge>
                  <StatusBadge status={agent.status} />
                </div>
              </div>

              {agent.currentTask && (
                <div className="mt-3 p-2 bg-apex-50 rounded-lg text-sm">
                  <span className="text-apex-600 font-medium">Current: </span>
                  <span className="text-apex-700">{agent.currentTask}</span>
                </div>
              )}

              {/* Metrics */}
              <div className="mt-4 grid grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.metrics.tasksCompleted}
                  </p>
                  <p className="text-xs text-gray-500">Completed</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.metrics.tasksFailed}
                  </p>
                  <p className="text-xs text-gray-500">Failed</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.metrics.successRate}%
                  </p>
                  <p className="text-xs text-gray-500">Success</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-900">
                    {agent.metrics.avgDuration}s
                  </p>
                  <p className="text-xs text-gray-500">Avg Time</p>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100">
                <span className="text-xs text-gray-400">
                  Last activity: {new Date(agent.lastActivity).toLocaleString()}
                </span>
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  {agent.status === 'stopped' || agent.status === 'idle' ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-success-500 hover:bg-success-50"
                      icon={<PlayIcon className="h-4 w-4" />}
                      onClick={() => onStartAgent(agent.id)}
                    >
                      Start
                    </Button>
                  ) : agent.status === 'running' ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-warning-500 hover:bg-warning-50"
                      icon={<StopIcon className="h-4 w-4" />}
                      onClick={() => onStopAgent(agent.id)}
                    >
                      Stop
                    </Button>
                  ) : null}

                  {agent.status === 'error' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-apex-500 hover:bg-apex-50"
                      icon={<ArrowPathIcon className="h-4 w-4" />}
                      onClick={() => onRestartAgent(agent.id)}
                    >
                      Restart
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {agents.length === 0 && (
          <div className="text-center py-12">
            <CpuChipIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No agents configured</p>
            <p className="text-sm text-gray-400 mt-1">
              Deploy a runbook to create agents
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMonitor;
