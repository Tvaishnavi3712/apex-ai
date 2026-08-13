/**
 * Apex Sidebar — dark, fixed, collapsible, group-aware color coding.
 * Ported from apex-prototype 2/*.html (renderSidebar + toggleSidebar).
 */

import React, { useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useApexStore } from '@/lib/store';
import { useDemoMode } from '@/lib/demoMode';
import { useProductBrand, brandWordmark, brandSubtitle, brandLabel } from '@/lib/productBrand';
import { Icon } from './icons';
import {
  NAV,
  GROUP_ACTIVE_CLASS,
  GROUP_BAR_COLOR,
  GROUP_LABEL_COLOR,
  type NavGroup,
} from './navConfig';

function isActive(pathname: string, href: string): boolean {
  if (href === '/') return pathname === '/';
  return pathname === href || pathname.startsWith(href + '/');
}

export function AppSidebar() {
  const router = useRouter();
  const sidebarOpen = useApexStore((s) => s.sidebarOpen);
  const toggleSidebar = useApexStore((s) => s.toggleSidebar);
  const [demoMode] = useDemoMode();
  const collapsed = !sidebarOpen;

  // In Verizon Far Edge demo mode, surface a MentorAgent link in OPERATE
  // so engineers can jump straight to the KB chat. Hidden in every other
  // mode since the page itself gates render on demo mode.
  const nav: NavGroup[] = useMemo(() => {
    if (demoMode !== 'verizon_far_edge') return NAV;
    return NAV.map((g) => {
      if (g.group !== 'OPERATE') return g;
      // Only inject if not already present.
      if (g.items.some((it) => it.href === '/mentor-agent')) return g;
      return {
        ...g,
        items: [
          ...g.items,
          { name: 'MentorAgent', href: '/mentor-agent', icon: 'tray' as const },
        ],
      };
    });
  }, [demoMode]);
  // Product brand toggle (Settings page). When user picks "Regulus Lens",
  // wordmark/subtitle + 3 nav labels (ApexSignal → Regulus Signal,
  // Agent Hub → Regulus Hub, ApexLens → Regulus Doc) flip system-wide.
  const [brand] = useProductBrand();
  const wordmark = brandWordmark(brand);
  const subtitle = brandSubtitle(brand);

  return (
    <aside
      className={`sidebar ${collapsed ? 'collapsed' : ''}`}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        height: '100%',
        zIndex: 40,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Logo row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 70,
          padding: '0 18px',
          borderBottom: '1px solid rgba(255,255,255,.06)',
          flexShrink: 0,
        }}
      >
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 14, overflow: 'hidden', minWidth: 0, textDecoration: 'none' }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 14,
              background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              boxShadow: '0 4px 14px rgba(59,130,246,.35)',
            }}
          >
            <svg style={{ width: 22, height: 22, color: '#fff' }} fill="currentColor" viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z" /></svg>
          </div>
          <div className="logo-text" style={{ overflow: 'hidden' }}>
            <div style={{ fontWeight: 800, fontSize: 17, color: '#f9fafb', letterSpacing: '-.01em', lineHeight: 1 }}>{wordmark}</div>
            <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '.18em', color: '#6b7280', marginTop: 3 }}>{subtitle}</div>
          </div>
        </Link>
        <button
          onClick={toggleSidebar}
          style={{
            padding: 7,
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#6b7280',
            borderRadius: 9,
            flexShrink: 0,
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,.07)')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'none')}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <Icon name={collapsed ? 'chevron_right' : 'chevron_left'} className="" style={{ width: 18, height: 18 }} />
        </button>
      </div>

      {/* Demo Mode badge — surfaces the active customer demo right below
       *  the logo. Shows nothing when 'all' is selected. Matches the badge
       *  treatment in the demo-7-boler / cwfcu mockups. */}
      {demoMode !== 'all' && !collapsed && (
        <div style={{
          margin: '10px 14px 0',
          background: 'rgba(108,71,255,.15)',
          border: '1px solid rgba(108,71,255,.30)',
          borderRadius: 6,
          padding: '7px 11px',
        }}>
          <div style={{
            fontSize: 9, fontWeight: 700, letterSpacing: '.14em',
            textTransform: 'uppercase', color: 'rgba(255,255,255,.38)',
          }}>
            Demo Mode
          </div>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#a78bfa', marginTop: 2 }}>
            {(demoMode === 'boler' || demoMode === 'manufacturing_multi_division') ? 'Manufacturing · Multi-Division'
            : (demoMode === 'cwfcu' || demoMode === 'credit_union') ? 'CommunityWide FCU'
            : (demoMode === 'eprod' || demoMode === 'oil_gas_midstream') ? 'EPROD · Midstream'
            : (demoMode === 'verizon_far_edge') ? 'Verizon Far Edge'
            : (demoMode === 'nuclear_operations' || demoMode === 'stp') ? 'STP Nuclear'
            : (demoMode === 'supply_manufacturing') ? 'CBB · Cornerstone Building Brands'
            : demoMode.replace(/_/g, ' ')}
          </div>
        </div>
      )}

      {/* Nav groups */}
      <nav
        className="dark-scroll"
        style={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          padding: '20px 14px',
          display: 'flex',
          flexDirection: 'column',
          gap: 24,
        }}
      >
        {nav.map((g) => (
          <div key={g.group} style={{ marginBottom: 4 }}>
            <div
              className="group-label"
              style={{
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '.12em',
                textTransform: 'uppercase',
                color: GROUP_LABEL_COLOR[g.group],
                padding: '0 6px 8px 6px',
              }}
            >
              {g.group}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {g.items.map((item) => {
                const active = isActive(router.pathname, item.href);
                const ac = active ? GROUP_ACTIVE_CLASS[g.group] : '';
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`nav-item ${ac}`}
                    style={{ position: 'relative' }}
                  >
                    {active && (
                      <span
                        style={{
                          position: 'absolute',
                          left: 0,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          width: 3,
                          height: 22,
                          borderRadius: '0 3px 3px 0',
                          background: GROUP_BAR_COLOR[g.group],
                        }}
                      />
                    )}
                    <Icon name={item.icon} className="" style={{ width: 22, height: 22, flexShrink: 0 }} />
                    <span className="nav-label">{brandLabel(item.name, brand)}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

    </aside>
  );
}
