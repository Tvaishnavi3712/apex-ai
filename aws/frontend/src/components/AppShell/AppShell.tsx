/**
 * Apex App Shell — composes sidebar + topbar + main content.
 * Replaces the old Layout/ on every page.
 *
 * STP demo mode (Settings → Demo Mode = "STP Demo") layers a subtle
 * slate-blue branding overlay on every page:
 *   • thin top accent bar (3px) above the topbar
 *   • soft gradient background tinted toward STP slate-blue
 *   • compact "STP Demo" pill in the corner of the main content area
 *
 * The overlay is intentionally subtle — accents-only, not a full reskin.
 * Reads as "configured for STP" without making the platform look fragile.
 */

import React from 'react';
import { useApexStore } from '@/lib/store';
import { useDemoMode } from '@/lib/demoMode';
import { AppSidebar } from './AppSidebar';
import { AppTopbar } from './AppTopbar';

export function AppShell({ children }: { children: React.ReactNode }) {
  const sidebarOpen = useApexStore((s) => s.sidebarOpen);
  const [demoMode] = useDemoMode();
  const marginLeft = sidebarOpen ? 280 : 76;

  // Demo overlay activates for any specific-industry demo mode (not 'all').
  // STP nuclear gets slate-blue; CBB supply chain gets green; others fall
  // back to neutral slate.
  const isDemoActive = demoMode !== 'all';
  const isSTP =
    demoMode === 'nuclear_operations' || demoMode === 'stp';
  const isCBB =
    demoMode === 'supply_manufacturing' || demoMode === 'manufacturing' || demoMode === 'supply_chain';
  const isEprod =
    demoMode === 'eprod' || demoMode === 'oil_gas_midstream';
  const isCwfcu =
    demoMode === 'cwfcu' || demoMode === 'credit_union';
  const isBoler =
    demoMode === 'boler' || demoMode === 'manufacturing_multi_division';
  // CWFCU + Boler both use purple (#6c47ff — matches both sets of HTML mockups).
  // EPROD keeps slate; CBB green; STP nuclear navy.
  const accent = isSTP ? '#1e3a8a'
               : isCBB ? '#16a34a'
               : isEprod ? '#475569'
               : isCwfcu ? '#6c47ff'
               : isBoler ? '#6c47ff'
               : '#475569';
  const accentLabel = isSTP ? 'STP DEMO MODE'
                    : isCBB ? 'CBB DEMO MODE'
                    : isCwfcu ? 'CREDIT UNION VIEW · CW FCU'
                    : isBoler ? 'MANUFACTURING · MULTI-DIVISION'
                    : `${demoMode.replace(/_/g, ' ').toUpperCase()} VIEW`;
  // Keep `isSTP`/`stpAccent` aliases for the rest of the file's references.
  const stpAccent = accent;

  return (
    <div
      className="apex-app"
      data-demo-mode={demoMode}
      style={{
        display: 'flex',
        minHeight: '100vh',
        // Subtle full-page wash when any demo industry is active.
        background: isDemoActive
          ? `linear-gradient(180deg, ${accent}06 0%, rgba(255,255,255,0) 220px)`
          : undefined,
      }}
    >
      <AppSidebar />
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          transition: 'margin-left .25s cubic-bezier(.4,0,.2,1)',
          marginLeft,
          position: 'relative',
        }}
      >
        {/* Top accent bar — colour follows the active demo industry */}
        {isDemoActive && (
          <div
            aria-hidden
            style={{
              position: 'absolute', top: 0, left: 0, right: 0, height: 3,
              background: `linear-gradient(90deg, ${accent} 0%, ${accent}cc 50%, ${accent} 100%)`,
              zIndex: 10,
              pointerEvents: 'none',
            }}
          />
        )}
        <AppTopbar />
        <main className="light-scroll" style={{ flex: 1, padding: 32, overflowY: 'auto', position: 'relative' }}>
          {/* Demo-mode pill — bottom-right floater. Colour matches the accent. */}
          {isDemoActive && (
            <div
              style={{
                position: 'fixed',
                bottom: 24,
                right: 24,
                zIndex: 20,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '8px 14px',
                borderRadius: 999,
                background: '#fff',
                border: `1.5px solid ${accent}`,
                boxShadow: `0 4px 14px ${accent}33`,
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '.08em',
                textTransform: 'uppercase',
                color: accent,
                pointerEvents: 'none',
              }}
              aria-label={`${accentLabel} active`}
            >
              <span
                style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: accent,
                  boxShadow: `0 0 0 3px ${accent}33`,
                }}
              />
              {accentLabel}
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
