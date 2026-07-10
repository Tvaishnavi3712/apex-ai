/**
 * Schema Generate Modal
 * Upload a sample document and let AI generate a blueprint schema
 */

import React, { useState, useCallback } from 'react';
import {
  XMarkIcon,
  ArrowUpTrayIcon,
  SparklesIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { BlueprintField, GeneratedField, ArrayFieldDefinition } from './types';

interface SchemaGenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: (fields: BlueprintField[], definitions: ArrayFieldDefinition[]) => void;
  apiBaseUrl?: string;
}

interface GenerationResult {
  documentType: string;
  confidence: number;
  description: string;
  fields: GeneratedField[];
  definitions: ArrayFieldDefinition[];
}

const INDUSTRIES = [
  { value: 'financial_services', label: 'Financial Services' },
  { value: 'healthcare_payers', label: 'Healthcare Payers' },
  { value: 'healthcare_providers', label: 'Healthcare Providers' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'hr', label: 'HR / Recruitment' },
  { value: 'retail', label: 'Retail' },
  { value: 'insurance', label: 'Insurance' },
  { value: 'general', label: 'General' }
];

const DOCUMENT_TYPES = [
  { value: '', label: 'Auto-detect' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'bank_statement', label: 'Bank Statement' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'contract', label: 'Contract' },
  { value: 'resume', label: 'Resume / CV' },
  { value: 'claim', label: 'Claim' }
];

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const SchemaGenerateModal: React.FC<SchemaGenerateModalProps> = ({
  isOpen,
  onClose,
  onAccept,
  apiBaseUrl = API_BASE_URL
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [industry, setIndustry] = useState('general');
  const [documentType, setDocumentType] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set());

  // Handle file selection
  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  }, []);

  // Handle drag and drop
  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.pdf'))) {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please upload a PDF file');
    }
  }, []);

  // Generate schema
  const handleGenerate = useCallback(async () => {
    if (!file) return;

    setIsGenerating(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const params = new URLSearchParams({
        industry,
        ...(documentType && { document_type: documentType })
      });

      const response = await fetch(`${apiBaseUrl}/blueprints/generate-from-sample?${params}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();

      // Transform API response to GenerationResult
      // API returns schema_fields directly (not nested in generated_schema)
      const generatedResult: GenerationResult = {
        documentType: data.document_type || documentType || 'document',
        confidence: 0.85,
        description: data.description || '',
        fields: (data.schema_fields || []).map((f: any) => ({
          name: f.name,
          type: f.type,
          required: f.required || false,
          instruction: f.description || ''
        })),
        definitions: []
      };

      setResult(generatedResult);

      // Select all fields by default
      setSelectedFields(new Set(generatedResult.fields.map(f => f.name)));

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsGenerating(false);
    }
  }, [file, industry, documentType, apiBaseUrl]);

  // Toggle field selection
  const toggleField = useCallback((fieldName: string) => {
    setSelectedFields(prev => {
      const next = new Set(prev);
      if (next.has(fieldName)) {
        next.delete(fieldName);
      } else {
        next.add(fieldName);
      }
      return next;
    });
  }, []);

  // Accept selected fields
  const handleAccept = useCallback(() => {
    if (!result) return;

    // Convert GeneratedFields to BlueprintFields
    const blueprintFields: BlueprintField[] = result.fields
      .filter(f => selectedFields.has(f.name))
      .map((f, index) => ({
        id: `field_${Date.now()}_${index}`,
        name: f.name,
        type: f.type as any,
        inferenceType: 'explicit' as const,
        instruction: f.instruction,
        required: f.required
      }));

    onAccept(blueprintFields, result.definitions);
    onClose();
  }, [result, selectedFields, onAccept, onClose]);

  // Reset modal state
  const handleClose = useCallback(() => {
    setFile(null);
    setResult(null);
    setError(null);
    setSelectedFields(new Set());
    onClose();
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black/50 transition-opacity"
          onClick={handleClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div className="flex items-center space-x-2">
              <SparklesIcon className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold">Generate Schema from Sample</h2>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {!result ? (
              // Upload and configure stage
              <>
                {/* File upload */}
                <div
                  className={`
                    border-2 border-dashed rounded-lg p-8 text-center mb-6
                    ${file ? 'border-blue-300 bg-blue-50' : 'border-gray-300'}
                  `}
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                >
                  {file ? (
                    <div className="flex items-center justify-center space-x-3">
                      <CheckIcon className="w-8 h-8 text-green-500" />
                      <div className="text-left">
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        onClick={() => setFile(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <XMarkIcon className="w-5 h-5" />
                      </button>
                    </div>
                  ) : (
                    <>
                      <ArrowUpTrayIcon className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                      <p className="text-gray-600 mb-2">
                        Drag and drop a PDF file here, or
                      </p>
                      <label className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 cursor-pointer hover:bg-gray-50">
                        Browse files
                        <input
                          type="file"
                          accept=".pdf"
                          className="hidden"
                          onChange={handleFileChange}
                        />
                      </label>
                    </>
                  )}
                </div>

                {/* Options */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Industry
                    </label>
                    <select
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      {INDUSTRIES.map(({ value, label }) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Document Type
                    </label>
                    <select
                      value={documentType}
                      onChange={(e) => setDocumentType(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      {DOCUMENT_TYPES.map(({ value, label }) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Error */}
                {error && (
                  <div className="flex items-center space-x-2 p-4 bg-red-50 text-red-700 rounded-lg mb-6">
                    <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />
                    <span className="text-sm">{error}</span>
                  </div>
                )}
              </>
            ) : (
              // Results stage
              <>
                {/* Detected info */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-sm text-gray-500">Detected Type:</span>
                    <span className="ml-2 font-medium text-gray-900 capitalize">
                      {result.documentType.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="text-sm text-gray-500">Confidence:</span>
                    <span className={`
                      font-medium
                      ${result.confidence >= 0.8 ? 'text-green-600' :
                        result.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600'}
                    `}>
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                </div>

                {/* Generated fields */}
                <div className="border rounded-lg overflow-hidden mb-4">
                  <div className="bg-gray-50 px-4 py-2 border-b">
                    <h4 className="font-medium text-sm text-gray-700">
                      Generated Fields ({selectedFields.size} of {result.fields.length} selected)
                    </h4>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {result.fields.map((field) => (
                      <label
                        key={field.name}
                        className="flex items-start px-4 py-2 border-b last:border-0 hover:bg-gray-50 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={selectedFields.has(field.name)}
                          onChange={() => toggleField(field.name)}
                          className="mt-1 mr-3"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-gray-900">{field.name}</span>
                            <span className="text-xs px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">
                              {field.type}
                            </span>
                            {field.required && (
                              <span className="text-xs px-1.5 py-0.5 bg-red-100 text-red-600 rounded">
                                required
                              </span>
                            )}
                          </div>
                          {field.instruction && (
                            <p className="text-sm text-gray-500 mt-0.5 truncate">
                              {field.instruction}
                            </p>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Selection actions */}
                <div className="flex space-x-2 mb-4">
                  <button
                    onClick={() => setSelectedFields(new Set(result.fields.map(f => f.name)))}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Select All
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    onClick={() => setSelectedFields(new Set())}
                    className="text-sm text-blue-600 hover:text-blue-700"
                  >
                    Deselect All
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50 rounded-b-xl">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 hover:text-gray-900"
            >
              Cancel
            </button>

            {!result ? (
              <button
                onClick={handleGenerate}
                disabled={!file || isGenerating}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-4 h-4 mr-2" />
                    Generate Schema
                  </>
                )}
              </button>
            ) : (
              <div className="flex space-x-3">
                <button
                  onClick={() => setResult(null)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  onClick={handleAccept}
                  disabled={selectedFields.size === 0}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <CheckIcon className="w-4 h-4 mr-2" />
                  Accept Fields ({selectedFields.size})
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemaGenerateModal;
