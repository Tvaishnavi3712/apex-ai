/**
 * BlueprintDesigner - Main component for creating/editing BDA blueprints
 * Part of Apex Studio
 *
 * Enhanced with Document Intelligence features:
 * - Visual Annotation UI for PDF field marking
 * - AI Schema Generation from sample documents
 * - Virtual Columns/Tables for computed fields
 */
import React, { useState, useCallback } from 'react';
import { Button, Card, CardHeader, Input, TextArea, Select, Badge } from '../common';
import {
  DocumentCheckIcon,
  PlayIcon,
  BeakerIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { FieldList } from './FieldList';
import { RuleBuilder } from './RuleBuilder';
import { BlueprintPreview } from './BlueprintPreview';
import { AnnotationPanel } from './AnnotationPanel';
import { VirtualFieldsPanel } from './VirtualFieldsPanel';
import { SchemaGenerateModal } from './SchemaGenerateModal';
import {
  Blueprint,
  BlueprintField,
  ArrayFieldDefinition,
  BlueprintDesignerProps,
  FieldAnnotation,
  VirtualColumn,
  VirtualTable,
} from './types';
import { v4 as uuidv4 } from 'uuid';

const DOCUMENT_TYPES = [
  { value: 'invoice', label: 'Invoice' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'bank_statement', label: 'Bank Statement' },
  { value: 'contract', label: 'Contract' },
  { value: 'resume', label: 'Resume/CV' },
  { value: 'form', label: 'Form' },
  { value: 'report', label: 'Report' },
  { value: 'insurance_application', label: 'Insurance Application' },
  { value: 'underwriting_submission', label: 'Underwriting Submission' },
  { value: 'policy_document', label: 'Policy Document' },
  { value: 'claim_form', label: 'Claim Form' },
  { value: 'medical_record', label: 'Medical Record' },
  { value: 'financial_statement', label: 'Financial Statement' },
  { value: 'property_appraisal', label: 'Property Appraisal' },
  { value: 'other', label: 'Other' },
];

const INDUSTRIES = [
  { value: 'financial_services', label: 'Financial Services' },
  { value: 'insurance_underwriting', label: 'Insurance Underwriting' },
  { value: 'insurance_commercial', label: 'Commercial Insurance' },
  { value: 'insurance_personal', label: 'Personal Lines Insurance' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'hr', label: 'Human Resources' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'healthcare_payers', label: 'Healthcare Payers' },
  { value: 'retail', label: 'Retail' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'logistics', label: 'Logistics' },
  { value: 'general', label: 'General' },
];

export const BlueprintDesigner: React.FC<BlueprintDesignerProps> = ({
  initialData,
  onSave,
  onDeploy,
  onTest,
  isLoading = false,
}) => {
  const [blueprint, setBlueprint] = useState<Blueprint>({
    id: initialData?.id || uuidv4(),
    name: initialData?.name || '',
    description: initialData?.description || '',
    documentType: initialData?.documentType || 'invoice',
    industry: initialData?.industry || 'financial_services',
    stage: initialData?.stage || 'DEVELOPMENT',
    fields: initialData?.fields || [],
    definitions: initialData?.definitions || [],
    createdAt: initialData?.createdAt,
    updatedAt: initialData?.updatedAt,
  });

  const [activeTab, setActiveTab] = useState<'definition' | 'fields' | 'virtual' | 'annotate' | 'rules' | 'preview'>(
    'definition'
  );
  const [isDirty, setIsDirty] = useState(false);
  const [testDocumentUri, setTestDocumentUri] = useState('');
  const [showTestModal, setShowTestModal] = useState(false);

  // Document Intelligence state
  const [showSchemaGenerateModal, setShowSchemaGenerateModal] = useState(false);
  const [annotations, setAnnotations] = useState<FieldAnnotation[]>(initialData?.annotations || []);
  const [virtualColumns, setVirtualColumns] = useState<VirtualColumn[]>(initialData?.virtualColumns || []);
  const [virtualTables, setVirtualTables] = useState<VirtualTable[]>(initialData?.virtualTables || []);
  const [sampleDocumentUrl, setSampleDocumentUrl] = useState<string | undefined>(initialData?.sampleDocumentUrl);
  const [isUploadingSample, setIsUploadingSample] = useState(false);

  const updateField = useCallback(<K extends keyof Blueprint>(key: K, value: Blueprint[K]) => {
    setBlueprint((prev) => ({ ...prev, [key]: value }));
    setIsDirty(true);
  }, []);

  const handleFieldsChange = useCallback(
    (fields: BlueprintField[]) => {
      updateField('fields', fields);
    },
    [updateField]
  );

  // Handle AI-generated schema acceptance
  const handleSchemaAccept = useCallback(
    (fields: BlueprintField[], definitions: ArrayFieldDefinition[]) => {
      updateField('fields', [...blueprint.fields, ...fields]);
      if (definitions.length > 0) {
        updateField('definitions', [...blueprint.definitions, ...definitions]);
      }
    },
    [blueprint.fields, blueprint.definitions, updateField]
  );

  // Handle annotations change
  const handleAnnotationsChange = useCallback((newAnnotations: FieldAnnotation[]) => {
    setAnnotations(newAnnotations);
    setIsDirty(true);
  }, []);

  // Handle virtual columns change
  const handleVirtualColumnsChange = useCallback((columns: VirtualColumn[]) => {
    setVirtualColumns(columns);
    setIsDirty(true);
  }, []);

  // Handle virtual tables change
  const handleVirtualTablesChange = useCallback((tables: VirtualTable[]) => {
    setVirtualTables(tables);
    setIsDirty(true);
  }, []);

  // Handle sample document upload
  const handleUploadSample = useCallback(async (file: File) => {
    setIsUploadingSample(true);
    try {
      // Create a local URL for preview
      const url = URL.createObjectURL(file);
      setSampleDocumentUrl(url);
      setIsDirty(true);
    } finally {
      setIsUploadingSample(false);
    }
  }, []);

  const handleSave = () => {
    const updatedBlueprint = {
      ...blueprint,
      virtualColumns,
      virtualTables,
      annotations,
      sampleDocumentUrl,
      updatedAt: new Date().toISOString(),
    };
    onSave?.(updatedBlueprint);
    setIsDirty(false);
  };

  const handleDeploy = () => {
    onDeploy?.(blueprint);
  };

  const handleTest = () => {
    if (testDocumentUri) {
      onTest?.(blueprint, testDocumentUri);
      setShowTestModal(false);
    }
  };

  const tabs = [
    { id: 'definition', label: 'Definition', icon: '1' },
    { id: 'fields', label: 'Fields', icon: '2' },
    { id: 'virtual', label: 'Virtual Fields', icon: '3' },
    { id: 'annotate', label: 'Annotate', icon: '4' },
    { id: 'rules', label: 'Rules', icon: '5' },
    { id: 'preview', label: 'Preview', icon: '6' },
  ];

  const isValid = blueprint.name.trim() !== '' && blueprint.fields.length > 0;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Blueprint Name"
            value={blueprint.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="text-lg font-semibold border-none shadow-none focus:ring-0"
          />
        </div>
        <div className="flex items-center gap-3">
          <Badge
            variant={blueprint.stage === 'LIVE' ? 'success' : 'warning'}
          >
            {blueprint.stage}
          </Badge>
          {isDirty && <Badge variant="warning">Unsaved changes</Badge>}
          <Button
            variant="ghost"
            size="sm"
            icon={<BeakerIcon className="h-4 w-4" />}
            onClick={() => setShowTestModal(true)}
            disabled={!isValid}
          >
            Test
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={<DocumentCheckIcon className="h-4 w-4" />}
            onClick={handleDeploy}
            disabled={!isValid || isLoading}
          >
            Deploy to BDA
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50 px-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={clsx(
              'flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === tab.id
                ? 'border-apex-600 text-apex-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            )}
          >
            <span
              className={clsx(
                'w-5 h-5 rounded-full text-xs flex items-center justify-center',
                activeTab === tab.id ? 'bg-apex-600 text-white' : 'bg-gray-300 text-white'
              )}
            >
              {tab.icon}
            </span>
            {tab.label}
            {tab.id === 'fields' && blueprint.fields.length > 0 && (
              <span className="ml-1 px-2 py-0.5 text-xs bg-gray-200 rounded-full">
                {blueprint.fields.length}
              </span>
            )}
            {tab.id === 'virtual' && (virtualColumns.length + virtualTables.length) > 0 && (
              <span className="ml-1 px-2 py-0.5 text-xs bg-apex-100 text-apex-700 rounded-full">
                {virtualColumns.length + virtualTables.length}
              </span>
            )}
            {tab.id === 'annotate' && annotations.length > 0 && (
              <span className="ml-1 px-2 py-0.5 text-xs bg-green-100 text-green-700 rounded-full">
                {annotations.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        {activeTab === 'definition' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <Card>
              <CardHeader
                title="Blueprint Details"
                subtitle="Basic information about this extraction blueprint"
              />
              <div className="space-y-4">
                <TextArea
                  label="Description"
                  placeholder="Describe what this blueprint extracts, e.g., 'Extracts key financial data from vendor invoices including line items, totals, and payment terms'"
                  value={blueprint.description}
                  onChange={(e) => updateField('description', e.target.value)}
                  rows={3}
                />

                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Document Type"
                    value={blueprint.documentType}
                    onChange={(e) => updateField('documentType', e.target.value)}
                    options={DOCUMENT_TYPES}
                  />
                  <Select
                    label="Industry"
                    value={blueprint.industry}
                    onChange={(e) => updateField('industry', e.target.value)}
                    options={INDUSTRIES}
                  />
                </div>
              </div>
            </Card>

            {/* AI Schema Generation */}
            <Card>
              <CardHeader
                title="AI-Powered Schema Generation"
                subtitle="Upload a sample document and let AI generate the extraction schema"
              />
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowSchemaGenerateModal(true)}
                  className="flex items-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-apex-500 hover:bg-apex-50 transition-colors text-left flex-1"
                >
                  <SparklesIcon className="h-8 w-8 text-apex-500" />
                  <div>
                    <div className="font-medium text-gray-900">Generate from Sample</div>
                    <div className="text-sm text-gray-500">
                      Upload a PDF and auto-generate fields
                    </div>
                  </div>
                </button>
              </div>
            </Card>

            <Card>
              <CardHeader
                title="Quick Start Templates"
                subtitle="Start with a pre-built template for common document types"
              />
              <div className="grid grid-cols-3 gap-3">
                {[
                  {
                    name: 'Invoice',
                    fields: ['invoice_number', 'vendor_name', 'date', 'total_amount', 'line_items'],
                  },
                  {
                    name: 'Receipt',
                    fields: ['merchant_name', 'date', 'items', 'subtotal', 'tax', 'total'],
                  },
                  {
                    name: 'Purchase Order',
                    fields: ['po_number', 'vendor', 'ship_to', 'items', 'total'],
                  },
                ].map((template) => (
                  <button
                    key={template.name}
                    onClick={() => {
                      const newFields: BlueprintField[] = template.fields.map((name) => ({
                        id: uuidv4(),
                        name,
                        type: name.includes('items') ? 'array' : name.includes('amount') || name.includes('total') || name.includes('tax') || name.includes('subtotal') ? 'number' : name.includes('date') ? 'date' : 'string',
                        inferenceType: 'explicit',
                        instruction: `Extract the ${name.replace(/_/g, ' ')} from the document`,
                        required: ['invoice_number', 'po_number', 'total', 'date'].includes(name),
                      }));
                      updateField('fields', [...blueprint.fields, ...newFields]);
                      updateField('documentType', template.name.toLowerCase().replace(' ', '_'));
                    }}
                    className="p-4 border border-gray-200 rounded-lg hover:border-apex-500 hover:bg-apex-50 transition-colors text-left"
                  >
                    <div className="font-medium text-gray-900">{template.name}</div>
                    <div className="text-sm text-gray-500 mt-1">
                      {template.fields.length} fields
                    </div>
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'fields' && (
          <div className="max-w-4xl mx-auto">
            {/* Import Document Banner */}
            {blueprint.fields.length === 0 && (
              <div className="mb-6 p-4 bg-gradient-to-r from-apex-50 to-blue-50 border border-apex-200 rounded-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-apex-100 rounded-lg">
                      <SparklesIcon className="h-6 w-6 text-apex-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Import Document to Auto-Generate Fields</h3>
                      <p className="text-sm text-gray-600">Upload a sample PDF and let AI detect all the fields automatically</p>
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    icon={<SparklesIcon className="h-4 w-4" />}
                    onClick={() => setShowSchemaGenerateModal(true)}
                  >
                    Import Document
                  </Button>
                </div>
              </div>
            )}

            {/* Quick Import Button when fields exist */}
            {blueprint.fields.length > 0 && (
              <div className="mb-4 flex justify-end">
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<SparklesIcon className="h-4 w-4" />}
                  onClick={() => setShowSchemaGenerateModal(true)}
                >
                  Import More Fields from Document
                </Button>
              </div>
            )}

            <FieldList fields={blueprint.fields} onChange={handleFieldsChange} />
          </div>
        )}

        {activeTab === 'virtual' && (
          <div className="max-w-4xl mx-auto">
            <VirtualFieldsPanel
              virtualColumns={virtualColumns}
              virtualTables={virtualTables}
              fields={blueprint.fields}
              onVirtualColumnsChange={handleVirtualColumnsChange}
              onVirtualTablesChange={handleVirtualTablesChange}
            />
          </div>
        )}

        {activeTab === 'annotate' && (
          <div className="h-full -m-6">
            <AnnotationPanel
              sampleDocumentUrl={sampleDocumentUrl}
              annotations={annotations}
              fields={blueprint.fields}
              onAnnotationsChange={handleAnnotationsChange}
              onUploadSample={handleUploadSample}
              isUploading={isUploadingSample}
            />
          </div>
        )}

        {activeTab === 'rules' && (
          <div className="max-w-4xl mx-auto">
            <RuleBuilder fields={blueprint.fields} onChange={handleFieldsChange} />
          </div>
        )}

        {activeTab === 'preview' && (
          <div className="max-w-4xl mx-auto">
            <BlueprintPreview blueprint={blueprint} />
          </div>
        )}
      </div>

      {/* Test Modal */}
      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Test Blueprint</h3>
            <Input
              label="Document S3 URI"
              placeholder="s3://bucket/path/to/document.pdf"
              value={testDocumentUri}
              onChange={(e) => setTestDocumentUri(e.target.value)}
              hint="Enter the S3 URI of a document to test extraction"
            />
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="ghost" onClick={() => setShowTestModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleTest}
                disabled={!testDocumentUri}
                icon={<PlayIcon className="h-4 w-4" />}
              >
                Run Test
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Schema Generate Modal */}
      <SchemaGenerateModal
        isOpen={showSchemaGenerateModal}
        onClose={() => setShowSchemaGenerateModal(false)}
        onAccept={handleSchemaAccept}
      />
    </div>
  );
};

export default BlueprintDesigner;
