/**
 * Tests for the global Zustand store.
 * Access state via useApexStore.getState()/setState() directly — no React renderer needed.
 */
import type { Playbook, Agent, WorkItem } from '../store';

// Mock persist + devtools so they pass through without storage/redux-devtools side effects.
jest.mock('zustand/middleware', () => ({
  persist: (fn: Function) => fn,
  devtools: (fn: Function) => fn,
}));

// Helpers: full-shape fixtures.
const makePlaybook = (id: string, name: string, overrides: Partial<Playbook> = {}): Playbook => ({
  id,
  name,
  description: '',
  status: 'draft',
  intent: '',
  recipe: '',
  actions: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  ...overrides,
});

const makeAgent = (id: string, name: string, status: Agent['status'], overrides: Partial<Agent> = {}): Agent => ({
  id,
  name,
  type: 'worker',
  status,
  playbook_id: 'pb-001',
  metrics: { tasks_completed: 0, success_rate: 1, avg_duration: 0 },
  ...overrides,
});

const makeWorkItem = (id: string, overrides: Partial<WorkItem> = {}): WorkItem => ({
  id,
  type: 'review',
  status: 'pending',
  priority: 'normal',
  data: {},
  created_at: '2026-01-01T00:00:00Z',
  ...overrides,
});

describe('Apex Store', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  describe('Auth State', () => {
    it('initializes with no user', async () => {
      const { useApexStore } = await import('../store');
      const s = useApexStore.getState();
      expect(s.user).toBeNull();
      expect(s.isAuthenticated).toBe(false);
    });

    it('sets user and updates authentication status', async () => {
      const { useApexStore } = await import('../store');
      const testUser = { id: 'user-001', name: 'Test User', email: 'test@example.com' };
      useApexStore.getState().setUser(testUser);
      expect(useApexStore.getState().user).toEqual(testUser);
      expect(useApexStore.getState().isAuthenticated).toBe(true);
    });

    it('clears user on logout', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setUser({ id: 'user-001', name: 'Test' });
      useApexStore.getState().logout();
      expect(useApexStore.getState().user).toBeNull();
      expect(useApexStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe('Playbooks State', () => {
    it('initializes with empty playbooks', async () => {
      const { useApexStore } = await import('../store');
      expect(useApexStore.getState().playbooks).toEqual([]);
      expect(useApexStore.getState().selectedPlaybook).toBeNull();
    });

    it('sets playbooks list', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setPlaybooks([
        makePlaybook('pb-001', 'Invoice Processing'),
        makePlaybook('pb-002', 'Expense Approval'),
      ]);
      expect(useApexStore.getState().playbooks).toHaveLength(2);
    });

    it('selects a playbook', async () => {
      const { useApexStore } = await import('../store');
      const playbook = makePlaybook('pb-001', 'Invoice Processing');
      useApexStore.getState().setSelectedPlaybook(playbook);
      expect(useApexStore.getState().selectedPlaybook).toEqual(playbook);
    });

    it('adds a new playbook', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setPlaybooks([]);
      useApexStore.getState().addPlaybook(makePlaybook('pb-001', 'New Playbook'));
      expect(useApexStore.getState().playbooks).toHaveLength(1);
      expect(useApexStore.getState().playbooks[0].name).toBe('New Playbook');
    });

    it('updates an existing playbook', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setPlaybooks([makePlaybook('pb-001', 'Original')]);
      useApexStore.getState().updatePlaybook('pb-001', { name: 'Updated' });
      expect(useApexStore.getState().playbooks[0].name).toBe('Updated');
    });
  });

  describe('Agents State', () => {
    it('initializes with empty agents', async () => {
      const { useApexStore } = await import('../store');
      expect(useApexStore.getState().agents).toEqual([]);
    });

    it('sets agents list', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setAgents([
        makeAgent('agent-001', 'Invoice Agent', 'running'),
        makeAgent('agent-002', 'Approval Agent', 'idle'),
      ]);
      expect(useApexStore.getState().agents).toHaveLength(2);
    });

    it('updates agent status', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setAgents([makeAgent('agent-001', 'Test', 'idle')]);
      useApexStore.getState().updateAgentStatus('agent-001', 'running');
      expect(useApexStore.getState().agents[0].status).toBe('running');
    });
  });

  describe('Work Items State', () => {
    it('initializes with empty work items', async () => {
      const { useApexStore } = await import('../store');
      expect(useApexStore.getState().workItems).toEqual([]);
    });

    it('sets work items', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setWorkItems([
        makeWorkItem('wi-001', { type: 'review', status: 'pending' }),
        makeWorkItem('wi-002', { type: 'approval', status: 'completed' }),
      ]);
      expect(useApexStore.getState().workItems).toHaveLength(2);
    });

    it('adds a work item', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setWorkItems([]);
      useApexStore.getState().addWorkItem(makeWorkItem('wi-001', { type: 'review' }));
      expect(useApexStore.getState().workItems).toHaveLength(1);
    });

    it('updates a work item', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setWorkItems([makeWorkItem('wi-001', { status: 'pending' })]);
      useApexStore.getState().updateWorkItem('wi-001', { status: 'completed' });
      expect(useApexStore.getState().workItems[0].status).toBe('completed');
    });

    it('sets work item filters', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setWorkItemFilters({ status: 'pending', priority: 'high' });
      expect(useApexStore.getState().workItemFilters.status).toBe('pending');
      expect(useApexStore.getState().workItemFilters.priority).toBe('high');
    });
  });

  describe('Notifications State', () => {
    it('adds notification', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().clearNotifications();
      useApexStore.getState().addNotification({
        type: 'success',
        title: 'Complete',
        message: 'Task completed',
      });
      expect(useApexStore.getState().notifications).toHaveLength(1);
      expect(useApexStore.getState().notifications[0].message).toBe('Task completed');
    });

    it('marks notification as read', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().clearNotifications();
      useApexStore.getState().addNotification({
        type: 'info',
        title: 'Info',
        message: 'Test',
      });
      const notifId = useApexStore.getState().notifications[0].id;
      useApexStore.getState().markNotificationRead(notifId);
      expect(useApexStore.getState().notifications[0].read).toBe(true);
    });

    it('clears all notifications', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().addNotification({ type: 'info', title: 'Hi', message: 'Test 1' });
      useApexStore.getState().addNotification({ type: 'info', title: 'Hi', message: 'Test 2' });
      useApexStore.getState().clearNotifications();
      expect(useApexStore.getState().notifications).toHaveLength(0);
    });
  });

  describe('UI State', () => {
    it('toggles sidebar', async () => {
      const { useApexStore } = await import('../store');
      const initial = useApexStore.getState().sidebarOpen;
      useApexStore.getState().toggleSidebar();
      expect(useApexStore.getState().sidebarOpen).toBe(!initial);
    });

    it('sets active view', async () => {
      const { useApexStore } = await import('../store');
      useApexStore.getState().setActiveView('blueprints');
      expect(useApexStore.getState().activeView).toBe('blueprints');
    });
  });
});
