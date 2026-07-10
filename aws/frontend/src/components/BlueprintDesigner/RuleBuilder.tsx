/**
 * RuleBuilder Component - Manage validation rules for blueprint fields
 */
import React from 'react';
import { BlueprintField, ValidationRule } from './types';
import { Input, Select } from '../common';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

interface RuleBuilderProps {
  fields: BlueprintField[];
  onChange: (fields: BlueprintField[]) => void;
}

const RULE_TYPES: { value: ValidationRule['type']; label: string; description: string }[] = [
  { value: 'pattern', label: 'Pattern Match', description: 'Regex pattern validation' },
  { value: 'min', label: 'Minimum Value', description: 'Minimum numeric value' },
  { value: 'max', label: 'Maximum Value', description: 'Maximum numeric value' },
  { value: 'minLength', label: 'Min Length', description: 'Minimum string length' },
  { value: 'maxLength', label: 'Max Length', description: 'Maximum string length' },
  { value: 'enum', label: 'Allowed Values', description: 'List of allowed values' },
  { value: 'custom', label: 'Custom Rule', description: 'Custom validation expression' },
];

const getApplicableRules = (fieldType: string): ValidationRule['type'][] => {
  switch (fieldType) {
    case 'string':
      return ['pattern', 'minLength', 'maxLength', 'enum'];
    case 'number':
      return ['min', 'max'];
    case 'date':
      return ['min', 'max', 'pattern'];
    case 'array':
      return ['minLength', 'maxLength'];
    default:
      return ['custom'];
  }
};

export const RuleBuilder: React.FC<RuleBuilderProps> = ({ fields, onChange }) => {
  const handleUpdateValidation = (
    fieldIndex: number,
    validation: ValidationRule | undefined
  ) => {
    const newFields = [...fields];
    newFields[fieldIndex] = { ...newFields[fieldIndex], validation };
    onChange(newFields);
  };

  const handleRemoveValidation = (fieldIndex: number) => {
    const newFields = [...fields];
    const { validation, ...fieldWithoutValidation } = newFields[fieldIndex];
    newFields[fieldIndex] = fieldWithoutValidation as BlueprintField;
    onChange(newFields);
  };

  const fieldsWithoutRules = fields.filter((f) => !f.validation);
  const fieldsWithRules = fields.filter((f) => f.validation);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Validation Rules</h3>
        <p className="text-sm text-gray-500">
          Configure validation rules for extracted fields
        </p>
      </div>

      {/* Fields with rules */}
      {fieldsWithRules.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">Configured Rules</h4>
          {fieldsWithRules.map((field) => {
            const fieldIndex = fields.findIndex((f) => f.id === field.id);
            return (
              <div
                key={field.id}
                className="border border-gray-200 rounded-lg bg-white p-4"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="font-medium text-gray-900">{field.name}</span>
                    <span className="ml-2 text-sm text-gray-500">({field.type})</span>
                  </div>
                  <button
                    onClick={() => handleRemoveValidation(fieldIndex)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove rule"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <Select
                    label="Rule Type"
                    value={field.validation?.type || ''}
                    onChange={(e) => {
                      const type = e.target.value as ValidationRule['type'];
                      handleUpdateValidation(fieldIndex, {
                        type,
                        value: type === 'enum' ? [] : '',
                      });
                    }}
                    options={[
                      { value: '', label: 'Select rule type...' },
                      ...RULE_TYPES.filter((r) =>
                        getApplicableRules(field.type).includes(r.value)
                      ).map((r) => ({
                        value: r.value,
                        label: r.label,
                      })),
                    ]}
                  />

                  {field.validation?.type === 'pattern' && (
                    <Input
                      label="Pattern"
                      placeholder="e.g., ^INV-[0-9]+$"
                      value={field.validation.value as string}
                      onChange={(e) =>
                        handleUpdateValidation(fieldIndex, {
                          ...field.validation!,
                          value: e.target.value,
                        })
                      }
                    />
                  )}

                  {(field.validation?.type === 'min' ||
                    field.validation?.type === 'max') && (
                    <Input
                      label={field.validation.type === 'min' ? 'Minimum' : 'Maximum'}
                      type="number"
                      value={field.validation.value as string}
                      onChange={(e) =>
                        handleUpdateValidation(fieldIndex, {
                          ...field.validation!,
                          value: parseFloat(e.target.value),
                        })
                      }
                    />
                  )}

                  {(field.validation?.type === 'minLength' ||
                    field.validation?.type === 'maxLength') && (
                    <Input
                      label={
                        field.validation.type === 'minLength'
                          ? 'Min Length'
                          : 'Max Length'
                      }
                      type="number"
                      value={field.validation.value as string}
                      onChange={(e) =>
                        handleUpdateValidation(fieldIndex, {
                          ...field.validation!,
                          value: parseInt(e.target.value, 10),
                        })
                      }
                    />
                  )}

                  {field.validation?.type === 'enum' && (
                    <Input
                      label="Allowed Values"
                      placeholder="value1, value2, value3"
                      value={(field.validation.value as string[]).join(', ')}
                      onChange={(e) =>
                        handleUpdateValidation(fieldIndex, {
                          ...field.validation!,
                          value: e.target.value.split(',').map((v) => v.trim()),
                        })
                      }
                      hint="Comma-separated list"
                    />
                  )}

                  <Input
                    label="Error Message"
                    placeholder="Optional custom error message"
                    value={field.validation?.message || ''}
                    onChange={(e) =>
                      handleUpdateValidation(fieldIndex, {
                        ...field.validation!,
                        message: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Fields without rules */}
      {fieldsWithoutRules.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">Add Rules to Fields</h4>
          <div className="grid grid-cols-2 gap-3">
            {fieldsWithoutRules.map((field) => {
              const fieldIndex = fields.findIndex((f) => f.id === field.id);
              const applicableRules = getApplicableRules(field.type);

              return (
                <button
                  key={field.id}
                  onClick={() =>
                    handleUpdateValidation(fieldIndex, {
                      type: applicableRules[0],
                      value: '',
                    })
                  }
                  className="flex items-center justify-between p-3 border border-dashed border-gray-300 rounded-lg hover:border-apex-500 hover:bg-apex-50 transition-colors text-left"
                >
                  <div>
                    <span className="font-medium text-gray-900">{field.name}</span>
                    <span className="ml-2 text-sm text-gray-500">({field.type})</span>
                  </div>
                  <PlusIcon className="w-5 h-5 text-gray-400" />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {fields.length === 0 && (
        <div className="text-center py-12 border-2 border-dashed border-gray-200 rounded-lg">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No fields to validate</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add fields in the Fields tab first, then configure validation rules here.
          </p>
        </div>
      )}
    </div>
  );
};

export default RuleBuilder;
