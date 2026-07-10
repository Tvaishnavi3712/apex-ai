/**
 * Main Layout Component
 */

import React from 'react';
import { Sidebar } from './Sidebar';
import { useApexStore } from '@/lib/store';
import clsx from 'clsx';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { sidebarOpen } = useApexStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main
        className={clsx(
          'transition-all duration-300 min-h-screen',
          sidebarOpen ? 'ml-64' : 'ml-20'
        )}
      >
        {children}
      </main>
    </div>
  );
};

export default Layout;
