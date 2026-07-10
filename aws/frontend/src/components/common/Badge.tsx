/**
 * Badge Component
 */

import React from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | 'outline' | 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  className?: string;
}

const variants = {
  default: 'bg-gray-100 text-gray-700',
  success: 'bg-success-50 text-success-700',
  warning: 'bg-warning-50 text-warning-700',
  danger: 'bg-danger-50 text-danger-700',
  info: 'bg-apex-50 text-apex-700',
  purple: 'bg-purple-50 text-purple-700',
  outline: 'bg-transparent border border-gray-300 text-gray-600',
  primary: 'bg-apex-100 text-apex-700',
  secondary: 'bg-purple-100 text-purple-700',
};

const dotColors = {
  default: 'bg-gray-400',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  danger: 'bg-danger-500',
  info: 'bg-apex-500',
  purple: 'bg-purple-500',
  outline: 'bg-gray-400',
  primary: 'bg-apex-500',
  secondary: 'bg-purple-500',
};

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className,
}) => {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full mr-1.5',
            dotColors[variant]
          )}
        />
      )}
      {children}
    </span>
  );
};

// Status Badge with predefined statuses
interface StatusBadgeProps {
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'review' | 'draft' | 'deployed' | 'idle' | 'running' | 'error' | 'stopped';
  className?: string;
}

const statusConfig: Record<string, { variant: BadgeProps['variant']; label: string }> = {
  pending: { variant: 'default', label: 'Pending' },
  in_progress: { variant: 'info', label: 'In Progress' },
  completed: { variant: 'success', label: 'Completed' },
  failed: { variant: 'danger', label: 'Failed' },
  review: { variant: 'warning', label: 'Review' },
  draft: { variant: 'default', label: 'Draft' },
  deployed: { variant: 'success', label: 'Deployed' },
  idle: { variant: 'default', label: 'Idle' },
  running: { variant: 'success', label: 'Running' },
  error: { variant: 'danger', label: 'Error' },
  stopped: { variant: 'warning', label: 'Stopped' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const config = statusConfig[status] || statusConfig.pending;
  return (
    <Badge variant={config.variant} dot className={className}>
      {config.label}
    </Badge>
  );
};

export default Badge;
