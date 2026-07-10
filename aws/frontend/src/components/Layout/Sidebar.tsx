/**
 * Sidebar - Main navigation component
 */

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  HomeIcon,
  DocumentTextIcon,
  CpuChipIcon,
  InboxStackIcon,
  BeakerIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  BoltIcon,
  CircleStackIcon,
  ClipboardDocumentCheckIcon,
  MicrophoneIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useApexStore } from '@/lib/store';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Canvas', href: '/canvas', icon: DocumentTextIcon },
  { name: 'Pipelines', href: '/pipelines', icon: ArrowPathIcon },
  { name: 'Actions', href: '/actions', icon: BoltIcon },
  { name: 'Voice Pipeline', href: '/voice-pipeline', icon: MicrophoneIcon },
  { name: 'Connectors', href: '/connectors', icon: CircleStackIcon },
  { name: 'Agent Hub', href: '/agent-hub', icon: InboxStackIcon },
  { name: 'Human Review', href: '/review', icon: ClipboardDocumentCheckIcon },
  { name: 'Command Center', href: '/command-center', icon: ChartBarIcon },
  { name: 'Agents', href: '/agents', icon: CpuChipIcon },
  { name: 'Testing', href: '/testing', icon: BeakerIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

export const Sidebar: React.FC = () => {
  const router = useRouter();
  const { sidebarOpen, toggleSidebar } = useApexStore();

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 h-full bg-gray-900 text-white transition-all duration-300 z-40',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-800">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-apex-500 to-purple-600 flex items-center justify-center">
            <SparklesIcon className="h-6 w-6 text-white" />
          </div>
          {sidebarOpen && (
            <div>
              <h1 className="font-bold text-lg">APEX</h1>
              <p className="text-xs text-gray-400">AI Platform</p>
            </div>
          )}
        </Link>
        <button
          onClick={toggleSidebar}
          className="p-1 hover:bg-gray-800 rounded-lg transition-colors"
        >
          {sidebarOpen ? (
            <ChevronLeftIcon className="h-5 w-5" />
          ) : (
            <ChevronRightIcon className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3 space-y-1">
        {navigation.map((item) => {
          const isActive = router.pathname === item.href ||
            (item.href !== '/' && router.pathname.startsWith(item.href));

          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200',
                isActive
                  ? 'bg-apex-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="h-6 w-6 flex-shrink-0" />
              {sidebarOpen && (
                <span className="font-medium">{item.name}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      {sidebarOpen && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-apex-500 to-purple-600 flex items-center justify-center">
              <span className="text-sm font-bold">CB</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">CBTS Admin</p>
              <p className="text-xs text-gray-400 truncate">admin@cbts.com</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
