/**
 * DataSourceBanner — a slim bar that tells the user whether the current
 * page is rendering real, partial, or sample data.
 *
 * Used by every list page. Hidden when source === 'api' (live).
 */

import React from 'react';

export type DataSource = 'api' | 'registry' | 'mock' | 'loading';

interface Props {
  source: DataSource;
  /** Optional entity label (e.g. "actions", "playbooks") used in the mock copy. */
  entity?: string;
  /** Optional CTA — e.g. a seed command the user can copy/paste. */
  hint?: string;
}

export function DataSourceBanner({ source, entity = 'records', hint }: Props) {
  if (source === 'api' || source === 'loading') return null;

  const isRegistry = source === 'registry';
  const bg        = isRegistry ? '#eff6ff' : '#fffbeb';
  const border    = isRegistry ? '#bfdbfe' : '#fde68a';
  const color     = isRegistry ? '#1d4ed8' : '#b45309';
  const iconColor = isRegistry ? '#3b82f6' : '#f59e0b';
  const dotColor  = isRegistry ? '#3b82f6' : '#f59e0b';

  const title = isRegistry
    ? `Showing ${entity} from the in-memory registry`
    : `Offline: showing sample ${entity}`;

  const body = isRegistry
    ? 'Backend is up but Cosmos DB has no records yet — results come from the handler code on disk. Sync them to Cosmos DB to see invocation counts and edits.'
    : 'The backend is unreachable or returned nothing. Start the backend and seed data to see live records.';

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 12,
        padding: '10px 14px',
        marginBottom: 20,
        background: bg,
        border: `1px solid ${border}`,
        borderRadius: 12,
        color,
        fontSize: 13,
        lineHeight: 1.5,
      }}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, flexShrink: 0, marginTop: 3 }}>
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: dotColor,
            animation: 'apex-pulse 2s infinite',
            display: 'inline-block',
          }}
        />
        <svg
          style={{ width: 16, height: 16, color: iconColor }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700 }}>{title}</div>
        <div style={{ color: isRegistry ? '#1e40af' : '#92400e', marginTop: 2 }}>{body}</div>
        {hint && (
          <code
            className="mono"
            style={{
              display: 'inline-block',
              marginTop: 8,
              padding: '4px 8px',
              background: 'rgba(255,255,255,.6)',
              border: `1px solid ${border}`,
              borderRadius: 6,
              fontSize: 11,
              color: '#0f172a',
            }}
          >
            {hint}
          </code>
        )}
      </div>
    </div>
  );
}
