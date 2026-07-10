/**
 * Playbook Editor - Main component for creating/editing playbooks
 * Part of Apex Canvas
 */

import React, { useState, useCallback } from 'react';
import { Button, Card, CardHeader, Input, TextArea, Select, Badge } from '../common';
import { PlusIcon, TrashIcon, PlayIcon, DocumentCheckIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface Action {
  id: string;
  name: string;
  action_id: string;
  description: string;
  required: boolean;
}

interface PlaybookData {
  name: string;
  description: string;
  intent: string;
  recipe: string;
  actions: Action[];
  triggers: any[];
}

interface PlaybookEditorProps {
  initialData?: Partial<PlaybookData>;
  onSave: (data: PlaybookData) => void;
  onDeploy?: (data: PlaybookData) => void;
  onTest?: (data: PlaybookData) => void;
  availableActions: { id: string; name: string; description: string }[];
}

export const PlaybookEditor: React.FC<PlaybookEditorProps> = ({
  initialData,
  onSave,
  onDeploy,
  onTest,
  availableActions,
}) => {
  const [data, setData] = useState<PlaybookData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    intent: initialData?.intent || '',
    recipe: initialData?.recipe || '',
    actions: initialData?.actions || [],
    triggers: initialData?.triggers || [],
  });

  const [activeTab, setActiveTab] = useState<'intent' | 'recipe' | 'actions' | 'triggers'>('intent');
  const [isDirty, setIsDirty] = useState(false);

  const updateField = useCallback((field: keyof PlaybookData, value: any) => {
    setData((prev) => ({ ...prev, [field]: value }));
    setIsDirty(true);
  }, []);

  const addAction = useCallback(() => {
    const newAction: Action = {
      id: `action-${Date.now()}`,
      name: '',
      action_id: '',
      description: '',
      required: true,
    };
    updateField('actions', [...data.actions, newAction]);
  }, [data.actions, updateField]);

  const updateAction = useCallback((id: string, updates: Partial<Action>) => {
    updateField(
      'actions',
      data.actions.map((a) => (a.id === id ? { ...a, ...updates } : a))
    );
  }, [data.actions, updateField]);

  const removeAction = useCallback((id: string) => {
    updateField(
      'actions',
      data.actions.filter((a) => a.id !== id)
    );
  }, [data.actions, updateField]);

  const tabs = [
    { id: 'intent', label: 'Intent & Output', icon: '1' },
    { id: 'recipe', label: 'Recipe', icon: '2' },
    { id: 'actions', label: 'Actions', icon: '3' },
    { id: 'triggers', label: 'Triggers', icon: '4' },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Playbook Name"
            value={data.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="text-lg font-semibold border-none shadow-none focus:ring-0"
          />
        </div>
        <div className="flex items-center gap-3">
          {isDirty && (
            <Badge variant="warning" size="sm">Unsaved changes</Badge>
          )}
          <Button
            variant="ghost"
            size="sm"
            icon={<PlayIcon className="h-4 w-4" />}
            onClick={() => onTest?.(data)}
          >
            Test
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              onSave(data);
              setIsDirty(false);
            }}
          >
            Save Draft
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={<DocumentCheckIcon className="h-4 w-4" />}
            onClick={() => onDeploy?.(data)}
          >
            Deploy
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50 px-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={clsx(
              'flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === tab.id
                ? 'border-apex-600 text-apex-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            )}
          >
            <span className={clsx(
              'w-5 h-5 rounded-full text-xs flex items-center justify-center',
              activeTab === tab.id ? 'bg-apex-600 text-white' : 'bg-gray-300 text-white'
            )}>
              {tab.icon}
            </span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        {activeTab === 'intent' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <Card>
              <CardHeader
                title="Intent"
                subtitle="Describe what this playbook should accomplish in plain English"
              />
              <TextArea
                placeholder="e.g., Process incoming vendor invoices by extracting data, validating against purchase orders, checking compliance rules, and routing for appropriate approval..."
                value={data.intent}
                onChange={(e) => updateField('intent', e.target.value)}
                rows={6}
                className="font-mono text-sm"
              />
            </Card>

            <Card>
              <CardHeader
                title="Description"
                subtitle="A brief summary of this playbook for the catalog"
              />
              <TextArea
                placeholder="e.g., Automated invoice processing workflow for accounts payable"
                value={data.description}
                onChange={(e) => updateField('description', e.target.value)}
                rows={3}
              />
            </Card>
          </div>
        )}

        {activeTab === 'recipe' && (
          <div className="max-w-4xl mx-auto">
            <Card>
              <CardHeader
                title="Recipe"
                subtitle="Step-by-step instructions in natural language (Markdown supported)"
              />
              <TextArea
                placeholder={`## Workflow Steps

### Step 1: Document Extraction
When a new invoice arrives:
1. Use the \`invoice_extract\` action to extract structured data
2. Wait for extraction to complete
3. Validate that key fields were extracted

### Step 2: Vendor Validation
With the extracted vendor information:
1. Use \`vendor_lookup\` to find the vendor in our database
2. If vendor not found, route to onboarding workflow
...`}
                value={data.recipe}
                onChange={(e) => updateField('recipe', e.target.value)}
                rows={24}
                className="font-mono text-sm"
              />
            </Card>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="max-w-4xl mx-auto space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Available Actions</h2>
              <Button
                variant="primary"
                size="sm"
                icon={<PlusIcon className="h-4 w-4" />}
                onClick={addAction}
              >
                Add Action
              </Button>
            </div>

            {data.actions.length === 0 ? (
              <Card className="text-center py-12">
                <p className="text-gray-500">No actions added yet.</p>
                <p className="text-sm text-gray-400 mt-1">
                  Actions are the tools your agent can use to complete tasks.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  icon={<PlusIcon className="h-4 w-4" />}
                  onClick={addAction}
                >
                  Add First Action
                </Button>
              </Card>
            ) : (
              data.actions.map((action, index) => (
                <Card key={action.id} className="relative">
                  <button
                    onClick={() => removeAction(action.id)}
                    className="absolute top-4 right-4 text-gray-400 hover:text-danger-500"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>

                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Action Name"
                      placeholder="e.g., extract_invoice"
                      value={action.name}
                      onChange={(e) => updateAction(action.id, { name: e.target.value })}
                    />
                    <Select
                      label="Action ID"
                      value={action.action_id}
                      onChange={(e) => updateAction(action.id, { action_id: e.target.value })}
                      options={[
                        { value: '', label: 'Select an action...' },
                        ...availableActions.map((a) => ({
                          value: a.id,
                          label: `${a.name} - ${a.description}`,
                        })),
                      ]}
                    />
                  </div>

                  <div className="mt-4">
                    <TextArea
                      label="Description"
                      placeholder="When should this action be used?"
                      value={action.description}
                      onChange={(e) => updateAction(action.id, { description: e.target.value })}
                      rows={2}
                    />
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    <input
                      type="checkbox"
                      id={`required-${action.id}`}
                      checked={action.required}
                      onChange={(e) => updateAction(action.id, { required: e.target.checked })}
                      className="rounded border-gray-300 text-apex-600 focus:ring-apex-500"
                    />
                    <label htmlFor={`required-${action.id}`} className="text-sm text-gray-600">
                      Required action (must be executed)
                    </label>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'triggers' && (
          <div className="max-w-3xl mx-auto">
            <Card>
              <CardHeader
                title="Triggers"
                subtitle="How this playbook gets activated"
              />
              <div className="space-y-4">
                <div className="p-4 border border-dashed border-gray-300 rounded-lg text-center">
                  <p className="text-gray-500">Trigger configuration coming soon</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Support for S3 events, API calls, schedules, and workflow events
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaybookEditor;
