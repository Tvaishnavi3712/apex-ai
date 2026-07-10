/**
 * FieldList Component - Manage list of blueprint fields
 */
import React, { useState } from 'react';
import { BlueprintField } from './types';
import { FieldEditor } from './FieldEditor';
import { Button } from '../common';
import { PlusIcon } from '@heroicons/react/24/outline';
import { v4 as uuidv4 } from 'uuid';

interface FieldListProps {
  fields: BlueprintField[];
  onChange: (fields: BlueprintField[]) => void;
}

const createDefaultField = (): BlueprintField => ({
  id: uuidv4(),
  name: '',
  type: 'string',
  inferenceType: 'explicit',
  instruction: '',
  required: false,
});

export const FieldList: React.FC<FieldListProps> = ({ fields, onChange }) => {
  const [expandedFieldId, setExpandedFieldId] = useState<string | null>(null);

  const handleAddField = () => {
    const newField = createDefaultField();
    onChange([...fields, newField]);
    setExpandedFieldId(newField.id);
  };

  const handleUpdateField = (index: number, updatedField: BlueprintField) => {
    const newFields = [...fields];
    newFields[index] = updatedField;
    onChange(newFields);
  };

  const handleDeleteField = (index: number) => {
    const newFields = fields.filter((_, i) => i !== index);
    onChange(newFields);
  };

  const handleMoveField = (index: number, direction: 'up' | 'down') => {
    const newFields = [...fields];
    const newIndex = direction === 'up' ? index - 1 : index + 1;

    if (newIndex < 0 || newIndex >= fields.length) return;

    [newFields[index], newFields[newIndex]] = [newFields[newIndex], newFields[index]];
    onChange(newFields);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Extraction Fields</h3>
          <p className="text-sm text-gray-500">
            Define the fields to extract from documents
          </p>
        </div>
        <Button
          onClick={handleAddField}
          icon={<PlusIcon className="w-4 h-4" />}
          size="sm"
        >
          Add Field
        </Button>
      </div>

      {fields.length === 0 ? (
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No fields defined</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add fields to specify what data to extract from documents.
          </p>
          <div className="mt-4">
            <Button onClick={handleAddField} size="sm">
              <PlusIcon className="w-4 h-4 mr-1" />
              Add First Field
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {fields.map((field, index) => (
            <div key={field.id} className="group relative">
              {/* Reorder buttons */}
              <div className="absolute -left-8 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col gap-1">
                <button
                  onClick={() => handleMoveField(index, 'up')}
                  disabled={index === 0}
                  className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                  title="Move up"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </button>
                <button
                  onClick={() => handleMoveField(index, 'down')}
                  disabled={index === fields.length - 1}
                  className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                  title="Move down"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              <FieldEditor
                field={field}
                onChange={(updatedField) => handleUpdateField(index, updatedField)}
                onDelete={() => handleDeleteField(index)}
                isExpanded={expandedFieldId === field.id}
                onToggleExpand={() =>
                  setExpandedFieldId(expandedFieldId === field.id ? null : field.id)
                }
              />
            </div>
          ))}
        </div>
      )}

      {/* Quick Add Templates */}
      {fields.length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-2">Quick Add Common Fields:</p>
          <div className="flex flex-wrap gap-2">
            {[
              { name: 'invoice_number', type: 'string', instruction: 'Unique invoice identifier' },
              { name: 'date', type: 'string', instruction: 'Document date' },
              { name: 'total_amount', type: 'number', instruction: 'Total amount including tax' },
              { name: 'vendor_name', type: 'string', instruction: 'Name of vendor/supplier' },
            ].map((template) => (
              <button
                key={template.name}
                onClick={() => {
                  const newField: BlueprintField = {
                    id: uuidv4(),
                    name: template.name,
                    type: template.type as any,
                    inferenceType: 'explicit',
                    instruction: template.instruction,
                    required: false,
                  };
                  onChange([...fields, newField]);
                }}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
              >
                + {template.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FieldList;
