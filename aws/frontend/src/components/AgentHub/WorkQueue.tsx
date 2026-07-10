/**
 * Work Queue - Display and manage work items
 */

import React, { useState } from 'react';
import { Card, CardHeader, Badge, StatusBadge, Button, Select } from '../common';
import { EyeIcon, PlayIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface WorkItem {
  id: string;
  type: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'review';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  assignedAgent?: string;
  data: any;
  createdAt: string;
  updatedAt: string;
}

interface WorkQueueProps {
  items: WorkItem[];
  onViewItem: (item: WorkItem) => void;
  onProcessItem: (item: WorkItem) => void;
  onCompleteItem: (item: WorkItem) => void;
  onRejectItem: (item: WorkItem) => void;
}

const priorityConfig = {
  low: { color: 'default', label: 'Low' },
  normal: { color: 'info', label: 'Normal' },
  high: { color: 'warning', label: 'High' },
  urgent: { color: 'danger', label: 'Urgent' },
};

export const WorkQueue: React.FC<WorkQueueProps> = ({
  items,
  onViewItem,
  onProcessItem,
  onCompleteItem,
  onRejectItem,
}) => {
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');

  const filteredItems = items.filter((item) => {
    if (statusFilter !== 'all' && item.status !== statusFilter) return false;
    if (priorityFilter !== 'all' && item.priority !== priorityFilter) return false;
    return true;
  });

  const groupedItems = filteredItems.reduce((acc, item) => {
    const key = item.status;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {} as Record<string, WorkItem[]>);

  const statusOrder = ['review', 'in_progress', 'pending', 'completed', 'failed'];

  return (
    <div className="h-full flex flex-col">
      {/* Filters */}
      <div className="flex items-center gap-4 p-4 bg-white border-b border-gray-200">
        <div className="flex-1">
          <h2 className="text-lg font-semibold">Work Queue</h2>
          <p className="text-sm text-gray-500">{filteredItems.length} items</p>
        </div>

        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { value: 'all', label: 'All Statuses' },
            { value: 'pending', label: 'Pending' },
            { value: 'in_progress', label: 'In Progress' },
            { value: 'review', label: 'Needs Review' },
            { value: 'completed', label: 'Completed' },
            { value: 'failed', label: 'Failed' },
          ]}
          className="w-40"
        />

        <Select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          options={[
            { value: 'all', label: 'All Priorities' },
            { value: 'urgent', label: 'Urgent' },
            { value: 'high', label: 'High' },
            { value: 'normal', label: 'Normal' },
            { value: 'low', label: 'Low' },
          ]}
          className="w-40"
        />
      </div>

      {/* Queue List */}
      <div className="flex-1 overflow-auto p-4 space-y-6">
        {statusOrder.map((status) => {
          const statusItems = groupedItems[status];
          if (!statusItems || statusItems.length === 0) return null;

          return (
            <div key={status}>
              <div className="flex items-center gap-2 mb-3">
                <StatusBadge status={status as any} />
                <span className="text-sm text-gray-500">
                  {statusItems.length} item{statusItems.length > 1 ? 's' : ''}
                </span>
              </div>

              <div className="space-y-2">
                {statusItems.map((item) => (
                  <Card
                    key={item.id}
                    padding="sm"
                    hover
                    className="flex items-center gap-4"
                  >
                    {/* Priority Indicator */}
                    <div className={clsx(
                      'w-1 h-12 rounded-full',
                      item.priority === 'urgent' && 'bg-danger-500',
                      item.priority === 'high' && 'bg-warning-500',
                      item.priority === 'normal' && 'bg-apex-500',
                      item.priority === 'low' && 'bg-gray-300'
                    )} />

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 truncate">
                          {item.title}
                        </span>
                        <Badge variant={priorityConfig[item.priority].color as any} size="sm">
                          {priorityConfig[item.priority].label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                        <span>{item.type}</span>
                        <span>•</span>
                        <span>ID: {item.id.slice(0, 8)}</span>
                        {item.assignedAgent && (
                          <>
                            <span>•</span>
                            <span>Agent: {item.assignedAgent}</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Timestamp */}
                    <div className="text-sm text-gray-400 text-right">
                      <div>{new Date(item.createdAt).toLocaleDateString()}</div>
                      <div>{new Date(item.createdAt).toLocaleTimeString()}</div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={<EyeIcon className="h-4 w-4" />}
                        onClick={() => onViewItem(item)}
                      />

                      {item.status === 'pending' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={<PlayIcon className="h-4 w-4" />}
                          onClick={() => onProcessItem(item)}
                        />
                      )}

                      {item.status === 'review' && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-success-500 hover:bg-success-50"
                            icon={<CheckIcon className="h-4 w-4" />}
                            onClick={() => onCompleteItem(item)}
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-danger-500 hover:bg-danger-50"
                            icon={<XMarkIcon className="h-4 w-4" />}
                            onClick={() => onRejectItem(item)}
                          />
                        </>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}

        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No work items match your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkQueue;
