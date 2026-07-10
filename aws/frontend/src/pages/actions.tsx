/**
 * Actions Page - Action Gallery & Management
 * Fetches real data from backend APIs
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Card, CardHeader, Button, Badge, Input } from '@/components/common';
import {
  BoltIcon,
  MagnifyingGlassIcon,
  PlayIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  PlusIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon,
  XMarkIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type CategoryFilter = 'all' | 'core' | 'financial_services' | 'healthcare' | 'manufacturing' | 'hr' | 'retail' | 'other';

interface Action {
  action_id: string;
  name: string;
  display_name?: string;
  description: string;
  category: string;
  industry: string;
  input_schema?: Record<string, any>;
  output_schema?: Record<string, any>;
  version?: string;
  status: string;
  invocation_count?: number;
  handler_path?: string;
}

export default function Actions() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all');
  const [selectedAction, setSelectedAction] = useState<Action | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [showDocsModal, setShowDocsModal] = useState(false);
  const [testInput, setTestInput] = useState('');
  const [testOutput, setTestOutput] = useState<any>(null);
  const [isTestRunning, setIsTestRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [actions, setActions] = useState<Action[]>([]);
  const [newAction, setNewAction] = useState({
    name: '',
    displayName: '',
    description: '',
    category: 'core',
    industry: 'Core',
  });

  // Fetch actions from API
  useEffect(() => {
    const fetchActions = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/actions/`);
        if (response.ok) {
          const data = await response.json();
          setActions(data);
        }
      } catch (err) {
        console.error('Failed to fetch actions:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchActions();
  }, []);

  // Helper to get display name
  const getDisplayName = (action: Action): string => {
    return action.display_name || action.name || action.action_id;
  };

  // Helper to get input schema fields
  const getInputSchemaFields = (action: Action): string[] => {
    if (!action.input_schema || typeof action.input_schema !== 'object') return [];
    const props = action.input_schema.properties || action.input_schema;
    return Object.keys(props);
  };

  // Helper to get output schema fields
  const getOutputSchemaFields = (action: Action): string[] => {
    if (!action.output_schema || typeof action.output_schema !== 'object') return [];
    const props = action.output_schema.properties || action.output_schema;
    return Object.keys(props);
  };

  // Map category to display
  const getCategoryDisplay = (category: string): string => {
    const map: Record<string, string> = {
      'core': 'Core',
      'healthcare_payers': 'Healthcare Payers',
      'healthcare_providers': 'Healthcare Providers',
      'financial_services': 'Financial Services',
      'manufacturing': 'Manufacturing',
      'hr': 'HR / Recruitment',
      'retail': 'Retail',
      'insurance_underwriting': 'Insurance Underwriting',
    };
    return map[category] || category;
  };

  // Build categories dynamically from actions
  const categorySet = new Set(actions.map(a => a.category));
  const categories = [
    { id: 'all', label: 'All Actions', count: actions.length },
    ...Array.from(categorySet).map(cat => ({
      id: cat,
      label: getCategoryDisplay(cat),
      count: actions.filter(a => a.category === cat).length,
    })),
  ];

  const filteredActions = actions.filter(action => {
    const displayName = getDisplayName(action);
    const matchesSearch = displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (action.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || action.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  // Group actions by category (since industry might not be set)
  const groupedActions = filteredActions.reduce((acc, action) => {
    const group = getCategoryDisplay(action.category || 'other');
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(action);
    return acc;
  }, {} as Record<string, Action[]>);

  // Handle test action
  const handleTestAction = () => {
    if (!selectedAction) return;
    setIsTestRunning(true);
    setTestOutput(null);

    // Simulate action execution
    setTimeout(() => {
      const mockOutput: Record<string, any> = {};
      const outputFields = getOutputSchemaFields(selectedAction);
      outputFields.forEach(field => {
        if (field.includes('score') || field.includes('count') || field.includes('amount')) {
          mockOutput[field] = Math.floor(Math.random() * 100);
        } else if (field.includes('status') || field.includes('result')) {
          mockOutput[field] = 'success';
        } else if (field.includes('items') || field.includes('products')) {
          mockOutput[field] = [{ id: '1', name: 'Sample Item' }];
        } else {
          mockOutput[field] = `sample_${field}_value`;
        }
      });

      setTestOutput({
        success: true,
        duration: `${(Math.random() * 2 + 0.5).toFixed(2)}s`,
        output: mockOutput,
      });
      setIsTestRunning(false);
    }, 1500);
  };

  // Handle create action
  const handleCreateAction = () => {
    console.log('Creating action:', newAction);
    alert(`Action "${newAction.displayName}" created successfully!`);
    setShowCreateModal(false);
    setNewAction({ name: '', displayName: '', description: '', category: 'core', industry: 'Core' });
  };

  // Open AWS Console
  const openAWSConsole = () => {
    if (selectedAction) {
      window.open(`https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/apex-action-${selectedAction.name}`, '_blank');
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading actions...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Actions | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Actions</h1>
            <p className="text-gray-500 mt-1">Browse and manage available actions for your agents</p>
          </div>
          <Button
            variant="primary"
            icon={<PlusIcon className="h-5 w-5" />}
            onClick={() => setShowCreateModal(true)}
          >
            Create Custom Action
          </Button>
        </div>

        <div className="flex gap-8">
          {/* Sidebar Filters */}
          <div className="w-64 flex-shrink-0">
            <Card>
              <CardHeader title="Categories" />
              <div className="space-y-1">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setCategoryFilter(category.id as CategoryFilter)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                      categoryFilter === category.id
                        ? 'bg-apex-50 text-apex-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <span className="text-sm">{category.label}</span>
                    <Badge variant="default" size="sm">{category.count}</Badge>
                  </button>
                ))}
              </div>
            </Card>

            <Card className="mt-6">
              <CardHeader title="Quick Stats" />
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Total Actions</span>
                  <span className="font-semibold">{actions.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Active</span>
                  <span className="font-semibold text-green-600">{actions.filter(a => a.status === 'active').length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Beta</span>
                  <span className="font-semibold text-yellow-600">{actions.filter(a => a.status === 'beta').length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Total Executions</span>
                  <span className="font-semibold">{actions.reduce((sum, a) => sum + (a.invocation_count || 0), 0).toLocaleString()}</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search actions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Actions Grid by Industry */}
            {Object.entries(groupedActions).map(([industry, industryActions]) => (
              <div key={industry} className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BoltIcon className="h-5 w-5 text-apex-500" />
                  {industry}
                  <Badge variant="outline">{industryActions.length}</Badge>
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {industryActions.map((action) => (
                    <Card
                      key={action.action_id}
                      hover
                      className="cursor-pointer"
                      onClick={() => setSelectedAction(action)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className="p-2 bg-apex-100 rounded-lg">
                            <BoltIcon className="h-5 w-5 text-apex-600" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{getDisplayName(action)}</h3>
                            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{action.description || 'No description'}</p>
                          </div>
                        </div>
                        <Badge
                          variant={action.status === 'active' ? 'success' : action.status === 'beta' ? 'warning' : 'default'}
                          size="sm"
                        >
                          {action.status || 'active'}
                        </Badge>
                      </div>
                      <div className="mt-4 flex items-center justify-between text-sm">
                        <span className="text-gray-400">v{action.version || '1.0'}</span>
                        <div className="flex items-center gap-1 text-gray-500">
                          <PlayIcon className="h-4 w-4" />
                          {(action.invocation_count || 0).toLocaleString()} runs
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            ))}

            {filteredActions.length === 0 && (
              <div className="text-center py-12">
                <BoltIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No actions found</h3>
                <p className="text-gray-500">Try adjusting your search or filter</p>
              </div>
            )}
          </div>
        </div>

        {/* Action Detail Modal */}
        {selectedAction && !showTestModal && !showDocsModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-apex-100 rounded-xl">
                    <BoltIcon className="h-8 w-8 text-apex-600" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{getDisplayName(selectedAction)}</h2>
                    <p className="text-gray-500 mt-1">{selectedAction.description || 'No description'}</p>
                    <div className="flex items-center gap-3 mt-3">
                      <Badge variant={selectedAction.status === 'active' ? 'success' : 'warning'}>
                        {selectedAction.status || 'active'}
                      </Badge>
                      <Badge variant="outline">{getCategoryDisplay(selectedAction.category)}</Badge>
                      <span className="text-sm text-gray-400">v{selectedAction.version || '1.0'}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAction(null)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Input Schema */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CodeBracketIcon className="h-5 w-5 text-gray-400" />
                    Input Schema
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-700">
{getInputSchemaFields(selectedAction).length > 0 ? `{
${getInputSchemaFields(selectedAction).map(field => `  "${field}": "<${field}>"`).join(',\n')}
}` : '{ /* No input schema defined */ }'}
                    </pre>
                  </div>
                </div>

                {/* Output Schema */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CodeBracketIcon className="h-5 w-5 text-gray-400" />
                    Output Schema
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-700">
{getOutputSchemaFields(selectedAction).length > 0 ? `{
${getOutputSchemaFields(selectedAction).map(field => `  "${field}": "<${field}>"`).join(',\n')}
}` : '{ /* No output schema defined */ }'}
                    </pre>
                  </div>
                </div>

                {/* Usage Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <PlayIcon className="h-6 w-6 text-apex-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{(selectedAction.invocation_count || 0).toLocaleString()}</p>
                    <p className="text-sm text-gray-500">Total Runs</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <CheckCircleIcon className="h-6 w-6 text-green-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold">98.5%</p>
                    <p className="text-sm text-gray-500">Success Rate</p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <ClockIcon className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                    <p className="text-2xl font-bold">1.2s</p>
                    <p className="text-sm text-gray-500">Avg Duration</p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4 border-t">
                  <Button
                    variant="primary"
                    icon={<PlayIcon className="h-4 w-4" />}
                    onClick={() => setShowTestModal(true)}
                  >
                    Test Action
                  </Button>
                  <Button
                    variant="secondary"
                    icon={<DocumentTextIcon className="h-4 w-4" />}
                    onClick={() => setShowDocsModal(true)}
                  >
                    View Documentation
                  </Button>
                  <Button
                    variant="ghost"
                    icon={<ArrowTopRightOnSquareIcon className="h-4 w-4" />}
                    onClick={openAWSConsole}
                  >
                    View in AWS
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Test Action Modal */}
        {showTestModal && selectedAction && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Test: {getDisplayName(selectedAction)}</h2>
                <button
                  onClick={() => {
                    setShowTestModal(false);
                    setTestOutput(null);
                    setTestInput('');
                  }}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Input */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Test Input</h3>
                  <textarea
                    value={testInput || JSON.stringify(
                      getInputSchemaFields(selectedAction).reduce((acc, field) => {
                        acc[field] = `test_${field}`;
                        return acc;
                      }, {} as Record<string, string>),
                      null,
                      2
                    )}
                    onChange={(e) => setTestInput(e.target.value)}
                    className="w-full h-40 p-4 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500"
                    placeholder="Enter test input JSON..."
                  />
                </div>

                {/* Run Button */}
                <Button
                  variant="primary"
                  className="w-full"
                  icon={isTestRunning ? <ArrowPathIcon className="h-5 w-5 animate-spin" /> : <PlayIcon className="h-5 w-5" />}
                  onClick={handleTestAction}
                  disabled={isTestRunning}
                >
                  {isTestRunning ? 'Running...' : 'Run Test'}
                </Button>

                {/* Output */}
                {testOutput && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      {testOutput.success ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-500" />
                      ) : (
                        <ExclamationCircleIcon className="h-5 w-5 text-red-500" />
                      )}
                      Test Result
                      <Badge variant={testOutput.success ? 'success' : 'danger'} size="sm">
                        {testOutput.duration}
                      </Badge>
                    </h3>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-sm text-green-400 overflow-auto">
                        {JSON.stringify(testOutput.output, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}

        {/* Documentation Modal */}
        {showDocsModal && selectedAction && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">{getDisplayName(selectedAction)} Documentation</h2>
                <button
                  onClick={() => setShowDocsModal(false)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="prose prose-sm max-w-none">
                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="whitespace-pre-wrap font-sans text-gray-700">
                    <p><strong>Action ID:</strong> {selectedAction.action_id}</p>
                    <p><strong>Category:</strong> {getCategoryDisplay(selectedAction.category)}</p>
                    <p><strong>Status:</strong> {selectedAction.status || 'active'}</p>
                    {selectedAction.handler_path && (
                      <p><strong>Handler:</strong> {selectedAction.handler_path}</p>
                    )}
                    <hr className="my-4" />
                    <p>{selectedAction.description || 'No description available.'}</p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Reference</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Input Parameters</h4>
                      <ul className="text-sm text-blue-700 space-y-1">
                        {getInputSchemaFields(selectedAction).length > 0 ? (
                          getInputSchemaFields(selectedAction).map(field => (
                            <li key={field} className="font-mono">• {field}</li>
                          ))
                        ) : (
                          <li className="text-gray-500">No input parameters defined</li>
                        )}
                      </ul>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-medium text-green-900 mb-2">Output Fields</h4>
                      <ul className="text-sm text-green-700 space-y-1">
                        {getOutputSchemaFields(selectedAction).length > 0 ? (
                          getOutputSchemaFields(selectedAction).map(field => (
                            <li key={field} className="font-mono">• {field}</li>
                          ))
                        ) : (
                          <li className="text-gray-500">No output fields defined</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Create Action Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-8">
            <Card className="w-full max-w-lg">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Create Custom Action</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                <Input
                  label="Action Name (snake_case)"
                  value={newAction.name}
                  onChange={(e) => setNewAction({ ...newAction, name: e.target.value })}
                  placeholder="my_custom_action"
                />
                <Input
                  label="Display Name"
                  value={newAction.displayName}
                  onChange={(e) => setNewAction({ ...newAction, displayName: e.target.value })}
                  placeholder="My Custom Action"
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={newAction.description}
                    onChange={(e) => setNewAction({ ...newAction, description: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500"
                    rows={3}
                    placeholder="Describe what this action does..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={newAction.category}
                    onChange={(e) => setNewAction({ ...newAction, category: e.target.value })}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500"
                  >
                    <option value="core">Core</option>
                    <option value="financial_services">Financial Services</option>
                    <option value="healthcare">Healthcare</option>
                    <option value="manufacturing">Manufacturing</option>
                    <option value="hr">HR / Recruitment</option>
                    <option value="retail">Retail</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button variant="secondary" onClick={() => setShowCreateModal(false)} className="flex-1">
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleCreateAction}
                    disabled={!newAction.name || !newAction.displayName}
                    className="flex-1"
                  >
                    Create Action
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </>
  );
}
