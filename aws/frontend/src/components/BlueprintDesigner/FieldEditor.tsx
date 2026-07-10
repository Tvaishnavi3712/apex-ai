/**
 * FieldEditor Component - Edit individual blueprint field configuration
 */
import React from 'react';
import { BlueprintField, FieldType, InferenceType } from './types';
import { Input, Select, TextArea } from '../common';
import { TrashIcon } from '@heroicons/react/24/outline';

interface FieldEditorProps {
  field: BlueprintField;
  onChange: (field: BlueprintField) => void;
  onDelete: () => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

const FIELD_TYPES: { value: FieldType; label: string }[] = [
  { value: 'string', label: 'Text' },
  { value: 'number', label: 'Number' },
  { value: 'boolean', label: 'Boolean' },
  { value: 'date', label: 'Date' },
  { value: 'array', label: 'Array' },
  { value: 'object', label: 'Object' },
];

const INFERENCE_TYPES: { value: InferenceType; label: string }[] = [
  { value: 'explicit', label: 'Explicit - Extract directly from document' },
  { value: 'inferred', label: 'Inferred - AI determines value' },
];

export const FieldEditor: React.FC<FieldEditorProps> = ({
  field,
  onChange,
  onDelete,
  isExpanded = false,
  onToggleExpand,
}) => {
  const handleChange = (key: keyof BlueprintField, value: any) => {
    onChange({ ...field, [key]: value });
  };

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      {/* Collapsed Header */}
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50"
        onClick={onToggleExpand}
      >
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-apex-500" />
          <span className="font-medium text-gray-900">{field.name || 'Untitled Field'}</span>
          <span className="text-sm text-gray-500">({field.type})</span>
          {field.required && (
            <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded">Required</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="p-1 text-gray-400 hover:text-red-500 transition-colors"
            title="Delete field"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 py-4 border-t border-gray-200 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Field Name"
              value={field.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., invoice_number"
              hint="Use snake_case for field names"
            />
            <Select
              label="Field Type"
              value={field.type}
              onChange={(e) => handleChange('type', e.target.value as FieldType)}
              options={FIELD_TYPES}
            />
          </div>

          <Select
            label="Inference Type"
            value={field.inferenceType}
            onChange={(e) => handleChange('inferenceType', e.target.value as InferenceType)}
            options={INFERENCE_TYPES}
          />

          <TextArea
            label="Extraction Instruction"
            value={field.instruction}
            onChange={(e) => handleChange('instruction', e.target.value)}
            placeholder="Describe what this field should extract, e.g., 'The unique invoice identifier or number'"
            rows={2}
          />

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id={`required-${field.id}`}
              checked={field.required}
              onChange={(e) => handleChange('required', e.target.checked)}
              className="w-4 h-4 text-apex-600 border-gray-300 rounded focus:ring-apex-500"
            />
            <label htmlFor={`required-${field.id}`} className="text-sm text-gray-700">
              Required field
            </label>
          </div>

          {/* Validation Section */}
          {field.type === 'string' && (
            <div className="pt-2 border-t border-gray-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Validation (Optional)
              </label>
              <Input
                placeholder="Regex pattern, e.g., ^INV-[0-9]+$"
                value={field.validation?.value as string || ''}
                onChange={(e) => handleChange('validation', {
                  type: 'pattern',
                  value: e.target.value,
                })}
              />
            </div>
          )}

          {field.type === 'number' && (
            <div className="pt-2 border-t border-gray-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Range Validation (Optional)
              </label>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Minimum"
                  type="number"
                  placeholder="Min value"
                  onChange={(e) => handleChange('validation', {
                    type: 'min',
                    value: parseFloat(e.target.value),
                  })}
                />
                <Input
                  label="Maximum"
                  type="number"
                  placeholder="Max value"
                  onChange={(e) => handleChange('validation', {
                    type: 'max',
                    value: parseFloat(e.target.value),
                  })}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FieldEditor;
