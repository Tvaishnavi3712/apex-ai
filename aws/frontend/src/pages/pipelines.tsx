/**
 * Pipelines Page - Unified view of all automation workflows
 *
 * Shows factory chains, playbooks, and processing pipelines across industries
 */

import React, { useState, useMemo } from 'react';
import { Layout } from '@/components/Layout/Layout';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import {
  ArrowPathIcon,
  PlayIcon,
  StopIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  SparklesIcon,
  CpuChipIcon,
  DocumentTextIcon,
  BanknotesIcon,
  HeartIcon,
  UserGroupIcon,
  PhoneIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

// Pipeline types
interface PipelineFactory {
  id: string;
  name: string;
  description: string;
  aiEnhanced: boolean;
  status: 'idle' | 'running' | 'completed' | 'failed';
}

interface Pipeline {
  id: string;
  name: string;
  description: string;
  industry: string;
  category: string;
  status: 'active' | 'inactive' | 'draft';
  factories: PipelineFactory[];
  metrics: {
    executions: number;
    avgDuration: string;
    successRate: number;
    lastRun?: string;
  };
  aiEnhanced: boolean;
}

// Industry icons mapping
const industryIcons: Record<string, React.ElementType> = {
  contact_center: PhoneIcon,
  financial_services: BanknotesIcon,
  healthcare_payers: ShieldCheckIcon,
  healthcare_providers: HeartIcon,
  hr: UserGroupIcon,
  insurance_underwriting: DocumentTextIcon,
  sales_ai: ChartBarIcon,
};

// Mock pipeline data
const mockPipelines: Pipeline[] = [
  {
    id: 'call_analytics',
    name: 'Contact Center Analytics',
    description: 'End-to-end call analysis with transcription, sentiment, and quality scoring',
    industry: 'contact_center',
    category: 'analytics',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'transcribe_audio', name: 'Transcribe Audio', description: 'Convert audio to text', aiEnhanced: false, status: 'completed' },
      { id: 'diarize_speakers', name: 'Diarize Speakers', description: 'Identify speakers', aiEnhanced: false, status: 'completed' },
      { id: 'intent_classify', name: 'Intent Classify', description: 'Classify call intent', aiEnhanced: true, status: 'completed' },
      { id: 'sentiment_timeline', name: 'Sentiment Timeline', description: 'Track sentiment over time', aiEnhanced: true, status: 'completed' },
      { id: 'entity_extract', name: 'Entity Extract', description: 'Extract named entities', aiEnhanced: true, status: 'completed' },
      { id: 'compliance_audit', name: 'Compliance Audit', description: 'Check compliance violations', aiEnhanced: false, status: 'completed' },
      { id: 'summary_generate', name: 'Summary Generate', description: 'Generate call summary', aiEnhanced: true, status: 'running' },
      { id: 'quality_score', name: 'Quality Score', description: 'Score call quality', aiEnhanced: true, status: 'idle' },
      { id: 'coaching_recommend', name: 'Coaching Tips', description: 'AI coaching recommendations', aiEnhanced: true, status: 'idle' },
    ],
    metrics: {
      executions: 12450,
      avgDuration: '8.2s',
      successRate: 98.5,
      lastRun: '2 minutes ago',
    },
  },
  {
    id: 'invoice_processing',
    name: 'Invoice Processing',
    description: 'Automated email-to-ERP invoice processing with vendor matching',
    industry: 'financial_services',
    category: 'processing',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'email_parse', name: 'Email Parse', description: 'Parse email and attachments', aiEnhanced: false, status: 'completed' },
      { id: 'document_classify', name: 'Document Classify', description: 'Classify document type', aiEnhanced: true, status: 'completed' },
      { id: 'invoice_extract', name: 'Invoice Extract', description: 'Extract invoice fields', aiEnhanced: true, status: 'completed' },
      { id: 'vendor_match', name: 'Vendor Match', description: 'Match to vendor database', aiEnhanced: false, status: 'running' },
      { id: 'po_reconcile', name: 'PO Reconcile', description: 'Reconcile with PO', aiEnhanced: false, status: 'idle' },
      { id: 'approval_route', name: 'Approval Route', description: 'Route for approval', aiEnhanced: false, status: 'idle' },
      { id: 'erp_post', name: 'ERP Post', description: 'Post to ERP system', aiEnhanced: false, status: 'idle' },
    ],
    metrics: {
      executions: 3240,
      avgDuration: '4.5s',
      successRate: 96.2,
      lastRun: '15 minutes ago',
    },
  },
  {
    id: 'claims_processing',
    name: 'Claims Processing',
    description: 'Healthcare claims adjudication with fraud detection and payment calculation',
    industry: 'healthcare_payers',
    category: 'claims',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'eligibility_verify', name: 'Eligibility Verify', description: 'Verify member eligibility', aiEnhanced: false, status: 'completed' },
      { id: 'claims_adjudication', name: 'Claims Adjudication', description: 'Adjudicate claim', aiEnhanced: false, status: 'completed' },
      { id: 'medical_necessity_check', name: 'Medical Necessity', description: 'Check medical necessity', aiEnhanced: true, status: 'running' },
      { id: 'fraud_detection', name: 'Fraud Detection', description: 'Detect fraud indicators', aiEnhanced: true, status: 'idle' },
      { id: 'payment_calculate', name: 'Payment Calculate', description: 'Calculate payment', aiEnhanced: false, status: 'idle' },
    ],
    metrics: {
      executions: 8920,
      avgDuration: '3.2s',
      successRate: 99.1,
      lastRun: '5 minutes ago',
    },
  },
  {
    id: 'patient_record',
    name: 'Patient Record Processing',
    description: 'Clinical documentation with AI-enhanced extraction and coding',
    industry: 'healthcare_providers',
    category: 'clinical',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'document_classify', name: 'Document Classify', description: 'Classify clinical document', aiEnhanced: true, status: 'completed' },
      { id: 'patient_identify', name: 'Patient Identify', description: 'Identify patient', aiEnhanced: false, status: 'completed' },
      { id: 'clinical_extract', name: 'Clinical Extract', description: 'Extract clinical data', aiEnhanced: true, status: 'completed' },
      { id: 'code_suggest', name: 'Code Suggest', description: 'Suggest ICD/CPT codes', aiEnhanced: true, status: 'running' },
      { id: 'quality_audit', name: 'Quality Audit', description: 'Audit documentation', aiEnhanced: false, status: 'idle' },
      { id: 'ehr_format', name: 'EHR Format', description: 'Format for EHR', aiEnhanced: false, status: 'idle' },
    ],
    metrics: {
      executions: 5680,
      avgDuration: '6.8s',
      successRate: 97.8,
      lastRun: '8 minutes ago',
    },
  },
  {
    id: 'employee_onboarding',
    name: 'Employee Onboarding',
    description: 'HR onboarding automation from document verification to system provisioning',
    industry: 'hr',
    category: 'onboarding',
    status: 'active',
    aiEnhanced: false,
    factories: [
      { id: 'document_classify', name: 'Document Classify', description: 'Classify HR documents', aiEnhanced: true, status: 'completed' },
      { id: 'identity_verify', name: 'Identity Verify', description: 'Verify identity documents', aiEnhanced: false, status: 'completed' },
      { id: 'i9_validate', name: 'I-9 Validate', description: 'Validate I-9 form', aiEnhanced: false, status: 'completed' },
      { id: 'background_check', name: 'Background Check', description: 'Initiate background check', aiEnhanced: false, status: 'running' },
      { id: 'benefits_enroll', name: 'Benefits Enroll', description: 'Process benefits enrollment', aiEnhanced: false, status: 'idle' },
      { id: 'provisioning_trigger', name: 'Provisioning', description: 'Trigger system provisioning', aiEnhanced: false, status: 'idle' },
    ],
    metrics: {
      executions: 890,
      avgDuration: '12.5s',
      successRate: 95.6,
      lastRun: '1 hour ago',
    },
  },
  {
    id: 'insurance_underwriting',
    name: 'Insurance Underwriting',
    description: 'Automated claim extraction, fraud analysis, and underwriting decisions',
    industry: 'insurance_underwriting',
    category: 'underwriting',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'claim_extract', name: 'Claim Extract', description: 'Extract claim data', aiEnhanced: true, status: 'completed' },
      { id: 'fraud_indicators', name: 'Fraud Indicators', description: 'Detect fraud patterns', aiEnhanced: true, status: 'completed' },
      { id: 'priority_calculate', name: 'Priority Calculate', description: 'Calculate priority score', aiEnhanced: false, status: 'running' },
      { id: 'auto_decision', name: 'Auto Decision', description: 'Automated decision', aiEnhanced: true, status: 'idle' },
    ],
    metrics: {
      executions: 4560,
      avgDuration: '5.1s',
      successRate: 98.9,
      lastRun: '10 minutes ago',
    },
  },
  {
    id: 'sales_interaction_agent',
    name: 'Sales Interaction Agent',
    description: 'AI-powered sales conversation intelligence with emotion analysis, buying signals, and coaching',
    industry: 'sales_ai',
    category: 'sales_intelligence',
    status: 'active',
    aiEnhanced: true,
    factories: [
      { id: 'transcribe_audio', name: 'Transcribe Audio', description: 'Convert sales call to text', aiEnhanced: false, status: 'completed' },
      { id: 'diarize_speakers', name: 'Diarize Speakers', description: 'Identify rep vs prospect', aiEnhanced: false, status: 'completed' },
      { id: 'emotion_analyze', name: 'Emotion Analyze', description: 'Analyze emotional cues', aiEnhanced: true, status: 'completed' },
      { id: 'buying_signals', name: 'Buying Signals', description: 'Detect purchase intent', aiEnhanced: true, status: 'completed' },
      { id: 'objection_detect', name: 'Objection Detect', description: 'Identify objections', aiEnhanced: true, status: 'running' },
      { id: 'competitor_mentions', name: 'Competitor Mentions', description: 'Track competitor references', aiEnhanced: true, status: 'idle' },
      { id: 'deal_intelligence', name: 'Deal Intelligence', description: 'Calculate win probability', aiEnhanced: true, status: 'idle' },
      { id: 'sales_coaching', name: 'Sales Coaching', description: 'Generate coaching tips', aiEnhanced: true, status: 'idle' },
      { id: 'sales_summary', name: 'Sales Summary', description: 'Create call summary & CRM updates', aiEnhanced: true, status: 'idle' },
    ],
    metrics: {
      executions: 7820,
      avgDuration: '12.4s',
      successRate: 97.2,
      lastRun: '3 minutes ago',
    },
  },
];

// Status badge component
const StatusBadge: React.FC<{ status: Pipeline['status'] | PipelineFactory['status'] }> = ({ status }) => {
  const variants: Record<string, { variant: 'success' | 'warning' | 'danger' | 'default'; icon: React.ElementType }> = {
    active: { variant: 'success', icon: CheckCircleIcon },
    completed: { variant: 'success', icon: CheckCircleIcon },
    running: { variant: 'warning', icon: ArrowPathIcon },
    inactive: { variant: 'default', icon: StopIcon },
    idle: { variant: 'default', icon: ClockIcon },
    draft: { variant: 'default', icon: DocumentTextIcon },
    failed: { variant: 'danger', icon: XCircleIcon },
  };

  const { variant, icon: Icon } = variants[status] || variants.idle;

  return (
    <Badge variant={variant} className="flex items-center gap-1">
      <Icon className={clsx('h-3.5 w-3.5', status === 'running' && 'animate-spin')} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
};

// Pipeline detail card component
const PipelineCard: React.FC<{
  pipeline: Pipeline;
  onRun: (id: string) => void;
  onStop: (id: string) => void;
  onView: (id: string) => void;
}> = ({ pipeline, onRun, onStop, onView }) => {
  const [expanded, setExpanded] = useState(false);
  const Icon = industryIcons[pipeline.industry] || CpuChipIcon;

  const runningFactories = pipeline.factories.filter(f => f.status === 'running').length;
  const completedFactories = pipeline.factories.filter(f => f.status === 'completed').length;
  const aiFactories = pipeline.factories.filter(f => f.aiEnhanced).length;

  return (
    <Card className="overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className={clsx(
              'p-3 rounded-xl',
              pipeline.aiEnhanced ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'
            )}>
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-gray-900">{pipeline.name}</h3>
                {pipeline.aiEnhanced && (
                  <Badge variant="default" className="flex items-center gap-1 bg-purple-100 text-purple-700">
                    <SparklesIcon className="h-3.5 w-3.5" />
                    AI Enhanced
                  </Badge>
                )}
                <StatusBadge status={pipeline.status} />
              </div>
              <p className="text-sm text-gray-500 mt-1">{pipeline.description}</p>
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <CpuChipIcon className="h-4 w-4" />
                  {pipeline.factories.length} factories
                </span>
                {aiFactories > 0 && (
                  <span className="flex items-center gap-1 text-purple-600">
                    <SparklesIcon className="h-4 w-4" />
                    {aiFactories} AI-powered
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <ClockIcon className="h-4 w-4" />
                  {pipeline.metrics.avgDuration}
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {runningFactories > 0 ? (
              <Button variant="secondary" size="sm" onClick={() => onStop(pipeline.id)}>
                <StopIcon className="h-4 w-4 mr-1" />
                Stop
              </Button>
            ) : (
              <Button variant="primary" size="sm" onClick={() => onRun(pipeline.id)}>
                <PlayIcon className="h-4 w-4 mr-1" />
                Run
              </Button>
            )}
            <Button variant="secondary" size="sm" onClick={() => setExpanded(!expanded)}>
              <ChevronRightIcon className={clsx('h-4 w-4 transition-transform', expanded && 'rotate-90')} />
            </Button>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-4 gap-4 mt-6 pt-4 border-t border-gray-100">
          <div>
            <div className="text-2xl font-bold text-gray-900">{pipeline.metrics.executions.toLocaleString()}</div>
            <div className="text-sm text-gray-500">Executions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{pipeline.metrics.avgDuration}</div>
            <div className="text-sm text-gray-500">Avg Duration</div>
          </div>
          <div>
            <div className={clsx(
              'text-2xl font-bold',
              pipeline.metrics.successRate >= 98 ? 'text-green-600' :
              pipeline.metrics.successRate >= 95 ? 'text-yellow-600' : 'text-red-600'
            )}>
              {pipeline.metrics.successRate}%
            </div>
            <div className="text-sm text-gray-500">Success Rate</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">{pipeline.metrics.lastRun}</div>
            <div className="text-sm text-gray-500">Last Run</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-500">Pipeline Progress</span>
            <span className="font-medium">{completedFactories}/{pipeline.factories.length} factories</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-apex-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${(completedFactories / pipeline.factories.length) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Expanded Factory List */}
      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50 p-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-4">Factory Chain</h4>
          <div className="space-y-2">
            {pipeline.factories.map((factory, index) => (
              <div
                key={factory.id}
                className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
              >
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-gray-100 text-gray-500 text-xs font-medium flex items-center justify-center">
                    {index + 1}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{factory.name}</span>
                      {factory.aiEnhanced && (
                        <SparklesIcon className="h-4 w-4 text-purple-500" />
                      )}
                    </div>
                    <span className="text-sm text-gray-500">{factory.description}</span>
                  </div>
                </div>
                <StatusBadge status={factory.status} />
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
};

// Main Pipelines page
const PipelinesPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState<string>('all');
  const [showAiOnly, setShowAiOnly] = useState(false);

  // Get unique industries
  const industries = useMemo(() => {
    const unique = [...new Set(mockPipelines.map(p => p.industry))];
    return ['all', ...unique];
  }, []);

  // Filter pipelines
  const filteredPipelines = useMemo(() => {
    return mockPipelines.filter(pipeline => {
      const matchesSearch = pipeline.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pipeline.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesIndustry = selectedIndustry === 'all' || pipeline.industry === selectedIndustry;
      const matchesAi = !showAiOnly || pipeline.aiEnhanced;
      return matchesSearch && matchesIndustry && matchesAi;
    });
  }, [searchQuery, selectedIndustry, showAiOnly]);

  // Summary stats
  const stats = useMemo(() => {
    const totalExecutions = mockPipelines.reduce((sum, p) => sum + p.metrics.executions, 0);
    const avgSuccessRate = mockPipelines.reduce((sum, p) => sum + p.metrics.successRate, 0) / mockPipelines.length;
    const activePipelines = mockPipelines.filter(p => p.status === 'active').length;
    const aiPipelines = mockPipelines.filter(p => p.aiEnhanced).length;
    return { totalExecutions, avgSuccessRate, activePipelines, aiPipelines };
  }, []);

  const handleRun = (id: string) => {
    console.log('Running pipeline:', id);
  };

  const handleStop = (id: string) => {
    console.log('Stopping pipeline:', id);
  };

  const handleView = (id: string) => {
    console.log('Viewing pipeline:', id);
  };

  return (
    <Layout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Pipelines</h1>
              <p className="text-gray-500 mt-1">Manage and monitor automation workflows</p>
            </div>
            <Button variant="primary" size="lg">
              <ArrowPathIcon className="h-5 w-5 mr-2" />
              Create Pipeline
            </Button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-blue-100 text-blue-600">
                <ArrowPathIcon className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.activePipelines}</div>
                <div className="text-sm text-gray-500">Active Pipelines</div>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-purple-100 text-purple-600">
                <SparklesIcon className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.aiPipelines}</div>
                <div className="text-sm text-gray-500">AI-Enhanced</div>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-green-100 text-green-600">
                <ChartBarIcon className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.totalExecutions.toLocaleString()}</div>
                <div className="text-sm text-gray-500">Total Executions</div>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-yellow-100 text-yellow-600">
                <CheckCircleIcon className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.avgSuccessRate.toFixed(1)}%</div>
                <div className="text-sm text-gray-500">Avg Success Rate</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search pipelines..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent"
          >
            {industries.map(industry => (
              <option key={industry} value={industry}>
                {industry === 'all' ? 'All Industries' : industry.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
          <Button
            variant={showAiOnly ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setShowAiOnly(!showAiOnly)}
          >
            <SparklesIcon className="h-4 w-4 mr-1" />
            AI Only
          </Button>
        </div>

        {/* Pipeline List */}
        <div className="space-y-6">
          {filteredPipelines.map(pipeline => (
            <PipelineCard
              key={pipeline.id}
              pipeline={pipeline}
              onRun={handleRun}
              onStop={handleStop}
              onView={handleView}
            />
          ))}
        </div>

        {filteredPipelines.length === 0 && (
          <Card className="p-12 text-center">
            <FunnelIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No pipelines found</h3>
            <p className="text-gray-500">Try adjusting your filters or search query</p>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default PipelinesPage;
