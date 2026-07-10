import { renderHook, act } from '@testing-library/react';

// Mock zustand persist middleware
jest.mock('zustand/middleware', () => ({
  persist: (fn: Function) => fn,
  devtools: (fn: Function) => fn,
}));

describe('Apex Store', () => {
  // Reset modules before each test to get fresh store
  beforeEach(() => {
    jest.resetModules();
  });

  describe('Auth State', () => {
    it('initializes with no user', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('sets user and updates authentication status', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const testUser = { id: 'user-001', name: 'Test User', email: 'test@example.com' };

      act(() => {
        result.current.setUser(testUser);
      });

      expect(result.current.user).toEqual(testUser);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('clears user on logout', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      // First login
      act(() => {
        result.current.setUser({ id: 'user-001', name: 'Test' });
      });

      // Then logout
      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Runbooks State', () => {
    it('initializes with empty runbooks', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      expect(result.current.runbooks).toEqual([]);
      expect(result.current.selectedRunbook).toBeNull();
    });

    it('sets runbooks list', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const runbooks = [
        { id: 'rb-001', name: 'Invoice Processing' },
        { id: 'rb-002', name: 'Expense Approval' },
      ];

      act(() => {
        result.current.setRunbooks(runbooks);
      });

      expect(result.current.runbooks).toHaveLength(2);
    });

    it('selects a runbook', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const runbook = { id: 'rb-001', name: 'Invoice Processing' };

      act(() => {
        result.current.setSelectedRunbook(runbook);
      });

      expect(result.current.selectedRunbook).toEqual(runbook);
    });

    it('adds a new runbook', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.addRunbook({ id: 'rb-001', name: 'New Runbook' });
      });

      expect(result.current.runbooks).toHaveLength(1);
      expect(result.current.runbooks[0].name).toBe('New Runbook');
    });

    it('updates an existing runbook', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      // Add runbook first
      act(() => {
        result.current.setRunbooks([{ id: 'rb-001', name: 'Original' }]);
      });

      // Update it
      act(() => {
        result.current.updateRunbook('rb-001', { name: 'Updated' });
      });

      expect(result.current.runbooks[0].name).toBe('Updated');
    });
  });

  describe('Agents State', () => {
    it('initializes with empty agents', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      expect(result.current.agents).toEqual([]);
    });

    it('sets agents list', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const agents = [
        { id: 'agent-001', name: 'Invoice Agent', status: 'running' },
        { id: 'agent-002', name: 'Approval Agent', status: 'idle' },
      ];

      act(() => {
        result.current.setAgents(agents);
      });

      expect(result.current.agents).toHaveLength(2);
    });

    it('updates agent status', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.setAgents([
          { id: 'agent-001', name: 'Test', status: 'idle' },
        ]);
      });

      act(() => {
        result.current.updateAgentStatus('agent-001', 'running');
      });

      expect(result.current.agents[0].status).toBe('running');
    });
  });

  describe('Work Items State', () => {
    it('initializes with empty work items', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      expect(result.current.workItems).toEqual([]);
    });

    it('sets work items', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const items = [
        { id: 'wi-001', type: 'review', status: 'pending' },
        { id: 'wi-002', type: 'approval', status: 'completed' },
      ];

      act(() => {
        result.current.setWorkItems(items);
      });

      expect(result.current.workItems).toHaveLength(2);
    });

    it('adds a work item', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.addWorkItem({ id: 'wi-001', type: 'review' });
      });

      expect(result.current.workItems).toHaveLength(1);
    });

    it('updates a work item', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.setWorkItems([{ id: 'wi-001', status: 'pending' }]);
      });

      act(() => {
        result.current.updateWorkItem('wi-001', { status: 'completed' });
      });

      expect(result.current.workItems[0].status).toBe('completed');
    });

    it('sets work item filters', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.setWorkItemFilters({ status: 'pending', priority: 'high' });
      });

      expect(result.current.workItemFilters.status).toBe('pending');
      expect(result.current.workItemFilters.priority).toBe('high');
    });
  });

  describe('Notifications State', () => {
    it('adds notification', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.addNotification({
          type: 'success',
          message: 'Task completed',
        });
      });

      expect(result.current.notifications).toHaveLength(1);
      expect(result.current.notifications[0].message).toBe('Task completed');
    });

    it('marks notification as read', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.addNotification({
          id: 'notif-001',
          type: 'info',
          message: 'Test',
        });
      });

      act(() => {
        result.current.markNotificationRead('notif-001');
      });

      expect(result.current.notifications[0].read).toBe(true);
    });

    it('clears all notifications', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.addNotification({ type: 'info', message: 'Test 1' });
        result.current.addNotification({ type: 'info', message: 'Test 2' });
      });

      act(() => {
        result.current.clearNotifications();
      });

      expect(result.current.notifications).toHaveLength(0);
    });
  });

  describe('UI State', () => {
    it('toggles sidebar', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      const initialState = result.current.sidebarOpen;

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.sidebarOpen).toBe(!initialState);
    });

    it('sets active view', async () => {
      const { useApexStore } = await import('../store');
      const { result } = renderHook(() => useApexStore());

      act(() => {
        result.current.setActiveView('blueprints');
      });

      expect(result.current.activeView).toBe('blueprints');
    });
  });
});
