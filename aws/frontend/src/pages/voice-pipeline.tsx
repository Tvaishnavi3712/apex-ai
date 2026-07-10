/**
 * Voice Pipeline Page - Process insurance claims from recorded calls
 * Uses Small Factory chain for transcription, analysis, and claim extraction
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Button, Badge } from '@/components/common';
import {
  MicrophoneIcon,
  ArrowUpTrayIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ShieldExclamationIcon,
  UserCircleIcon,
  PhoneIcon,
  PlayIcon,
  XMarkIcon,
  ChevronRightIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface VoiceJob {
  job_id: string;
  filename: string;
  status: string;
  chain_id: string;
  current_factory?: string;
  progress?: Record<string, any>;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  transcript?: {
    full_text: string;
    segments: Array<{
      speaker: string;
      text: string;
      start_time: number;
      end_time: number;
    }>;
    speakers: string[];
    word_count: number;
    duration_seconds: number;
  };
  factory_results?: Record<string, any>;
  outputs?: Record<string, any>;
}

interface FactoryChain {
  id: string;
  name: string;
  description: string;
  factory_count: number;
}

export default function VoicePipeline() {
  const [activeTab, setActiveTab] = useState<'upload' | 'jobs'>('upload');
  const [jobs, setJobs] = useState<VoiceJob[]>([]);
  const [chains, setChains] = useState<FactoryChain[]>([]);
  const [selectedChain, setSelectedChain] = useState('insurance_claim_from_call');
  const [selectedJob, setSelectedJob] = useState<VoiceJob | null>(null);
  const [showJobDetail, setShowJobDetail] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch available chains
  useEffect(() => {
    const fetchChains = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/voice/chains`);
        if (res.ok) {
          const data = await res.json();
          setChains(data.chains || []);
        }
      } catch (err) {
        console.error('Failed to fetch chains:', err);
        // Set default chains for demo
        setChains([
          {
            id: 'insurance_claim_from_call',
            name: 'Insurance Claim from Recorded Call',
            description: 'Full pipeline: Audio → Transcript → Claim extraction → Analysis',
            factory_count: 12
          },
          {
            id: 'call_quality_analysis',
            name: 'Call Quality Analysis',
            description: 'QA scoring and compliance checking',
            factory_count: 6
          },
          {
            id: 'quick_sentiment',
            name: 'Quick Sentiment Analysis',
            description: 'Fast sentiment analysis for call triage',
            factory_count: 3
          }
        ]);
      }
    };
    fetchChains();
  }, []);

  // Handle file upload
  const handleFileUpload = async (file: File) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(
        `${API_BASE_URL}/voice/upload?chain_id=${selectedChain}&auto_process=true`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (res.ok) {
        const data = await res.json();
        // Add to jobs list
        setJobs(prev => [{
          job_id: data.job_id,
          filename: file.name,
          status: data.status,
          chain_id: selectedChain,
          created_at: new Date().toISOString(),
        }, ...prev]);
        setActiveTab('jobs');
      }
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
    }
  };

  // Handle demo processing
  const handleDemoProcess = async () => {
    setProcessing(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/voice/demo/process?chain_id=${selectedChain}&scenario=insurance_claim`,
        { method: 'POST' }
      );

      if (res.ok) {
        const data = await res.json();
        setJobs(prev => [{
          job_id: data.job_id,
          filename: 'demo_call.mp3',
          status: data.status,
          chain_id: selectedChain,
          created_at: new Date().toISOString(),
        }, ...prev]);
        setActiveTab('jobs');
        // Start polling for this job
        pollJobStatus(data.job_id);
      }
    } catch (err) {
      console.error('Demo process failed:', err);
    } finally {
      setProcessing(false);
    }
  };

  // Poll job status
  const pollJobStatus = useCallback(async (jobId: string) => {
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/voice/result/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          setJobs(prev => prev.map(j =>
            j.job_id === jobId ? { ...j, ...data } : j
          ));

          if (selectedJob?.job_id === jobId) {
            setSelectedJob({ ...selectedJob, ...data });
          }

          // Continue polling if not complete
          if (!['completed', 'failed', 'partial'].includes(data.status)) {
            setTimeout(poll, 1000);
          }
        }
      } catch (err) {
        console.error('Poll failed:', err);
      }
    };
    poll();
  }, [selectedJob]);

  // View job details
  const handleViewJob = (job: VoiceJob) => {
    setSelectedJob(job);
    setShowJobDetail(true);
    if (!['completed', 'failed', 'partial'].includes(job.status)) {
      pollJobStatus(job.job_id);
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'processing': return 'bg-blue-100 text-blue-700';
      case 'failed': return 'bg-red-100 text-red-700';
      case 'partial': return 'bg-orange-100 text-orange-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // Format time
  const formatTime = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  };

  return (
    <>
      <Head>
        <title>Voice Pipeline | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <MicrophoneIcon className="h-8 w-8 text-apex-500" />
              Voice Pipeline
            </h1>
            <p className="text-gray-500 mt-1">
              Process insurance claims from recorded calls using Small Factory chains
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={selectedChain}
              onChange={(e) => setSelectedChain(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-apex-500 focus:border-apex-500"
            >
              {chains.map(chain => (
                <option key={chain.id} value={chain.id}>{chain.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <ArrowUpTrayIcon className="h-5 w-5" />
            Upload & Process
          </button>
          <button
            onClick={() => setActiveTab('jobs')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'jobs'
                ? 'border-apex-500 text-apex-600 font-medium'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <DocumentTextIcon className="h-5 w-5" />
            Processing Jobs
            {jobs.filter(j => j.status === 'processing').length > 0 && (
              <Badge variant="primary">{jobs.filter(j => j.status === 'processing').length}</Badge>
            )}
          </button>
        </div>

        {/* Content */}
        {activeTab === 'upload' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload Section */}
            <Card>
              <CardHeader title="Upload Audio File" />
              <div className="p-6">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-apex-400 hover:bg-apex-50 transition-colors"
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="audio/mpeg,audio/wav,audio/x-m4a,audio/flac,audio/mp3"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(file);
                    }}
                  />
                  {uploading ? (
                    <div className="flex flex-col items-center">
                      <ArrowPathIcon className="h-12 w-12 text-apex-500 animate-spin mb-3" />
                      <p className="text-gray-600">Uploading...</p>
                    </div>
                  ) : (
                    <>
                      <ArrowUpTrayIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600 font-medium">Drop audio file here or click to upload</p>
                      <p className="text-sm text-gray-400 mt-2">Supports MP3, WAV, M4A, FLAC</p>
                    </>
                  )}
                </div>

                <div className="mt-6 flex items-center gap-4">
                  <div className="flex-1 h-px bg-gray-200" />
                  <span className="text-sm text-gray-500">or</span>
                  <div className="flex-1 h-px bg-gray-200" />
                </div>

                <Button
                  variant="primary"
                  className="w-full mt-6"
                  onClick={handleDemoProcess}
                  disabled={processing}
                  icon={processing ? <ArrowPathIcon className="h-5 w-5 animate-spin" /> : <PlayIcon className="h-5 w-5" />}
                >
                  {processing ? 'Starting Demo...' : 'Run Demo Call Processing'}
                </Button>
                <p className="text-xs text-gray-400 mt-2 text-center">
                  Process a sample insurance claim call without uploading
                </p>
              </div>
            </Card>

            {/* Selected Chain Info */}
            <Card>
              <CardHeader title="Processing Chain" />
              <div className="p-6">
                {chains.find(c => c.id === selectedChain) && (
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900 mb-2">
                      {chains.find(c => c.id === selectedChain)?.name}
                    </h3>
                    <p className="text-gray-500 mb-4">
                      {chains.find(c => c.id === selectedChain)?.description}
                    </p>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <SparklesIcon className="h-4 w-4 text-apex-500" />
                      <span>{chains.find(c => c.id === selectedChain)?.factory_count} factories in chain</span>
                    </div>

                    {selectedChain === 'insurance_claim_from_call' && (
                      <div className="mt-6">
                        <h4 className="font-medium text-gray-700 mb-3">Processing Steps:</h4>
                        <div className="space-y-2">
                          {[
                            { name: 'Transcribe', icon: MicrophoneIcon, desc: 'Convert audio to text with speaker labels' },
                            { name: 'Diarize', icon: UserCircleIcon, desc: 'Label speakers (Agent, Customer)' },
                            { name: 'Intent', icon: ChatBubbleLeftRightIcon, desc: 'Classify call intent' },
                            { name: 'Sentiment', icon: ChartBarIcon, desc: 'Analyze sentiment timeline' },
                            { name: 'Entities', icon: DocumentTextIcon, desc: 'Extract names, dates, amounts' },
                            { name: 'Claim', icon: DocumentTextIcon, desc: 'Extract claim details' },
                            { name: 'Compliance', icon: ShieldExclamationIcon, desc: 'Audit compliance' },
                            { name: 'Fraud', icon: ExclamationTriangleIcon, desc: 'Detect fraud indicators' },
                            { name: 'Decision', icon: CheckCircleIcon, desc: 'Auto-route claim' },
                          ].map((step, idx) => (
                            <div key={idx} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                              <step.icon className="h-5 w-5 text-apex-500" />
                              <div>
                                <p className="font-medium text-sm text-gray-900">{step.name}</p>
                                <p className="text-xs text-gray-500">{step.desc}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          </div>
        ) : (
          <div>
            {/* Jobs List */}
            <Card>
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Processing Jobs</h3>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<ArrowPathIcon className="h-4 w-4" />}
                  onClick={() => {
                    jobs.forEach(j => {
                      if (!['completed', 'failed', 'partial'].includes(j.status)) {
                        pollJobStatus(j.job_id);
                      }
                    });
                  }}
                >
                  Refresh
                </Button>
              </div>

              {jobs.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <PhoneIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>No processing jobs yet</p>
                  <p className="text-sm mt-1">Upload an audio file or run a demo to get started</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {jobs.map(job => (
                    <div
                      key={job.job_id}
                      className="p-4 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
                      onClick={() => handleViewJob(job)}
                    >
                      <div className="flex items-center gap-4">
                        {job.status === 'processing' ? (
                          <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />
                        ) : job.status === 'completed' ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" />
                        ) : job.status === 'failed' ? (
                          <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
                        ) : (
                          <ClockIcon className="h-5 w-5 text-gray-400" />
                        )}
                        <div>
                          <p className="font-medium text-gray-900">{job.filename}</p>
                          <p className="text-sm text-gray-500">
                            {job.chain_id.replace(/_/g, ' ')} • {formatTime(job.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {job.current_factory && job.status === 'processing' && (
                          <span className="text-sm text-blue-600">
                            Processing: {job.current_factory}
                          </span>
                        )}
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                        <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Job Detail Modal */}
        {showJobDetail && selectedJob && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    selectedJob.status === 'completed' ? 'bg-green-100' :
                    selectedJob.status === 'processing' ? 'bg-blue-100' :
                    selectedJob.status === 'failed' ? 'bg-red-100' : 'bg-gray-100'
                  }`}>
                    {selectedJob.status === 'completed' ? (
                      <CheckCircleIcon className="h-6 w-6 text-green-600" />
                    ) : selectedJob.status === 'processing' ? (
                      <ArrowPathIcon className="h-6 w-6 text-blue-600 animate-spin" />
                    ) : (
                      <MicrophoneIcon className="h-6 w-6 text-gray-600" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{selectedJob.filename}</h3>
                    <p className="text-sm text-gray-500">{selectedJob.job_id}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowJobDetail(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-auto p-6">
                {selectedJob.status === 'processing' ? (
                  <div className="text-center py-12">
                    <ArrowPathIcon className="h-16 w-16 text-apex-500 animate-spin mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Call</h3>
                    <p className="text-gray-500">
                      {selectedJob.current_factory
                        ? `Running: ${selectedJob.current_factory.replace(/_/g, ' ')}`
                        : 'Initializing pipeline...'}
                    </p>
                  </div>
                ) : selectedJob.status === 'completed' && selectedJob.outputs ? (
                  <div className="space-y-6">
                    {/* Summary */}
                    {selectedJob.outputs.summary && (
                      <div className="bg-apex-50 border border-apex-200 rounded-xl p-4">
                        <h4 className="font-semibold text-apex-800 mb-2">Call Summary</h4>
                        <p className="text-gray-700">{selectedJob.outputs.summary.summary}</p>
                        {selectedJob.outputs.summary.action_items?.length > 0 && (
                          <div className="mt-3">
                            <p className="font-medium text-sm text-gray-700 mb-1">Action Items:</p>
                            <ul className="list-disc list-inside text-sm text-gray-600">
                              {selectedJob.outputs.summary.action_items.map((item: string, idx: number) => (
                                <li key={idx}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {/* Claim Type */}
                      {selectedJob.outputs.claim && (
                        <div className="bg-white border border-gray-200 rounded-xl p-4">
                          <p className="text-xs text-gray-500 uppercase">Claim Type</p>
                          <p className="text-lg font-bold text-gray-900">
                            {selectedJob.outputs.claim.claim_type?.replace(/_/g, ' ').toUpperCase()}
                          </p>
                        </div>
                      )}

                      {/* Sentiment */}
                      {selectedJob.outputs.sentiment && (
                        <div className="bg-white border border-gray-200 rounded-xl p-4">
                          <p className="text-xs text-gray-500 uppercase">Sentiment</p>
                          <p className={`text-lg font-bold ${
                            selectedJob.outputs.sentiment.overall_sentiment === 'positive' ? 'text-green-600' :
                            selectedJob.outputs.sentiment.overall_sentiment === 'negative' ? 'text-red-600' :
                            'text-gray-600'
                          }`}>
                            {selectedJob.outputs.sentiment.overall_sentiment?.toUpperCase()}
                          </p>
                          <p className="text-xs text-gray-400">{selectedJob.outputs.sentiment.sentiment_arc}</p>
                        </div>
                      )}

                      {/* Fraud Score */}
                      {selectedJob.outputs.fraud && (
                        <div className="bg-white border border-gray-200 rounded-xl p-4">
                          <p className="text-xs text-gray-500 uppercase">Fraud Risk</p>
                          <p className={`text-lg font-bold ${
                            selectedJob.outputs.fraud.risk_level === 'low' ? 'text-green-600' :
                            selectedJob.outputs.fraud.risk_level === 'medium' ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {selectedJob.outputs.fraud.fraud_score}%
                          </p>
                          <p className="text-xs text-gray-400">{selectedJob.outputs.fraud.risk_level} risk</p>
                        </div>
                      )}

                      {/* Decision */}
                      {selectedJob.outputs.decision && (
                        <div className={`rounded-xl p-4 ${
                          selectedJob.outputs.decision.decision === 'approve' ? 'bg-green-50 border border-green-200' :
                          selectedJob.outputs.decision.decision === 'deny' ? 'bg-red-50 border border-red-200' :
                          'bg-orange-50 border border-orange-200'
                        }`}>
                          <p className="text-xs text-gray-500 uppercase">Decision</p>
                          <p className={`text-lg font-bold ${
                            selectedJob.outputs.decision.decision === 'approve' ? 'text-green-700' :
                            selectedJob.outputs.decision.decision === 'deny' ? 'text-red-700' :
                            'text-orange-700'
                          }`}>
                            {selectedJob.outputs.decision.decision?.toUpperCase()}
                          </p>
                          <p className="text-xs text-gray-400">{selectedJob.outputs.decision.routing}</p>
                        </div>
                      )}
                    </div>

                    {/* Transcript */}
                    {selectedJob.outputs.transcribe && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <DocumentTextIcon className="h-5 w-5 text-apex-500" />
                          Transcript
                        </h4>
                        <div className="bg-gray-50 rounded-xl p-4 max-h-64 overflow-y-auto">
                          {selectedJob.outputs.diarize?.segments ? (
                            <div className="space-y-3">
                              {selectedJob.outputs.diarize.segments.slice(0, 20).map((seg: any, idx: number) => (
                                <div key={idx} className="flex gap-3">
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    seg.speaker?.includes('Agent') ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                                  }`}>
                                    {seg.speaker}
                                  </span>
                                  <p className="text-gray-700 text-sm flex-1">{seg.text}</p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-700 whitespace-pre-wrap">
                              {selectedJob.outputs.transcribe.full_text?.substring(0, 1000)}
                              {selectedJob.outputs.transcribe.full_text?.length > 1000 && '...'}
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Compliance */}
                    {selectedJob.outputs.compliance && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <ShieldExclamationIcon className="h-5 w-5 text-apex-500" />
                          Compliance Audit
                        </h4>
                        <div className={`rounded-xl p-4 ${
                          selectedJob.outputs.compliance.passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">
                              Score: {selectedJob.outputs.compliance.overall_score}/100
                            </span>
                            <span className={`px-2 py-1 rounded text-sm font-medium ${
                              selectedJob.outputs.compliance.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                            }`}>
                              {selectedJob.outputs.compliance.passed ? 'PASSED' : 'FAILED'}
                            </span>
                          </div>
                          {selectedJob.outputs.compliance.violations?.length > 0 && (
                            <div className="mt-2">
                              <p className="text-sm font-medium text-red-700 mb-1">Violations:</p>
                              <ul className="list-disc list-inside text-sm text-red-600">
                                {selectedJob.outputs.compliance.violations.map((v: any, idx: number) => (
                                  <li key={idx}>{v.description}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Coaching Tips */}
                    {selectedJob.outputs.coaching?.tips?.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <SparklesIcon className="h-5 w-5 text-apex-500" />
                          Coaching Recommendations
                        </h4>
                        <div className="space-y-2">
                          {selectedJob.outputs.coaching.tips.map((tip: any, idx: number) => (
                            <div key={idx} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                  tip.priority === 'high' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                                }`}>
                                  {tip.priority}
                                </span>
                                <span className="font-medium text-sm">{tip.area}</span>
                              </div>
                              <p className="text-sm text-gray-700">{tip.tip}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <ExclamationTriangleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Processing Failed</h3>
                    <p className="text-gray-500">An error occurred while processing this call</p>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-gray-200 flex justify-end">
                <Button variant="secondary" onClick={() => setShowJobDetail(false)}>
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
