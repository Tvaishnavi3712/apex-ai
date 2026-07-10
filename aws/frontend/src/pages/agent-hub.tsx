/**
 * Agent Hub Page - Agent Chat & Work Queue
 * Fetches real data from backend APIs
 * Enhanced with document viewing and work item processing
 */

import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Button, StatusBadge, Badge } from '@/components/common';
import api from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import {
  ChatBubbleLeftRightIcon,
  InboxStackIcon,
  PaperAirplaneIcon,
  PaperClipIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  FunnelIcon,
  ArrowPathIcon,
  EyeIcon,
  PlayIcon,
  XMarkIcon,
  DocumentMagnifyingGlassIcon,
  ArrowRightIcon,
  SparklesIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type TabType = 'chat' | 'queue';
type QueueFilter = 'all' | 'pending' | 'processing' | 'needs_review' | 'completed' | 'failed';

interface Agent {
  agent_id: string;
  name: string;
  status: string;
  description?: string;
  type?: string;
}

interface ProcessingLogEntry {
  timestamp: string;
  stage: string;
  details: {
    message: string;
    [key: string]: any;
  };
}

interface WorkItem {
  work_item_id: string;
  document_name?: string;
  document_type?: string;
  document_url?: string;
  agent_id?: string;
  status: string;
  processing_stage?: string;
  current_stage_details?: any;
  processing_log?: ProcessingLogEntry[];
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
  payload?: {
    property_name?: string;
    submission_id?: string;
    document_type?: string;
    s3_uri?: string;
    extracted_data?: any;
  };
}

interface ReasoningStep {
  step: number;
  thought: string;
  action?: string;
}

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  attachments?: string[];
  reasoning?: ReasoningStep[];
}

export default function AgentHub() {
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [message, setMessage] = useState('');
  const [queueFilter, setQueueFilter] = useState<QueueFilter>('all');
  const [loading, setLoading] = useState(true);

  // State for agents and work items from API
  const [agents, setAgents] = useState<Agent[]>([]);
  const [workQueue, setWorkQueue] = useState<WorkItem[]>([]);

  // Document viewer and work item detail state
  const [selectedWorkItem, setSelectedWorkItem] = useState<WorkItem | null>(null);
  const [showDocumentViewer, setShowDocumentViewer] = useState(false);
  const [showWorkItemDetail, setShowWorkItemDetail] = useState(false);
  const [processingItem, setProcessingItem] = useState<string | null>(null);

  // Agentic processing state
  const [showProcessingModal, setShowProcessingModal] = useState(false);
  const [processingWorkItem, setProcessingWorkItem] = useState<WorkItem | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch data from APIs
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      try {
        const [agentsRes, workItemsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/agents/`),
          fetch(`${API_BASE_URL}/work-items/`),
        ]);

        const agentsData = agentsRes.ok ? await agentsRes.json() : [];
        const workItemsData = workItemsRes.ok ? await workItemsRes.json() : [];

        setAgents(agentsData);
        setWorkQueue(workItemsData);

        // Select first active agent by default
        if (agentsData.length > 0) {
          const activeAgent = agentsData.find((a: Agent) => a.status === 'active') || agentsData[0];
          setSelectedAgent(activeAgent.agent_id);
        }
      } catch (err) {
        console.error('Failed to fetch agent hub data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Chat messages - initialized based on selected agent
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update welcome message when agent changes
  useEffect(() => {
    const agent = agents.find(a => a.agent_id === selectedAgent);
    if (agent) {
      const isUnderwritingAgent = agent.name.toLowerCase().includes('underwrite') ||
                                   agent.description?.toLowerCase().includes('underwriting');

      const welcomeMessage = isUnderwritingAgent
        ? `Hello! I'm **${agent.name}**, your CRE Underwriting Assistant.

I have **3 submissions** in the queue ready for review:
- **CRE-2026-001-MUP** - Chicago Mixed-Use Portfolio ($226M)
- **CRE-2026-002-IND** - Industrial Portfolio ($372M)
- **CRE-2026-003-HRT** - Miami Hotels & Retail ($505M)

I can help you with:
- Risk assessments and scoring
- Premium calculations
- Loss history analysis
- Underwriting decisions and recommendations

What would you like to review first?`
        : `Hello! I'm ${agent.name}. ${agent.description || 'I\'m here to help you with your tasks.'}\n\nHow can I assist you today?`;

      setMessages([{
        id: '1',
        role: 'agent',
        content: welcomeMessage,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    }
  }, [selectedAgent, agents]);

  // Helper function to format time
  const formatTime = (dateStr?: string): string => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  };

  // Get document name from work item
  const getDocumentName = (item: WorkItem): string => {
    if (item.document_name) return item.document_name;
    if (item.payload?.property_name) return item.payload.property_name;
    if (item.payload?.submission_id) return item.payload.submission_id;
    return item.work_item_id;
  };

  // Get document type from work item
  const getDocumentType = (item: WorkItem): string => {
    if (item.document_type) return item.document_type;
    if (item.payload?.document_type) return item.payload.document_type;
    return 'Document';
  };

  // Get agent name from agent_id
  const getAgentName = (agentId?: string): string => {
    if (!agentId) return 'Unknown';
    const agent = agents.find(a => a.agent_id === agentId);
    return agent?.name || agentId;
  };

  const filteredQueue = queueFilter === 'all'
    ? workQueue
    : queueFilter === 'processing'
      ? workQueue.filter(item => item.status === 'processing' || item.status === 'executing')
      : workQueue.filter(item => item.status === queueFilter);

  // Process a work item (move through status workflow)
  const handleProcessWorkItem = async (item: WorkItem) => {
    setProcessingItem(item.work_item_id);

    try {
      // Determine next status based on current status
      let nextStatus = 'processing';
      if (item.status === 'pending') {
        nextStatus = 'processing';
      } else if (item.status === 'processing') {
        nextStatus = 'completed';
      }

      // Update status via API
      const res = await fetch(`${API_BASE_URL}/work-items/${item.work_item_id}/status?status=${nextStatus}`, {
        method: 'PUT',
      });

      if (res.ok) {
        // Update local state
        setWorkQueue(prev => prev.map(w => {
          if (w.work_item_id === item.work_item_id) {
            const now = new Date().toISOString();
            return {
              ...w,
              status: nextStatus,
              started_at: nextStatus === 'processing' ? now : w.started_at,
              completed_at: nextStatus === 'completed' ? now : w.completed_at,
              result: nextStatus === 'completed' ? generateMockExtractionResult(w) : w.result,
            };
          }
          return w;
        }));
      }
    } catch (err) {
      console.error('Failed to process work item:', err);
    } finally {
      setProcessingItem(null);
    }
  };

  // Generate mock extraction result for demo
  const generateMockExtractionResult = (item: WorkItem) => {
    return {
      extraction_confidence: 0.94,
      fields_extracted: 24,
      processing_time_ms: 2340,
      extracted_data: {
        property_name: item.payload?.property_name || 'Sample Property',
        property_type: 'Commercial Office',
        total_insured_value: '$5,250,000',
        location: '500 Michigan Ave, Chicago, IL 60611',
        construction_type: 'Fire Resistive',
        year_built: 1995,
        square_footage: '125,000 sq ft',
        occupancy: 'Professional Office',
        risk_score: 78,
      },
    };
  };

  // View document
  const handleViewDocument = (item: WorkItem) => {
    setSelectedWorkItem(item);
    setShowDocumentViewer(true);
  };

  // View work item details
  const handleViewDetails = (item: WorkItem) => {
    setSelectedWorkItem(item);
    setShowWorkItemDetail(true);
  };

  // Get sample PDF URL for demo
  const getSampleDocumentUrl = (item: WorkItem): string => {
    // Return a sample PDF URL for demo purposes
    // In production, this would be the actual S3 presigned URL
    return item.document_url || item.payload?.s3_uri || 'https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf';
  };

  // Create demo CRE submission using the new API
  const handleCreateDemoSubmission = async () => {
    try {
      const types = ['chicago', 'industrial', 'miami'];
      const randomType = types[Math.floor(Math.random() * types.length)];

      const res = await fetch(`${API_BASE_URL}/work-items/demo/create-submission?submission_type=${randomType}`, {
        method: 'POST',
      });

      if (res.ok) {
        const data = await res.json();
        // Refresh the work queue
        const workItemsRes = await fetch(`${API_BASE_URL}/work-items/`);
        if (workItemsRes.ok) {
          const workItemsData = await workItemsRes.json();
          setWorkQueue(workItemsData);
        }
      }
    } catch (err) {
      console.error('Failed to create demo submission:', err);
    }
  };

  // Start agentic processing with real-time status updates
  const handleStartAgentProcessing = async (item: WorkItem) => {
    setProcessingWorkItem(item);
    setShowProcessingModal(true);
    setIsPolling(true);

    try {
      // Start the processing
      const res = await fetch(`${API_BASE_URL}/work-items/${item.work_item_id}/process`, {
        method: 'POST',
      });

      if (res.ok) {
        // Start polling for status updates
        startStatusPolling(item.work_item_id);
      }
    } catch (err) {
      console.error('Failed to start processing:', err);
      setIsPolling(false);
    }
  };

  // Poll for processing status
  const startStatusPolling = (workItemId: string) => {
    // Clear any existing polling
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/work-items/${workItemId}/processing-status`);
        if (res.ok) {
          const status = await res.json();

          // Update the processing work item
          setProcessingWorkItem(prev => prev ? {
            ...prev,
            status: status.status,
            processing_stage: status.processing_stage,
            current_stage_details: status.current_stage_details,
            processing_log: status.processing_log,
            result: status.result,
          } : null);

          // Update work queue
          setWorkQueue(prev => prev.map(w =>
            w.work_item_id === workItemId ? {
              ...w,
              status: status.status,
              processing_stage: status.processing_stage,
              result: status.result,
            } : w
          ));

          // Stop polling if processing is complete
          if (status.status === 'completed' || status.status === 'needs_review' || status.status === 'failed') {
            setIsPolling(false);
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    // Poll every 500ms for smooth updates
    pollingRef.current = setInterval(poll, 500);
    // Also poll immediately
    poll();
  };

  // Stop polling when modal closes
  const handleCloseProcessingModal = () => {
    setShowProcessingModal(false);
    setIsPolling(false);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    // Refresh work queue
    fetch(`${API_BASE_URL}/work-items/`)
      .then(res => res.json())
      .then(data => setWorkQueue(data))
      .catch(err => console.error('Failed to refresh:', err));
  };

  // Approve a work item
  const handleApproveWorkItem = async (workItemId: string) => {
    try {
      const res = await fetch(
        `${API_BASE_URL}/work-items/${workItemId}/approve?approver=Michael Torres&comments=Approved after review`,
        { method: 'POST' }
      );

      if (res.ok) {
        // Refresh status
        const statusRes = await fetch(`${API_BASE_URL}/work-items/${workItemId}/processing-status`);
        if (statusRes.ok) {
          const status = await statusRes.json();
          setProcessingWorkItem(prev => prev ? { ...prev, ...status } : null);
          setWorkQueue(prev => prev.map(w =>
            w.work_item_id === workItemId ? { ...w, status: 'completed' } : w
          ));
        }
      }
    } catch (err) {
      console.error('Failed to approve:', err);
    }
  };

  // Get stage display info
  const getStageInfo = (stage: string) => {
    const stages: Record<string, { label: string; color: string; icon: string }> = {
      pending: { label: 'Pending', color: 'gray', icon: '⏳' },
      queued: { label: 'Queued', color: 'blue', icon: '📋' },
      extracting: { label: 'Extracting Data', color: 'blue', icon: '📄' },
      validating: { label: 'Validating', color: 'blue', icon: '✓' },
      analyzing_risk: { label: 'Analyzing Risk', color: 'yellow', icon: '⚠️' },
      calculating_premium: { label: 'Calculating Premium', color: 'yellow', icon: '💰' },
      checking_loss_history: { label: 'Checking Loss History', color: 'yellow', icon: '📊' },
      making_decision: { label: 'Making Decision', color: 'purple', icon: '🤔' },
      requires_approval: { label: 'Requires Approval', color: 'orange', icon: '👤' },
      approved: { label: 'Approved', color: 'green', icon: '✅' },
      completed: { label: 'Completed', color: 'green', icon: '🎉' },
      failed: { label: 'Failed', color: 'red', icon: '❌' },
    };
    return stages[stage] || { label: stage, color: 'gray', icon: '•' };
  };

  // Create sample work item for demo (legacy)
  const handleCreateSampleWorkItem = async () => {
    const sampleNames = [
      'Midwest Office Partners Submission',
      'Harbor Industrial Complex Application',
      'Downtown Retail Center SOV',
      'Tech Campus Property Appraisal',
      'Suburban Medical Plaza',
    ];
    const sampleTypes = [
      'ACORD 125 Application',
      'Statement of Values',
      'Loss Run Report',
      'Property Appraisal',
      'Insurance Submission',
    ];

    const randomIndex = Math.floor(Math.random() * sampleNames.length);

    try {
      const res = await fetch(`${API_BASE_URL}/work-items/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_name: sampleNames[randomIndex],
          document_type: sampleTypes[randomIndex],
          agent_id: agents.length > 0 ? agents[0].agent_id : undefined,
          playbook_id: 'cre-underwriting-playbook',
          payload: {
            property_name: sampleNames[randomIndex],
            document_type: sampleTypes[randomIndex],
            s3_uri: `s3://apex-documents/submissions/${Date.now()}.pdf`,
          },
        }),
      });

      if (res.ok) {
        const newItem = await res.json();
        setWorkQueue(prev => [newItem, ...prev]);
      }
    } catch (err) {
      console.error('Failed to create sample work item:', err);
    }
  };

  const [isLoading, setIsLoading] = useState(false);

  // Send a specific message (used by suggested prompts)
  const sendSpecificMessage = async (specificMessage: string) => {
    if (!specificMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: specificMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.invokeAgent(selectedAgent, specificMessage);

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: response.response || 'I received your message but could not generate a response.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        reasoning: response.reasoning || [],
      };
      setMessages(prev => [...prev, agentResponse]);
    } catch (error: any) {
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: `I apologize, I encountered an error: ${error.message || 'Unable to process request'}. Please try again.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = message;
    setMessage('');
    setIsLoading(true);

    try {
      // Call real AgentCore API
      const response = await api.invokeAgent(selectedAgent, currentMessage);

      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: response.response || 'I received your message but could not generate a response.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        reasoning: response.reasoning || [],
      };
      setMessages(prev => [...prev, agentResponse]);
    } catch (error: any) {
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: `I apologize, I encountered an error: ${error.message || 'Unable to process request'}. Please try again.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'processing':
      case 'executing': return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'pending': return <ClockIcon className="h-5 w-5 text-gray-400" />;
      case 'needs_review': return <ExclamationTriangleIcon className="h-5 w-5 text-orange-500" />;
      case 'failed': return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default: return null;
    }
  };

  const queueStats = {
    total: workQueue.length,
    pending: workQueue.filter(i => i.status === 'pending').length,
    processing: workQueue.filter(i => i.status === 'processing' || i.status === 'executing').length,
    needs_review: workQueue.filter(i => i.status === 'needs_review').length,
    completed: workQueue.filter(i => i.status === 'completed').length,
    failed: workQueue.filter(i => i.status === 'failed').length,
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-500">Loading agent hub...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Agent Hub | APEX AI Platform</title>
      </Head>

      <div className="p-8 h-[calc(100vh-2rem)]">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Agent Hub</h1>
            <p className="text-gray-500 mt-1">Chat with agents and manage work queue</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'chat'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <ChatBubbleLeftRightIcon className="h-5 w-5" />
            Agent Chat
          </button>
          <button
            onClick={() => setActiveTab('queue')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'queue'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <InboxStackIcon className="h-5 w-5" />
            Work Queue
            <Badge variant="primary">{queueStats.pending + queueStats.processing}</Badge>
          </button>
        </div>

        {/* Content */}
        {activeTab === 'chat' ? (
          <div className="flex gap-6 h-[calc(100%-8rem)]">
            {/* Agent List */}
            <div className="w-64 flex-shrink-0">
              <Card className="h-full">
                <CardHeader title="Agents" />
                <div className="p-2 space-y-1">
                  {agents.length === 0 ? (
                    <div className="text-center py-4 text-gray-500">
                      <p>No agents available</p>
                    </div>
                  ) : (
                    agents.map(agent => (
                      <button
                        key={agent.agent_id}
                        onClick={() => setSelectedAgent(agent.agent_id)}
                        className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                          selectedAgent === agent.agent_id
                            ? 'bg-apex-50 border border-apex-200'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="relative">
                          <div className="w-10 h-10 bg-gradient-to-br from-apex-500 to-purple-600 rounded-full flex items-center justify-center">
                            <CpuChipIcon className="h-5 w-5 text-white" />
                          </div>
                          <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${
                            agent.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                          }`} />
                        </div>
                        <div className="flex-1 text-left">
                          <p className="font-medium text-gray-900">{agent.name}</p>
                          <p className="text-xs text-gray-500">{agent.description || agent.type || 'AI Agent'}</p>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </Card>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              <Card className="flex-1 flex flex-col">
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-200 flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-apex-500 to-purple-600 rounded-full flex items-center justify-center">
                    <CpuChipIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {agents.find(a => a.agent_id === selectedAgent)?.name || 'Select an Agent'}
                    </h3>
                    <p className={`text-sm ${agents.find(a => a.agent_id === selectedAgent)?.status === 'active' ? 'text-green-500' : 'text-gray-400'}`}>
                      {agents.find(a => a.agent_id === selectedAgent)?.status === 'active' ? 'Online' : 'Offline'}
                    </p>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 p-4 overflow-y-auto space-y-4">
                  {messages.map(msg => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${
                        msg.role === 'user'
                          ? 'bg-apex-500 text-white rounded-2xl rounded-br-md'
                          : 'bg-gray-100 text-gray-900 rounded-2xl rounded-bl-md'
                      } px-4 py-3`}>
                        {msg.role === 'agent' && msg.reasoning && msg.reasoning.length > 0 && (
                          <details className="mb-3 text-xs">
                            <summary className="cursor-pointer text-apex-600 font-medium flex items-center gap-1 hover:text-apex-700">
                              <SparklesIcon className="h-3.5 w-3.5" />
                              View reasoning ({msg.reasoning.length} steps)
                            </summary>
                            <div className="mt-2 pl-2 border-l-2 border-apex-200 space-y-1">
                              {msg.reasoning.map((step, idx) => (
                                <div key={idx} className="text-gray-600">
                                  <span className="font-medium text-apex-600">Step {step.step}:</span> {step.thought}
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                        {msg.role === 'agent' ? (
                          <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-headings:font-semibold prose-headings:mt-2 prose-headings:mb-1 prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-table:my-2 prose-th:px-2 prose-th:py-1 prose-td:px-2 prose-td:py-1 prose-th:bg-gray-200 prose-strong:text-gray-900">
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap">{msg.content}</p>
                        )}
                        <p className={`text-xs mt-2 ${
                          msg.role === 'user' ? 'text-apex-200' : 'text-gray-400'
                        }`}>{msg.timestamp}</p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-bl-md px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-apex-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-apex-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-apex-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                          <span className="text-sm text-gray-500">Analyzing your request...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Suggested Prompts */}
                {messages.length <= 1 && !isLoading && (
                  <div className="px-4 pb-2 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-2 pt-2">Suggested questions:</p>
                    <div className="flex flex-wrap gap-2">
                      {[
                        "What's in the queue?",
                        "Tell me about the Miami hotels deal",
                        "Compare all submissions",
                        "What are the key concerns?",
                        "Which deal has the best risk profile?",
                      ].map((prompt, idx) => (
                        <button
                          key={idx}
                          onClick={() => sendSpecificMessage(prompt)}
                          className="px-3 py-1.5 text-sm bg-apex-50 text-apex-700 rounded-full hover:bg-apex-100 transition-colors"
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Input */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex items-center gap-3">
                    <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors" disabled={isLoading}>
                      <PaperClipIcon className="h-5 w-5" />
                    </button>
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                      placeholder={isLoading ? "Analyzing your request..." : "Ask about deals, risk scores, premiums, or decisions..."}
                      disabled={isLoading}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                    />
                    <Button
                      variant="primary"
                      onClick={handleSendMessage}
                      disabled={isLoading || !message.trim()}
                      icon={<PaperAirplaneIcon className="h-5 w-5" />}
                    >
                      {isLoading ? 'Sending...' : 'Send'}
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        ) : (
          <div>
            {/* Queue Header with Add Sample Button */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Work Items</h2>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<ArrowPathIcon className="h-4 w-4" />}
                  onClick={async () => {
                    const res = await fetch(`${API_BASE_URL}/work-items/`);
                    if (res.ok) {
                      const data = await res.json();
                      setWorkQueue(data);
                    }
                  }}
                >
                  Refresh
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  icon={<PlusIcon className="h-4 w-4" />}
                  onClick={handleCreateDemoSubmission}
                >
                  Add CRE Submission
                </Button>
              </div>
            </div>

            {/* Queue Stats */}
            <div className="grid grid-cols-6 gap-4 mb-6">
              {[
                { label: 'Total', value: queueStats.total, filter: 'all' as QueueFilter },
                { label: 'Pending', value: queueStats.pending, filter: 'pending' as QueueFilter },
                { label: 'Processing', value: queueStats.processing, filter: 'processing' as QueueFilter },
                { label: 'Needs Review', value: queueStats.needs_review, filter: 'needs_review' as QueueFilter, highlight: true },
                { label: 'Completed', value: queueStats.completed, filter: 'completed' as QueueFilter },
                { label: 'Failed', value: queueStats.failed, filter: 'failed' as QueueFilter },
              ].map(stat => (
                <button
                  key={stat.filter}
                  onClick={() => setQueueFilter(stat.filter)}
                  className={`p-4 rounded-xl border transition-colors ${
                    queueFilter === stat.filter
                      ? 'border-apex-500 bg-apex-50'
                      : stat.filter === 'needs_review' && stat.value > 0
                        ? 'border-orange-300 bg-orange-50 hover:border-orange-400'
                        : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <p className={`text-sm ${stat.filter === 'needs_review' && stat.value > 0 ? 'text-orange-600' : 'text-gray-500'}`}>
                    {stat.label}
                  </p>
                  <p className={`text-2xl font-bold ${stat.filter === 'needs_review' && stat.value > 0 ? 'text-orange-600' : 'text-gray-900'}`}>
                    {stat.value}
                  </p>
                </button>
              ))}
            </div>

            {/* Queue List */}
            <Card>
              <div className="divide-y divide-gray-200">
                {filteredQueue.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <InboxStackIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                    <p>No work items found</p>
                  </div>
                ) : (
                  filteredQueue.map(item => (
                    <div key={item.work_item_id} className={`p-4 flex items-center justify-between hover:bg-gray-50 ${
                      (item.status === 'executing' || item.status === 'processing') ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}>
                      <div className="flex items-center gap-4">
                        {getStatusIcon(item.status)}
                        <div className={`p-2 rounded-lg ${
                          (item.status === 'executing' || item.status === 'processing') ? 'bg-blue-100' : 'bg-gray-100'
                        }`}>
                          <DocumentTextIcon className={`h-5 w-5 ${
                            (item.status === 'executing' || item.status === 'processing') ? 'text-blue-600' : 'text-gray-600'
                          }`} />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{getDocumentName(item)}</p>
                          <div className="flex items-center gap-2">
                            <p className="text-sm text-gray-500">{getDocumentType(item)} • {getAgentName(item.agent_id)}</p>
                            {/* Show processing stage for items being processed */}
                            {item.processing_stage && (item.status === 'executing' || item.status === 'processing') && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                                <ArrowPathIcon className="h-3 w-3 animate-spin" />
                                {getStageInfo(item.processing_stage).label}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Submitted</p>
                          <p className="font-medium">{formatTime(item.created_at)}</p>
                        </div>
                        {item.completed_at && (
                          <div className="text-right">
                            <p className="text-sm text-gray-500">Completed</p>
                            <p className="font-medium">{formatTime(item.completed_at)}</p>
                          </div>
                        )}
                        {/* Status badge with special handling for executing status */}
                        {(item.status === 'executing' || item.status === 'processing') ? (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                            <ArrowPathIcon className="h-4 w-4 animate-spin" />
                            Processing
                          </span>
                        ) : item.status === 'needs_review' ? (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-700 text-sm font-medium rounded-full">
                            <ExclamationTriangleIcon className="h-4 w-4" />
                            Needs Review
                          </span>
                        ) : (
                          <StatusBadge status={item.status as any} />
                        )}
                        <div className="flex items-center gap-2 ml-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<EyeIcon className="h-4 w-4" />}
                            onClick={() => handleViewDocument(item)}
                            title="View Document"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<DocumentMagnifyingGlassIcon className="h-4 w-4" />}
                            onClick={() => handleViewDetails(item)}
                            title="View Details"
                          />
                          {item.status === 'pending' && (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={<PlayIcon className="h-4 w-4" />}
                              onClick={() => handleStartAgentProcessing(item)}
                            >
                              Process
                            </Button>
                          )}
                          {/* View Progress button for items being processed */}
                          {(item.status === 'executing' || item.status === 'processing') && (
                            <Button
                              variant="secondary"
                              size="sm"
                              icon={<ArrowPathIcon className="h-4 w-4 animate-spin" />}
                              onClick={() => {
                                setProcessingWorkItem(item);
                                setShowProcessingModal(true);
                                startStatusPolling(item.work_item_id);
                              }}
                            >
                              View Progress
                            </Button>
                          )}
                          {item.status === 'needs_review' && (
                            <Button
                              variant="primary"
                              size="sm"
                              icon={<ExclamationTriangleIcon className="h-4 w-4" />}
                              onClick={() => {
                                setProcessingWorkItem(item);
                                setShowProcessingModal(true);
                                // Fetch current status
                                fetch(`${API_BASE_URL}/work-items/${item.work_item_id}/processing-status`)
                                  .then(res => res.json())
                                  .then(status => setProcessingWorkItem({...item, ...status}))
                                  .catch(console.error);
                              }}
                            >
                              Review & Approve
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        )}

        {/* Document Viewer Modal */}
        {showDocumentViewer && selectedWorkItem && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl h-[85vh] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-apex-100 rounded-lg">
                    <DocumentTextIcon className="h-6 w-6 text-apex-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getDocumentName(selectedWorkItem)}</h3>
                    <p className="text-sm text-gray-500">{getDocumentType(selectedWorkItem)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={selectedWorkItem.status as any} />
                  <button
                    onClick={() => setShowDocumentViewer(false)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="flex-1 flex">
                {/* Document Preview */}
                <div className="flex-1 bg-gray-100 p-4">
                  <div className="h-full bg-white rounded-lg shadow-inner flex items-center justify-center">
                    {/* For demo, show a sample document representation */}
                    <div className="text-center p-8">
                      <div className="w-full max-w-md mx-auto bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8">
                        <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                        <h4 className="font-medium text-gray-900 mb-2">Document Preview</h4>
                        <p className="text-sm text-gray-500 mb-4">
                          {getDocumentName(selectedWorkItem)}
                        </p>
                        <div className="text-left bg-white p-4 rounded-lg border border-gray-200 text-sm">
                          <p className="font-mono text-gray-600">
                            <span className="text-gray-400">S3 URI:</span><br />
                            s3://apex-documents/{selectedWorkItem.work_item_id}.pdf
                          </p>
                        </div>
                        <p className="text-xs text-gray-400 mt-4">
                          In production, the actual PDF would render here using a PDF viewer component.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Extraction Results Panel */}
                <div className="w-80 border-l border-gray-200 p-4 overflow-y-auto">
                  <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <SparklesIcon className="h-5 w-5 text-apex-500" />
                    Extraction Results
                  </h4>

                  {selectedWorkItem.status === 'completed' && selectedWorkItem.result ? (
                    <div className="space-y-4">
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-800">Extraction Complete</p>
                        <p className="text-xs text-green-600">
                          Confidence: {(selectedWorkItem.result.extraction_confidence * 100).toFixed(0)}%
                        </p>
                      </div>

                      <div className="space-y-3">
                        {Object.entries(selectedWorkItem.result.extracted_data || {}).map(([key, value]) => (
                          <div key={key} className="p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500 uppercase tracking-wide">
                              {key.replace(/_/g, ' ')}
                            </p>
                            <p className="font-medium text-gray-900 mt-1">{String(value)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : selectedWorkItem.status === 'processing' ? (
                    <div className="text-center py-8">
                      <ArrowPathIcon className="h-8 w-8 text-apex-500 animate-spin mx-auto mb-3" />
                      <p className="text-sm text-gray-600">Extracting data...</p>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <ClockIcon className="h-8 w-8 text-gray-300 mx-auto mb-3" />
                      <p className="text-sm text-gray-500">Pending extraction</p>
                      <Button
                        variant="primary"
                        size="sm"
                        className="mt-4"
                        onClick={() => handleProcessWorkItem(selectedWorkItem)}
                      >
                        Start Processing
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Work Item Detail Modal */}
        {showWorkItemDetail && selectedWorkItem && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-2xl max-h-[85vh] overflow-auto">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-apex-100 rounded-lg">
                    <DocumentMagnifyingGlassIcon className="h-6 w-6 text-apex-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Work Item Details</h3>
                    <p className="text-sm text-gray-500">{selectedWorkItem.work_item_id}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowWorkItemDetail(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Status Timeline */}
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Processing Timeline</h4>
                <div className="flex items-center gap-2">
                  <div className={`flex items-center gap-2 p-2 rounded-lg ${
                    selectedWorkItem.status !== 'pending' ? 'bg-green-50' : 'bg-gray-100'
                  }`}>
                    <CheckCircleIcon className={`h-5 w-5 ${
                      selectedWorkItem.status !== 'pending' ? 'text-green-500' : 'text-gray-400'
                    }`} />
                    <span className="text-sm">Pending</span>
                  </div>
                  <ArrowRightIcon className="h-4 w-4 text-gray-400" />
                  <div className={`flex items-center gap-2 p-2 rounded-lg ${
                    selectedWorkItem.status === 'processing' ? 'bg-blue-50' :
                    selectedWorkItem.status === 'completed' ? 'bg-green-50' : 'bg-gray-100'
                  }`}>
                    {selectedWorkItem.status === 'processing' ? (
                      <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />
                    ) : selectedWorkItem.status === 'completed' ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    ) : (
                      <ClockIcon className="h-5 w-5 text-gray-400" />
                    )}
                    <span className="text-sm">Processing</span>
                  </div>
                  <ArrowRightIcon className="h-4 w-4 text-gray-400" />
                  <div className={`flex items-center gap-2 p-2 rounded-lg ${
                    selectedWorkItem.status === 'completed' ? 'bg-green-50' : 'bg-gray-100'
                  }`}>
                    <CheckCircleIcon className={`h-5 w-5 ${
                      selectedWorkItem.status === 'completed' ? 'text-green-500' : 'text-gray-400'
                    }`} />
                    <span className="text-sm">Completed</span>
                  </div>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Document</p>
                  <p className="font-medium text-gray-900">{getDocumentName(selectedWorkItem)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Type</p>
                  <p className="font-medium text-gray-900">{getDocumentType(selectedWorkItem)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Agent</p>
                  <p className="font-medium text-gray-900">{getAgentName(selectedWorkItem.agent_id)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Status</p>
                  <StatusBadge status={selectedWorkItem.status as any} />
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Created</p>
                  <p className="font-medium text-gray-900">{formatTime(selectedWorkItem.created_at)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 uppercase">Completed</p>
                  <p className="font-medium text-gray-900">{selectedWorkItem.completed_at ? formatTime(selectedWorkItem.completed_at) : '-'}</p>
                </div>
              </div>

              {/* Extraction Results */}
              {selectedWorkItem.status === 'completed' && selectedWorkItem.result && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Extracted Data</h4>
                  <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-60">
                    <pre className="text-sm text-green-400">
                      {JSON.stringify(selectedWorkItem.result.extracted_data || selectedWorkItem.result, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setShowWorkItemDetail(false)}
                >
                  Close
                </Button>
                <Button
                  variant="secondary"
                  icon={<EyeIcon className="h-4 w-4" />}
                  onClick={() => {
                    setShowWorkItemDetail(false);
                    setShowDocumentViewer(true);
                  }}
                >
                  View Document
                </Button>
                {selectedWorkItem.status === 'pending' && (
                  <Button
                    variant="primary"
                    icon={<PlayIcon className="h-4 w-4" />}
                    onClick={() => handleStartAgentProcessing(selectedWorkItem)}
                  >
                    Process Now
                  </Button>
                )}
              </div>
            </Card>
          </div>
        )}

        {/* Agentic Processing Modal */}
        {showProcessingModal && processingWorkItem && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    processingWorkItem.status === 'completed' ? 'bg-green-100' :
                    processingWorkItem.status === 'needs_review' ? 'bg-orange-100' :
                    processingWorkItem.status === 'failed' ? 'bg-red-100' :
                    'bg-apex-100'
                  }`}>
                    {processingWorkItem.status === 'completed' ? (
                      <CheckCircleIcon className="h-6 w-6 text-green-600" />
                    ) : processingWorkItem.status === 'needs_review' ? (
                      <ExclamationTriangleIcon className="h-6 w-6 text-orange-600" />
                    ) : processingWorkItem.status === 'failed' ? (
                      <XMarkIcon className="h-6 w-6 text-red-600" />
                    ) : (
                      <CpuChipIcon className="h-6 w-6 text-apex-600" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Agent Processing</h3>
                    <p className="text-sm text-gray-500">{getDocumentName(processingWorkItem)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {isPolling && (
                    <div className="flex items-center gap-2 text-apex-600">
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Live</span>
                    </div>
                  )}
                  <button
                    onClick={handleCloseProcessingModal}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Processing Stage Timeline */}
              <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center justify-between">
                  {['extracting', 'validating', 'analyzing_risk', 'calculating_premium', 'making_decision'].map((stage, idx, arr) => {
                    const stageInfo = getStageInfo(stage);
                    const currentStageIdx = arr.indexOf(processingWorkItem.processing_stage || 'pending');
                    const isComplete = idx < currentStageIdx || processingWorkItem.status === 'completed' || processingWorkItem.status === 'needs_review';
                    const isCurrent = stage === processingWorkItem.processing_stage;
                    const isPending = idx > currentStageIdx && !isComplete;

                    return (
                      <React.Fragment key={stage}>
                        <div className={`flex flex-col items-center ${isCurrent ? 'scale-110' : ''}`}>
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            isComplete ? 'bg-green-100' :
                            isCurrent ? 'bg-apex-100 ring-2 ring-apex-500 ring-offset-2' :
                            'bg-gray-200'
                          }`}>
                            {isComplete ? (
                              <CheckCircleIcon className="h-5 w-5 text-green-600" />
                            ) : isCurrent ? (
                              <ArrowPathIcon className="h-5 w-5 text-apex-600 animate-spin" />
                            ) : (
                              <span className="text-gray-400 text-sm">{idx + 1}</span>
                            )}
                          </div>
                          <span className={`text-xs mt-1 text-center max-w-[80px] ${
                            isCurrent ? 'text-apex-600 font-medium' :
                            isComplete ? 'text-green-600' :
                            'text-gray-400'
                          }`}>
                            {stageInfo.label}
                          </span>
                        </div>
                        {idx < arr.length - 1 && (
                          <div className={`flex-1 h-0.5 mx-2 ${
                            idx < currentStageIdx || (processingWorkItem.status === 'completed' || processingWorkItem.status === 'needs_review')
                              ? 'bg-green-300' : 'bg-gray-200'
                          }`} />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

              {/* Main Content */}
              <div className="flex-1 flex overflow-hidden">
                {/* Processing Log */}
                <div className="flex-1 p-4 overflow-y-auto">
                  <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                    <SparklesIcon className="h-4 w-4 text-apex-500" />
                    Processing Log
                  </h4>
                  <div className="space-y-2">
                    {processingWorkItem.processing_log?.map((entry, idx) => {
                      const stageInfo = getStageInfo(entry.stage);
                      return (
                        <div
                          key={idx}
                          className="p-3 bg-gray-50 rounded-lg border-l-4 border-apex-300"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{stageInfo.icon}</span>
                            <span className="font-medium text-gray-900">{stageInfo.label}</span>
                            <span className="text-xs text-gray-400 ml-auto">
                              {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{entry.details.message}</p>
                          {entry.details.data && (
                            <details className="mt-2">
                              <summary className="text-xs text-apex-600 cursor-pointer hover:text-apex-700">
                                View details
                              </summary>
                              <pre className="mt-2 text-xs bg-gray-900 text-green-400 p-2 rounded overflow-x-auto">
                                {JSON.stringify(entry.details.data, null, 2)}
                              </pre>
                            </details>
                          )}
                        </div>
                      );
                    })}
                    {(!processingWorkItem.processing_log || processingWorkItem.processing_log.length === 0) && (
                      <div className="text-center py-8 text-gray-400">
                        <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto mb-2" />
                        <p>Waiting for processing to start...</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Results Panel */}
                <div className="w-80 border-l border-gray-200 p-4 overflow-y-auto bg-gray-50">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">
                    {processingWorkItem.status === 'needs_review' ? 'Requires Approval' :
                     processingWorkItem.status === 'completed' ? 'Final Decision' :
                     'Current Analysis'}
                  </h4>

                  {/* Current Stage Details */}
                  {processingWorkItem.current_stage_details && (
                    <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
                      <p className="text-sm font-medium text-gray-900 mb-2">
                        {processingWorkItem.current_stage_details.message || 'Processing...'}
                      </p>
                      {processingWorkItem.current_stage_details.data && (
                        <div className="space-y-2">
                          {Object.entries(processingWorkItem.current_stage_details.data).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-sm">
                              <span className="text-gray-500">{key.replace(/_/g, ' ')}:</span>
                              <span className="font-medium text-gray-900">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Final Result */}
                  {processingWorkItem.result && (
                    <div className="space-y-3">
                      {/* Decision/Recommendation */}
                      {(processingWorkItem.result.decision_result?.decision_text || processingWorkItem.result.recommendation) && (
                        <div className={`p-3 rounded-lg ${
                          processingWorkItem.result.decision_result?.decision === 'approve' ? 'bg-green-50 border border-green-200' :
                          processingWorkItem.result.decision_result?.decision === 'decline' ? 'bg-red-50 border border-red-200' :
                          'bg-orange-50 border border-orange-200'
                        }`}>
                          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Decision</p>
                          <p className={`text-lg font-bold ${
                            processingWorkItem.result.decision_result?.decision === 'approve' ? 'text-green-700' :
                            processingWorkItem.result.decision_result?.decision === 'decline' ? 'text-red-700' :
                            'text-orange-700'
                          }`}>
                            {processingWorkItem.result.decision_result?.decision_text || processingWorkItem.result.recommendation}
                          </p>
                        </div>
                      )}

                      {/* Premium */}
                      {(processingWorkItem.result.premium_result?.final_premium || processingWorkItem.result.final_premium) && (
                        <div className="p-3 bg-white rounded-lg border border-gray-200">
                          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Premium</p>
                          <p className="text-xl font-bold text-gray-900">
                            ${(processingWorkItem.result.premium_result?.final_premium || processingWorkItem.result.final_premium).toLocaleString()}
                          </p>
                          {processingWorkItem.result.premium_result?.rate_per_100 && (
                            <p className="text-xs text-gray-500 mt-1">
                              Rate: ${processingWorkItem.result.premium_result.rate_per_100}/100 TIV
                            </p>
                          )}
                        </div>
                      )}

                      {/* Risk Score */}
                      {(processingWorkItem.result.risk_result?.risk_score || processingWorkItem.result.risk_score) && (
                        <div className="p-3 bg-white rounded-lg border border-gray-200">
                          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Risk Score</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${
                                  (processingWorkItem.result.risk_result?.risk_score || processingWorkItem.result.risk_score) >= 75 ? 'bg-green-500' :
                                  (processingWorkItem.result.risk_result?.risk_score || processingWorkItem.result.risk_score) >= 60 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`}
                                style={{ width: `${processingWorkItem.result.risk_result?.risk_score || processingWorkItem.result.risk_score}%` }}
                              />
                            </div>
                            <span className="font-bold text-gray-900">
                              {processingWorkItem.result.risk_result?.risk_score || processingWorkItem.result.risk_score}
                            </span>
                          </div>
                          {processingWorkItem.result.risk_result?.risk_tier && (
                            <p className="text-xs text-gray-500 mt-1">
                              Tier: {processingWorkItem.result.risk_result.risk_tier}
                            </p>
                          )}
                        </div>
                      )}

                      {/* Loss History */}
                      {processingWorkItem.result.loss_result && (
                        <div className="p-3 bg-white rounded-lg border border-gray-200">
                          <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Loss History</p>
                          <p className="text-sm text-gray-900">
                            <span className="font-medium">{processingWorkItem.result.loss_result.total_claims}</span> claims
                          </p>
                          <p className="text-xs text-gray-500">
                            ${processingWorkItem.result.loss_result.total_paid?.toLocaleString()} paid
                            {processingWorkItem.result.loss_result.open_claims > 0 && (
                              <span className="text-orange-600 ml-1">
                                ({processingWorkItem.result.loss_result.open_claims} open)
                              </span>
                            )}
                          </p>
                        </div>
                      )}

                      {/* Approval Reason */}
                      {processingWorkItem.result.approval_reason && (
                        <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                          <p className="text-xs uppercase tracking-wide text-orange-600 mb-1">Approval Required</p>
                          <p className="text-sm text-orange-800">{processingWorkItem.result.approval_reason}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Approval Actions */}
                  {processingWorkItem.status === 'needs_review' && (
                    <div className="mt-4 space-y-2">
                      <Button
                        variant="primary"
                        className="w-full"
                        icon={<CheckCircleIcon className="h-4 w-4" />}
                        onClick={() => handleApproveWorkItem(processingWorkItem.work_item_id)}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="secondary"
                        className="w-full"
                        onClick={handleCloseProcessingModal}
                      >
                        Review Later
                      </Button>
                    </div>
                  )}

                  {processingWorkItem.status === 'completed' && (
                    <div className="mt-4">
                      <div className="p-3 bg-green-50 rounded-lg border border-green-200 text-center">
                        <CheckCircleIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
                        <p className="text-sm font-medium text-green-800">Processing Complete</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-4 border-t border-gray-200 flex justify-end gap-3">
                <Button variant="secondary" onClick={handleCloseProcessingModal}>
                  Close
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
