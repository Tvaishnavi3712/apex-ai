/**
 * BlueprintPreview Component - JSON schema preview for BDA blueprints
 */
import React, { useMemo } from 'react';
import { Blueprint, BlueprintField, BlueprintSchema } from './types';

interface BlueprintPreviewProps {
  blueprint: Partial<Blueprint>;
}

const mapFieldType = (type: string): string => {
  const typeMap: Record<string, string> = {
    string: 'string',
    number: 'number',
    boolean: 'boolean',
    date: 'string',
    array: 'array',
    object: 'object',
  };
  return typeMap[type] || 'string';
};

export const BlueprintPreview: React.FC<BlueprintPreviewProps> = ({ blueprint }) => {
  const schema = useMemo<BlueprintSchema>(() => {
    const properties: BlueprintSchema['properties'] = {};
    const definitions: BlueprintSchema['definitions'] = {};

    // Build definitions from array fields
    blueprint.definitions?.forEach((def) => {
      const defProperties: Record<string, { type: string; instruction?: string }> = {};
      def.properties.forEach((prop) => {
        defProperties[prop.name] = {
          type: mapFieldType(prop.type),
          ...(prop.instruction && { instruction: prop.instruction }),
        };
      });
      definitions[def.name] = { properties: defProperties };
    });

    // Build properties from fields
    blueprint.fields?.forEach((field: BlueprintField) => {
      const prop: BlueprintSchema['properties'][string] = {
        type: mapFieldType(field.type),
        inferenceType: field.inferenceType,
        instruction: field.instruction || undefined,
      };

      // Handle array types with references
      if (field.type === 'array') {
        const matchingDef = blueprint.definitions?.find(
          (d) => d.name.toLowerCase() === field.name.toLowerCase() ||
                 d.name.toLowerCase() === `${field.name.toLowerCase()}_item`
        );
        if (matchingDef) {
          prop.items = { '$ref': `#/definitions/${matchingDef.name}` };
        } else {
          prop.items = { type: 'string' };
        }
      }

      properties[field.name] = prop;
    });

    return {
      class: blueprint.name || 'UntitledBlueprint',
      description: blueprint.description || '',
      definitions,
      properties,
    };
  }, [blueprint]);

  const jsonString = JSON.stringify(schema, null, 2);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(jsonString);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">BDA Schema Preview</h3>
          <p className="text-sm text-gray-500">
            This JSON schema will be used for AWS Bedrock Data Automation
          </p>
        </div>
        <button
          onClick={copyToClipboard}
          className="px-4 py-2 text-sm font-medium text-apex-600 hover:text-apex-700 border border-apex-300 rounded-lg hover:bg-apex-50 transition-colors"
        >
          Copy to Clipboard
        </button>
      </div>

      <div className="relative">
        <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-auto max-h-[500px] text-sm font-mono">
          <code>{jsonString}</code>
        </pre>
      </div>

      {/* Schema Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {blueprint.fields?.length || 0}
          </div>
          <div className="text-sm text-gray-500">Fields</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {blueprint.definitions?.length || 0}
          </div>
          <div className="text-sm text-gray-500">Definitions</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-2xl font-semibold text-gray-900">
            {blueprint.fields?.filter((f) => f.required).length || 0}
          </div>
          <div className="text-sm text-gray-500">Required</div>
        </div>
      </div>
    </div>
  );
};

export default BlueprintPreview;
