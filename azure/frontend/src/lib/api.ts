/**
 * Apex AI Platform - API Client
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApexAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('apex_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('apex_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Runbooks
  async getRunbooks() {
    const response = await this.client.get('/runbooks');
    return response.data;
  }

  async getRunbook(id: string) {
    const response = await this.client.get(`/runbooks/${id}`);
    return response.data;
  }

  async createRunbook(data: any) {
    const response = await this.client.post('/runbooks', data);
    return response.data;
  }

  async updateRunbook(id: string, data: any) {
    const response = await this.client.put(`/runbooks/${id}`, data);
    return response.data;
  }

  async deleteRunbook(id: string) {
    const response = await this.client.delete(`/runbooks/${id}`);
    return response.data;
  }

  async deployRunbook(id: string) {
    const response = await this.client.post(`/runbooks/${id}/deploy`);
    return response.data;
  }

  // Agents
  async getAgents() {
    const response = await this.client.get('/agents');
    return response.data;
  }

  async getAgent(id: string) {
    const response = await this.client.get(`/agents/${id}`);
    return response.data;
  }

  async createAgent(data: any) {
    const response = await this.client.post('/agents', data);
    return response.data;
  }

  async startAgent(id: string) {
    const response = await this.client.post(`/agents/${id}/start`);
    return response.data;
  }

  async stopAgent(id: string) {
    const response = await this.client.post(`/agents/${id}/stop`);
    return response.data;
  }

  // Work Items
  async getWorkItems(filters?: any) {
    const response = await this.client.get('/work-items', { params: filters });
    return response.data;
  }

  async getWorkItem(id: string) {
    const response = await this.client.get(`/work-items/${id}`);
    return response.data;
  }

  async assignWorkItem(id: string, agentId: string) {
    const response = await this.client.post(`/work-items/${id}/assign`, { agent_id: agentId });
    return response.data;
  }

  async completeWorkItem(id: string, result: any) {
    const response = await this.client.post(`/work-items/${id}/complete`, result);
    return response.data;
  }

  // Blueprints
  async getBlueprints() {
    const response = await this.client.get('/blueprints');
    return response.data;
  }

  async getBlueprint(id: string) {
    const response = await this.client.get(`/blueprints/${id}`);
    return response.data;
  }

  // Actions
  async getActions() {
    const response = await this.client.get('/actions');
    return response.data;
  }

  async getAction(id: string) {
    const response = await this.client.get(`/actions/${id}`);
    return response.data;
  }

  async testAction(id: string, input: any) {
    const response = await this.client.post(`/actions/${id}/test`, input);
    return response.data;
  }

  // Documents
  async uploadDocument(file: File, metadata?: any) {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    const response = await this.client.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getDocuments(filters?: any) {
    const response = await this.client.get('/documents', { params: filters });
    return response.data;
  }

  async extractDocument(id: string, blueprintId: string) {
    const response = await this.client.post(`/documents/${id}/extract`, { blueprint_id: blueprintId });
    return response.data;
  }

  // Chat / Copilot
  async sendMessage(sessionId: string, message: string, context?: any) {
    const response = await this.client.post('/chat', {
      session_id: sessionId,
      message,
      context,
    });
    return response.data;
  }

  async getChatHistory(sessionId: string) {
    const response = await this.client.get(`/chat/${sessionId}/history`);
    return response.data;
  }

  // Foundry Agent Service - Direct agent invocation
  async invokeAgent(agentId: string, prompt: string) {
    const response = await this.client.post(`/chat/invoke/${agentId}`, null, {
      params: { prompt },
    });
    return response.data;
  }

  async getAvailableAgents() {
    const response = await this.client.get('/chat/agents');
    return response.data;
  }

  // Metrics
  async getMetrics(timeRange?: string) {
    const response = await this.client.get('/metrics', { params: { time_range: timeRange } });
    return response.data;
  }

  async getAgentMetrics(agentId: string) {
    const response = await this.client.get(`/agents/${agentId}/metrics`);
    return response.data;
  }
}

export const api = new ApexAPI();
export default api;
