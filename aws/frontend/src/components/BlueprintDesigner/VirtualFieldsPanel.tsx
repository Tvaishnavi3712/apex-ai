/**
 * Virtual Fields Panel
 * Define computed columns and aggregated tables for post-extraction processing
 */

import React, { useState, useCallback } from 'react';
import {
  PlusIcon,
  TrashIcon,
  CalculatorIcon,
  TableCellsIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { VirtualColumn, VirtualTable, BlueprintField, ExpressionType, FieldType } from './types';

interface VirtualFieldsPanelProps {
  virtualColumns: VirtualColumn[];
  virtualTables: VirtualTable[];
  fields: BlueprintField[];
  onVirtualColumnsChange: (columns: VirtualColumn[]) => void;
  onVirtualTablesChange: (tables: VirtualTable[]) => void;
}

const EXPRESSION_TYPES: { value: ExpressionType; label: string; description: string; example: string }[] = [
  {
    value: 'formula',
    label: 'Formula',
    description: 'Mathematical calculation',
    example: 'subtotal + tax_amount'
  },
  {
    value: 'concatenate',
    label: 'Concatenate',
    description: 'Join text values',
    example: 'vendor_name + " - " + vendor_id'
  },
  {
    value: 'aggregate',
    label: 'Aggregate',
    description: 'Array aggregation (sum, count, avg)',
    example: 'sum(line_items.amount)'
  },
  {
    value: 'conditional',
    label: 'Conditional',
    description: 'If/else logic',
    example: 'if(amount > 1000, "HIGH", "LOW")'
  },
  {
    value: 'lookup',
    label: 'Lookup',
    description: 'Reference another field',
    example: 'vendor.payment_terms'
  }
];

const FIELD_TYPES: FieldType[] = ['string', 'number', 'boolean', 'date', 'array', 'object'];

export const VirtualFieldsPanel: React.FC<VirtualFieldsPanelProps> = ({
  virtualColumns,
  virtualTables,
  fields,
  onVirtualColumnsChange,
  onVirtualTablesChange
}) => {
  const [expandedColumn, setExpandedColumn] = useState<string | null>(null);
  const [expandedTable, setExpandedTable] = useState<string | null>(null);

  // Get array fields for virtual table sources
  const arrayFields = fields.filter(f => f.type === 'array');

  // Add new virtual column
  const addVirtualColumn = useCallback(() => {
    const newColumn: VirtualColumn = {
      id: `vc_${Date.now()}`,
      name: '',
      type: 'string',
      expressionType: 'formula',
      expression: '',
      sourceFields: []
    };
    onVirtualColumnsChange([...virtualColumns, newColumn]);
    setExpandedColumn(newColumn.id);
  }, [virtualColumns, onVirtualColumnsChange]);

  // Update virtual column
  const updateVirtualColumn = useCallback((id: string, updates: Partial<VirtualColumn>) => {
    onVirtualColumnsChange(
      virtualColumns.map(vc => vc.id === id ? { ...vc, ...updates } : vc)
    );
  }, [virtualColumns, onVirtualColumnsChange]);

  // Delete virtual column
  const deleteVirtualColumn = useCallback((id: string) => {
    onVirtualColumnsChange(virtualColumns.filter(vc => vc.id !== id));
    if (expandedColumn === id) {
      setExpandedColumn(null);
    }
  }, [virtualColumns, onVirtualColumnsChange, expandedColumn]);

  // Add new virtual table
  const addVirtualTable = useCallback(() => {
    const newTable: VirtualTable = {
      id: `vt_${Date.now()}`,
      name: '',
      sourceArray: arrayFields[0]?.name || '',
      aggregations: []
    };
    onVirtualTablesChange([...virtualTables, newTable]);
    setExpandedTable(newTable.id);
  }, [virtualTables, onVirtualTablesChange, arrayFields]);

  // Update virtual table
  const updateVirtualTable = useCallback((id: string, updates: Partial<VirtualTable>) => {
    onVirtualTablesChange(
      virtualTables.map(vt => vt.id === id ? { ...vt, ...updates } : vt)
    );
  }, [virtualTables, onVirtualTablesChange]);

  // Delete virtual table
  const deleteVirtualTable = useCallback((id: string) => {
    onVirtualTablesChange(virtualTables.filter(vt => vt.id !== id));
    if (expandedTable === id) {
      setExpandedTable(null);
    }
  }, [virtualTables, onVirtualTablesChange, expandedTable]);

  // Add aggregation to virtual table
  const addAggregation = useCallback((tableId: string) => {
    const table = virtualTables.find(t => t.id === tableId);
    if (!table) return;

    const newAgg: VirtualColumn = {
      id: `agg_${Date.now()}`,
      name: '',
      type: 'number',
      expressionType: 'aggregate',
      expression: '',
      sourceFields: []
    };

    updateVirtualTable(tableId, {
      aggregations: [...table.aggregations, newAgg]
    });
  }, [virtualTables, updateVirtualTable]);

  return (
    <div className="space-y-6">
      {/* Virtual Columns Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <CalculatorIcon className="w-5 h-5 text-gray-500" />
            <h3 className="font-medium text-gray-900">Virtual Columns</h3>
            <span className="text-sm text-gray-500">({virtualColumns.length})</span>
          </div>
          <button
            onClick={addVirtualColumn}
            className="flex items-center text-sm text-blue-600 hover:text-blue-700"
          >
            <PlusIcon className="w-4 h-4 mr-1" />
            Add Column
          </button>
        </div>

        {virtualColumns.length === 0 ? (
          <div className="text-center py-6 bg-gray-50 rounded-lg border border-dashed">
            <CalculatorIcon className="w-8 h-8 mx-auto text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">No virtual columns defined</p>
            <p className="text-xs text-gray-400 mt-1">
              Create computed fields like totals, concatenations, or conditionals
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {virtualColumns.map((column) => (
              <div key={column.id} className="border rounded-lg">
                {/* Header */}
                <div
                  className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpandedColumn(expandedColumn === column.id ? null : column.id)}
                >
                  <div className="flex items-center space-x-3">
                    {expandedColumn === column.id ? (
                      <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRightIcon className="w-4 h-4 text-gray-400" />
                    )}
                    <span className="font-medium text-gray-900">
                      {column.name || 'Untitled'}
                    </span>
                    <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                      {column.expressionType}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteVirtualColumn(column.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-500"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>

                {/* Expanded editor */}
                {expandedColumn === column.id && (
                  <div className="px-4 pb-4 space-y-3 border-t bg-gray-50">
                    {/* Name and Type */}
                    <div className="grid grid-cols-2 gap-3 pt-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">
                          Column Name
                        </label>
                        <input
                          type="text"
                          value={column.name}
                          onChange={(e) => updateVirtualColumn(column.id, { name: e.target.value })}
                          placeholder="e.g., total_with_tax"
                          className="w-full px-3 py-2 text-sm border rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">
                          Output Type
                        </label>
                        <select
                          value={column.type}
                          onChange={(e) => updateVirtualColumn(column.id, { type: e.target.value as FieldType })}
                          className="w-full px-3 py-2 text-sm border rounded-lg"
                        >
                          {FIELD_TYPES.map(type => (
                            <option key={type} value={type}>{type}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Expression Type */}
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">
                        Expression Type
                      </label>
                      <div className="grid grid-cols-5 gap-1">
                        {EXPRESSION_TYPES.map(({ value, label }) => (
                          <button
                            key={value}
                            onClick={() => updateVirtualColumn(column.id, { expressionType: value })}
                            className={`
                              px-2 py-1 text-xs rounded border
                              ${column.expressionType === value
                                ? 'bg-blue-50 border-blue-300 text-blue-700'
                                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                              }
                            `}
                          >
                            {label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Expression */}
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">
                        Expression
                      </label>
                      <input
                        type="text"
                        value={column.expression}
                        onChange={(e) => updateVirtualColumn(column.id, { expression: e.target.value })}
                        placeholder={EXPRESSION_TYPES.find(t => t.value === column.expressionType)?.example}
                        className="w-full px-3 py-2 text-sm border rounded-lg font-mono"
                      />
                      <p className="text-xs text-gray-400 mt-1">
                        {EXPRESSION_TYPES.find(t => t.value === column.expressionType)?.description}
                      </p>
                    </div>

                    {/* Description */}
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">
                        Description (optional)
                      </label>
                      <input
                        type="text"
                        value={column.description || ''}
                        onChange={(e) => updateVirtualColumn(column.id, { description: e.target.value })}
                        placeholder="What this column represents"
                        className="w-full px-3 py-2 text-sm border rounded-lg"
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Virtual Tables Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <TableCellsIcon className="w-5 h-5 text-gray-500" />
            <h3 className="font-medium text-gray-900">Virtual Tables</h3>
            <span className="text-sm text-gray-500">({virtualTables.length})</span>
          </div>
          <button
            onClick={addVirtualTable}
            disabled={arrayFields.length === 0}
            className="flex items-center text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title={arrayFields.length === 0 ? 'Add array fields first' : undefined}
          >
            <PlusIcon className="w-4 h-4 mr-1" />
            Add Table
          </button>
        </div>

        {arrayFields.length === 0 ? (
          <div className="text-center py-6 bg-gray-50 rounded-lg border border-dashed">
            <TableCellsIcon className="w-8 h-8 mx-auto text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">No array fields available</p>
            <p className="text-xs text-gray-400 mt-1">
              Add array fields (like line_items) to create virtual tables
            </p>
          </div>
        ) : virtualTables.length === 0 ? (
          <div className="text-center py-6 bg-gray-50 rounded-lg border border-dashed">
            <TableCellsIcon className="w-8 h-8 mx-auto text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">No virtual tables defined</p>
            <p className="text-xs text-gray-400 mt-1">
              Create aggregated summaries from array fields
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {virtualTables.map((table) => (
              <div key={table.id} className="border rounded-lg">
                {/* Header */}
                <div
                  className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpandedTable(expandedTable === table.id ? null : table.id)}
                >
                  <div className="flex items-center space-x-3">
                    {expandedTable === table.id ? (
                      <ChevronDownIcon className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRightIcon className="w-4 h-4 text-gray-400" />
                    )}
                    <span className="font-medium text-gray-900">
                      {table.name || 'Untitled'}
                    </span>
                    <span className="text-xs text-gray-500">
                      from {table.sourceArray || '...'}
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteVirtualTable(table.id);
                    }}
                    className="p-1 text-gray-400 hover:text-red-500"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>

                {/* Expanded editor */}
                {expandedTable === table.id && (
                  <div className="px-4 pb-4 space-y-3 border-t bg-gray-50">
                    {/* Name and Source */}
                    <div className="grid grid-cols-2 gap-3 pt-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">
                          Table Name
                        </label>
                        <input
                          type="text"
                          value={table.name}
                          onChange={(e) => updateVirtualTable(table.id, { name: e.target.value })}
                          placeholder="e.g., category_totals"
                          className="w-full px-3 py-2 text-sm border rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">
                          Source Array
                        </label>
                        <select
                          value={table.sourceArray}
                          onChange={(e) => updateVirtualTable(table.id, { sourceArray: e.target.value })}
                          className="w-full px-3 py-2 text-sm border rounded-lg"
                        >
                          {arrayFields.map(f => (
                            <option key={f.id} value={f.name}>{f.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Aggregations */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-xs font-medium text-gray-500">
                          Aggregations
                        </label>
                        <button
                          onClick={() => addAggregation(table.id)}
                          className="text-xs text-blue-600 hover:text-blue-700"
                        >
                          + Add
                        </button>
                      </div>
                      {table.aggregations.length === 0 ? (
                        <p className="text-xs text-gray-400 italic">
                          No aggregations defined
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {table.aggregations.map((agg, idx) => (
                            <div key={agg.id} className="flex items-center space-x-2">
                              <input
                                type="text"
                                value={agg.name}
                                onChange={(e) => {
                                  const newAggs = [...table.aggregations];
                                  newAggs[idx] = { ...agg, name: e.target.value };
                                  updateVirtualTable(table.id, { aggregations: newAggs });
                                }}
                                placeholder="column_name"
                                className="flex-1 px-2 py-1 text-sm border rounded"
                              />
                              <input
                                type="text"
                                value={agg.expression}
                                onChange={(e) => {
                                  const newAggs = [...table.aggregations];
                                  newAggs[idx] = { ...agg, expression: e.target.value };
                                  updateVirtualTable(table.id, { aggregations: newAggs });
                                }}
                                placeholder="sum(amount)"
                                className="flex-1 px-2 py-1 text-sm border rounded font-mono"
                              />
                              <button
                                onClick={() => {
                                  const newAggs = table.aggregations.filter((_, i) => i !== idx);
                                  updateVirtualTable(table.id, { aggregations: newAggs });
                                }}
                                className="p-1 text-gray-400 hover:text-red-500"
                              >
                                <TrashIcon className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VirtualFieldsPanel;
