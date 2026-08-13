/**
 * Apex navigation config — ported from apex-prototype 2/index.html (NAV array).
 * Five color-coded groups, 12 routes.
 */

import type { IconName } from './icons';

export type GroupKey = 'MAIN' | 'BUILD' | 'OPERATE' | 'MONITOR' | 'CONFIGURE';

export interface NavItem {
  name: string;
  href: string;
  icon: IconName;
}

export interface NavGroup {
  group: GroupKey;
  items: NavItem[];
}

export const NAV: NavGroup[] = [
  {
    group: 'MAIN',
    items: [{ name: 'Dashboard', href: '/', icon: 'home' }],
  },
  {
    group: 'BUILD',
    items: [
      { name: 'Canvas',    href: '/canvas',    icon: 'doc' },
      { name: 'Import',    href: '/import',    icon: 'db' },
      { name: 'Pipelines', href: '/pipelines', icon: 'pipeline' },
      { name: 'Actions',   href: '/actions',   icon: 'bolt' },
    ],
  },
  {
    group: 'OPERATE',
    items: [
      { name: 'Inventory',      href: '/inventory',       icon: 'cpu' },
      { name: 'Jobs',           href: '/jobs',            icon: 'play' },
      { name: 'ApexLens',       href: '/apex-lens',       icon: 'tray' },
      { name: 'Agent Hub',      href: '/agent-hub',       icon: 'inbox' },
      { name: 'Orchestration',  href: '/orchestration',   icon: 'play' },
      { name: 'Voice Pipeline', href: '/voice-pipeline',  icon: 'mic' },
      { name: 'Human Review',   href: '/review',          icon: 'check' },
    ],
  },
  {
    group: 'MONITOR',
    items: [
      { name: 'Command Center', href: '/command-center', icon: 'chart' },
      { name: 'Agents',         href: '/agents',         icon: 'cpu' },
      { name: 'Simulator',      href: '/simulator',      icon: 'bolt' },
      { name: 'ApexSignal',     href: '/apex-signal',    icon: 'chart' },
    ],
  },
  {
    group: 'CONFIGURE',
    items: [
      { name: 'Connectors', href: '/connectors', icon: 'db' },
      { name: 'Testing',    href: '/testing',    icon: 'flask' },
      { name: 'Settings',   href: '/settings',   icon: 'gear' },
    ],
  },
];

/** Map a pathname to its owning nav group — used to color the topbar badge. */
export function groupForPath(pathname: string): GroupKey {
  // Normalise: '/canvas/playbook/abc' → should match '/canvas'
  for (const g of NAV) {
    for (const item of g.items) {
      if (pathname === item.href) return g.group;
      if (item.href !== '/' && pathname.startsWith(item.href + '/')) return g.group;
    }
  }
  // Canvas detail / new pages fall under BUILD
  if (pathname.startsWith('/canvas')) return 'BUILD';
  return 'MAIN';
}

/** Resolve human-readable page title from pathname. */
export function titleForPath(pathname: string): string {
  for (const g of NAV) {
    for (const item of g.items) {
      if (pathname === item.href) return item.name;
      if (item.href !== '/' && pathname.startsWith(item.href + '/')) return item.name;
    }
  }
  if (pathname.startsWith('/canvas/new-playbook'))  return 'New Playbook';
  if (pathname.startsWith('/canvas/new-blueprint')) return 'New Blueprint';
  if (pathname.startsWith('/canvas/playbook'))      return 'Playbook';
  if (pathname.startsWith('/canvas/blueprint'))     return 'Blueprint';
  return 'Dashboard';
}

/** Classes for active nav item by group. */
export const GROUP_ACTIVE_CLASS: Record<GroupKey, string> = {
  MAIN: 'active-main',
  BUILD: 'active-build',
  OPERATE: 'active-operate',
  MONITOR: 'active-monitor',
  CONFIGURE: 'active-configure',
};

/** Hex color for the active-rail indicator. */
export const GROUP_BAR_COLOR: Record<GroupKey, string> = {
  MAIN: '#9ca3af',
  BUILD: '#60a5fa',
  OPERATE: '#a78bfa',
  MONITOR: '#34d399',
  CONFIGURE: '#fbbf24',
};

/** CSS color for the uppercase group label above each nav group. */
export const GROUP_LABEL_COLOR: Record<GroupKey, string> = {
  MAIN: '#6b7280',
  BUILD: '#60a5fa',
  OPERATE: '#a78bfa',
  MONITOR: '#34d399',
  CONFIGURE: '#fbbf24',
};

/** Badge class used in the topbar. */
export const GROUP_BADGE_CLASS: Record<GroupKey, string> = {
  MAIN: 'badge-main',
  BUILD: 'badge-build',
  OPERATE: 'badge-operate',
  MONITOR: 'badge-monitor',
  CONFIGURE: 'badge-configure',
};
