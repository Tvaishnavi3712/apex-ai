/**
 * Apex Topbar — sticky white bar with page title, group badge,
 * system status, search, notifications, avatar.
 */

import React from 'react';
import { useRouter } from 'next/router';
import { Icon } from './icons';
import { groupForPath, titleForPath, GROUP_BADGE_CLASS } from './navConfig';
import { useProductBrand, brandLabel } from '@/lib/productBrand';

export function AppTopbar() {
  const router = useRouter();
  const [brand] = useProductBrand();
  // Page title respects the active product brand (ApexSignal → Regulus Signal etc.).
  const title = brandLabel(titleForPath(router.pathname), brand);
  const group = groupForPath(router.pathname);
  const badgeCls = GROUP_BADGE_CLASS[group];

  return (
    <header
      style={{
        height: 64,
        background: '#fff',
        borderBottom: '1px solid #f1f5f9',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 30,
        flexShrink: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h1 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>{title}</h1>
        <span className={`badge ${badgeCls}`}>{group}</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* Search (hidden on small screens) */}
        <div style={{ position: 'relative' }} className="hidden md:block">
          <Icon
            name="search"
            className=""
            style={{
              position: 'absolute',
              left: 10,
              top: '50%',
              transform: 'translateY(-50%)',
              width: 16,
              height: 16,
              color: '#9ca3af',
            }}
          />
          <input
            type="text"
            placeholder="Search..."
            style={{
              padding: '8px 14px 8px 34px',
              fontSize: 13,
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: 10,
              outline: 'none',
              width: 220,
              fontFamily: 'inherit',
            }}
          />
        </div>

        {/* System health */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12,
            color: '#16a34a',
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            padding: '6px 12px',
            borderRadius: 8,
            fontWeight: 500,
          }}
        >
          <span className="dot-green animate-pulse" /> All Systems Operational
        </div>

        {/* Bell */}
        <button
          type="button"
          style={{
            padding: 8,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#6b7280',
            borderRadius: 10,
            position: 'relative',
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'none')}
          aria-label="Notifications"
        >
          <Icon name="bell" className="" style={{ width: 20, height: 20 }} />
          <span
            style={{
              position: 'absolute',
              top: 6,
              right: 6,
              width: 8,
              height: 8,
              background: '#ef4444',
              borderRadius: '50%',
              border: '2px solid #fff',
            }}
          />
        </button>

        {/* Avatar */}
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
          }}
        >
          <span style={{ fontSize: 11, fontWeight: 700, color: '#fff' }}>CB</span>
        </div>
      </div>
    </header>
  );
}
