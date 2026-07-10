/**
 * Testing Sandbox Page - Test agents and playbooks
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Button, Badge } from '@/components/common';
import {
  PlayIcon,
  DocumentArrowUpIcon,
  CpuChipIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  BuildingOffice2Icon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function TestingSandbox() {
  const [selectedPlaybook, setSelectedPlaybook] = useState('');
  const [testFile, setTestFile] = useState<File | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [playbooks, setPlaybooks] = useState<any[]>([]);

  // Fetch all playbooks from API
  useEffect(() => {
    const fetchPlaybooks = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/playbooks/`);
        if (response.ok) {
          const data = await response.json();
          // Sort: insurance_underwriting first, then alphabetically
          const sortedPlaybooks = data.sort((a: any, b: any) => {
            if (a.industry === 'insurance_underwriting' && b.industry !== 'insurance_underwriting') return -1;
            if (b.industry === 'insurance_underwriting' && a.industry !== 'insurance_underwriting') return 1;
            return a.name.localeCompare(b.name);
          });

          setPlaybooks(sortedPlaybooks.map((p: any) => ({
            id: p.playbook_id,
            name: p.name,
            industry: p.industry,
            intent: p.intent
          })));
        } else {
          setPlaybooks(defaultPlaybooks);
        }
      } catch (error) {
        console.log('Using default playbooks');
        setPlaybooks(defaultPlaybooks);
      }
    };
    fetchPlaybooks();
  }, []);

  // Default playbooks (fallback)
  const defaultPlaybooks = [
    { id: 'ins-cre-playbook-001', name: 'CRE Underwriting Workflow', industry: 'insurance_underwriting', intent: 'Process commercial real estate insurance submissions' },
    { id: 'underwriting_workflow', name: 'Personal Lines Underwriting', industry: 'insurance_underwriting', intent: 'Process personal insurance applications' },
    { id: 'invoice_processing', name: 'Invoice Processing', industry: 'financial_services', intent: 'Extract and validate invoice data' },
    { id: 'claims_processing', name: 'Claims Processing', industry: 'healthcare_payers', intent: 'Process and adjudicate claims' },
  ];

  // Get mock results based on selected playbook
  const getMockResults = (playbookId: string) => {
    if (playbookId.includes('cre') || playbookId.includes('underwriting')) {
      return {
        status: 'success',
        duration: '4.2s',
        steps: [
          { name: 'Document Upload', status: 'success', duration: '0.3s' },
          { name: 'BDA Extraction', status: 'success', duration: '2.1s', output: { fields_extracted: 25, confidence: 0.94 } },
          { name: 'Risk Score Calculation', status: 'success', duration: '0.8s' },
          { name: 'Premium Calculation', status: 'success', duration: '0.4s' },
          { name: 'Underwriting Decision', status: 'success', duration: '0.6s' },
        ],
        extractedData: {
          submission_id: 'CRE-2024-001847',
          property_name: 'Parkview Office Tower',
          property_type: 'Class A Office',
          total_insurable_value: '$27,000,000',
          occupancy_rate: '94%',
          risk_score: 42,
          decision: 'AUTO-APPROVE',
          premium_indication: '$48,500',
          conditions: ['Standard fire protection maintenance', 'Annual roof inspection required']
        },
      };
    }
    return {
      status: 'success',
      duration: '2.3s',
      steps: [
        { name: 'Document Upload', status: 'success', duration: '0.2s' },
        { name: 'BDA Extraction', status: 'success', duration: '1.5s', output: { fields_extracted: 24, confidence: 0.95 } },
        { name: 'Validation', status: 'success', duration: '0.1s' },
        { name: 'Business Logic', status: 'success', duration: '0.3s' },
        { name: 'Output Generation', status: 'success', duration: '0.2s' },
      ],
      extractedData: {
        invoice_number: 'INV-2024-0892',
        vendor_name: 'Acme Corp',
        total_amount: '$12,450.00',
        due_date: '2024-02-15',
      },
    };
  };

  const handleRunTest = () => {
    setIsRunning(true);
    // Simulate test run with playbook-specific results
    const duration = selectedPlaybook.includes('cre') || selectedPlaybook.includes('underwriting') ? 4000 : 2000;
    setTimeout(() => {
      setTestResults(getMockResults(selectedPlaybook));
      setIsRunning(false);
    }, duration);
  };

  return (
    <>
      <Head>
        <title>Testing Sandbox | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Testing Sandbox</h1>
            <p className="text-gray-500 mt-1">Test your playbooks with sample documents</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8">
          {/* Left Panel - Configuration */}
          <div className="space-y-6">
            {/* Playbook Selection */}
            <Card>
              <CardHeader
                title="1. Select Playbook"
                subtitle={`${playbooks.length} playbooks available`}
              />
              <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
                {playbooks.map((playbook) => (
                  <button
                    key={playbook.id}
                    onClick={() => setSelectedPlaybook(playbook.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                      selectedPlaybook === playbook.id
                        ? 'border-apex-500 bg-apex-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {playbook.industry === 'insurance_underwriting' ? (
                      <ShieldCheckIcon className={`h-5 w-5 flex-shrink-0 ${
                        selectedPlaybook === playbook.id ? 'text-apex-600' : 'text-blue-500'
                      }`} />
                    ) : (
                      <DocumentTextIcon className={`h-5 w-5 flex-shrink-0 ${
                        selectedPlaybook === playbook.id ? 'text-apex-600' : 'text-gray-400'
                      }`} />
                    )}
                    <div className="flex-1 text-left min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`truncate ${selectedPlaybook === playbook.id ? 'text-apex-600 font-medium' : 'text-gray-700'}`}>
                          {playbook.name}
                        </span>
                      </div>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        playbook.industry === 'insurance_underwriting'
                          ? 'bg-blue-100 text-blue-700'
                          : playbook.industry === 'financial_services'
                          ? 'bg-green-100 text-green-700'
                          : playbook.industry === 'healthcare_payers'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {playbook.industry?.replace(/_/g, ' ') || 'general'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </Card>

            {/* File Upload */}
            <Card>
              <CardHeader title="2. Upload Test Document" />
              <div
                className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-apex-400 transition-colors cursor-pointer"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => setTestFile(e.target.files?.[0] || null)}
                />
                <DocumentArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                {testFile ? (
                  <div>
                    <p className="font-medium text-gray-900">{testFile.name}</p>
                    <p className="text-sm text-gray-500">{(testFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium text-gray-900">Drop a file or click to upload</p>
                    <p className="text-sm text-gray-500">PDF, PNG, JPG up to 10MB</p>
                  </div>
                )}
              </div>
            </Card>

            {/* Run Button */}
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              icon={isRunning ? <ArrowPathIcon className="h-5 w-5 animate-spin" /> : <PlayIcon className="h-5 w-5" />}
              onClick={handleRunTest}
              disabled={!selectedPlaybook || isRunning}
            >
              {isRunning ? 'Running Test...' : 'Run Test'}
            </Button>
          </div>

          {/* Right Panel - Results */}
          <div>
            <Card className="h-full">
              <CardHeader title="Test Results" />

              {!testResults ? (
                <div className="text-center py-12">
                  <CpuChipIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Run a test to see results</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Status */}
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <CheckCircleIcon className="h-6 w-6 text-green-600" />
                      <span className="font-medium text-green-800">Test Passed</span>
                      {testResults.extractedData?.decision && (
                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                          testResults.extractedData.decision === 'AUTO-APPROVE'
                            ? 'bg-green-200 text-green-800'
                            : testResults.extractedData.decision === 'REFER'
                            ? 'bg-yellow-200 text-yellow-800'
                            : 'bg-red-200 text-red-800'
                        }`}>
                          {testResults.extractedData.decision}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-green-600">
                      <ClockIcon className="h-4 w-4" />
                      <span>{testResults.duration}</span>
                    </div>
                  </div>

                  {/* Steps */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Execution Steps</h4>
                    <div className="space-y-2">
                      {testResults.steps.map((step: any, index: number) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            {step.status === 'success' ? (
                              <CheckCircleIcon className="h-5 w-5 text-green-500" />
                            ) : (
                              <XCircleIcon className="h-5 w-5 text-red-500" />
                            )}
                            <span className="text-gray-700">{step.name}</span>
                          </div>
                          <span className="text-sm text-gray-500">{step.duration}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Extracted Data */}
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3">Extracted Data</h4>
                    <div className="bg-gray-900 rounded-xl p-4 overflow-x-auto">
                      <pre className="text-sm text-green-400">
                        {JSON.stringify(testResults.extractedData, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
