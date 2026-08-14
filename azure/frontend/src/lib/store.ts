/**
 * Apex AI Platform - Global State Store (Zustand)
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Types
export interface Playbook {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'deployed' | 'archived';
  intent: string;
  recipe: string;
  actions: string[];
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  name: string;
  type: 'supervisor' | 'worker' | 'collaborator';
  status: 'idle' | 'running' | 'error' | 'stopped';
  playbook_id: string;
  metrics: {
    tasks_completed: number;
    success_rate: number;
    avg_duration: number;
  };
}

export interface WorkItem {
  id: string;
  type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'review';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  assigned_agent?: string;
  data: any;
  created_at: string;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// Store State
interface ApexState {
  // Auth
  user: any | null;
  isAuthenticated: boolean;
  setUser: (user: any) => void;
  logout: () => void;

  // Playbooks
  playbooks: Playbook[];
  selectedPlaybook: Playbook | null;
  setPlaybooks: (playbooks: Playbook[]) => void;
  setSelectedPlaybook: (playbook: Playbook | null) => void;
  addPlaybook: (playbook: Playbook) => void;
  updatePlaybook: (id: string, updates: Partial<Playbook>) => void;

  // Agents
  agents: Agent[];
  selectedAgent: Agent | null;
  setAgents: (agents: Agent[]) => void;
  setSelectedAgent: (agent: Agent | null) => void;
  updateAgentStatus: (id: string, status: Agent['status']) => void;

  // Work Items
  workItems: WorkItem[];
  workItemFilters: { status?: string; priority?: string };
  setWorkItems: (items: WorkItem[]) => void;
  setWorkItemFilters: (filters: any) => void;
  addWorkItem: (item: WorkItem) => void;
  updateWorkItem: (id: string, updates: Partial<WorkItem>) => void;

  // Notifications
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;

  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  activeView: string;
  setActiveView: (view: string) => void;
}

export const useApexStore = create<ApexState>()(
  devtools(
    persist(
      (set, get) => ({
        // Auth
        user: null,
        isAuthenticated: false,
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        logout: () => set({ user: null, isAuthenticated: false }),

        // Playbooks
        playbooks: [],
        selectedPlaybook: null,
        setPlaybooks: (playbooks) => set({ playbooks }),
        setSelectedPlaybook: (playbook) => set({ selectedPlaybook: playbook }),
        addPlaybook: (playbook) => set((state) => ({ playbooks: [...state.playbooks, playbook] })),
        updatePlaybook: (id, updates) => set((state) => ({
          playbooks: state.playbooks.map((r) => r.id === id ? { ...r, ...updates } : r),
          selectedPlaybook: state.selectedPlaybook?.id === id
            ? { ...state.selectedPlaybook, ...updates }
            : state.selectedPlaybook,
        })),

        // Agents
        agents: [],
        selectedAgent: null,
        setAgents: (agents) => set({ agents }),
        setSelectedAgent: (agent) => set({ selectedAgent: agent }),
        updateAgentStatus: (id, status) => set((state) => ({
          agents: state.agents.map((a) => a.id === id ? { ...a, status } : a),
        })),

        // Work Items
        workItems: [],
        workItemFilters: {},
        setWorkItems: (items) => set({ workItems: items }),
        setWorkItemFilters: (filters) => set({ workItemFilters: filters }),
        addWorkItem: (item) => set((state) => ({ workItems: [item, ...state.workItems] })),
        updateWorkItem: (id, updates) => set((state) => ({
          workItems: state.workItems.map((w) => w.id === id ? { ...w, ...updates } : w),
        })),

        // Notifications
        notifications: [],
        addNotification: (notification) => set((state) => ({
          notifications: [
            {
              ...notification,
              id: `notif-${Date.now()}`,
              timestamp: new Date().toISOString(),
              read: false,
            },
            ...state.notifications,
          ].slice(0, 50), // Keep last 50
        })),
        markNotificationRead: (id) => set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),
        clearNotifications: () => set({ notifications: [] }),

        // UI State
        sidebarOpen: true,
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        activeView: 'dashboard',
        setActiveView: (view) => set({ activeView: view }),
      }),
      {
        name: 'apex-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    )
  )
);
