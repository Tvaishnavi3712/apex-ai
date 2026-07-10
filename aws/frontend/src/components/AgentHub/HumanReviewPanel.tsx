/**
 * Human Review Panel - Human-in-the-Loop Approval Component
 * Allows underwriters to review, approve, modify, or reject AI decisions
 */

import React, { useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  PencilSquareIcon,
  ExclamationTriangleIcon,
  UserIcon,
  CpuChipIcon,
  ClockIcon,
  DocumentTextIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';

interface ReviewItem {
  id: string;
  submissionId: string;
  propertyName: string;
  aiDecision: 'APPROVE' | 'REFER' | 'DECLINE';
  aiConfidence: number;
  riskScore: number;
  premiumIndication: number;
  keyFactors: string[];
  concerns: string[];
  extractedData: Record<string, any>;
  status: 'pending_review' | 'approved' | 'modified' | 'rejected';
  timestamp: string;
}

interface HumanReviewPanelProps {
  item?: ReviewItem;
  onApprove?: (id: string, comments: string) => void;
  onReject?: (id: string, reason: string) => void;
  onModify?: (id: string, modifications: Record<string, any>) => void;
}

// Demo data
const demoReviewItem: ReviewItem = {
  id: 'review-001',
  submissionId: 'CRE-2024-001848',
  propertyName: 'Bayshore Mixed-Use Complex',
  aiDecision: 'REFER',
  aiConfidence: 0.82,
  riskScore: 67,
  premiumIndication: 142000,
  keyFactors: [
    'Mixed-use property in Miami, FL',
    'Total Insurable Value: $54,000,000',
    'Occupancy Rate: 88%',
    'Year Built: 2015',
    'Construction: Non-Combustible (ISO Class 4)',
  ],
  concerns: [
    'Hurricane Zone: High exposure area',
    'TIV exceeds auto-approval limit ($25M)',
    'Occupancy below preferred threshold (85%)',
    'Roof age: 9 years (approaching maintenance window)',
  ],
  extractedData: {
    property_address: '2500 Biscayne Blvd, Miami, FL 33137',
    property_type: 'Mixed-Use Retail/Residential',
    total_insurable_value: 54000000,
    building_value: 42000000,
    contents_value: 8000000,
    business_income: 4000000,
    occupancy_rate: 88,
    year_built: 2015,
    construction_type: 'Non-Combustible',
    roof_age: 9,
    sprinkler_system: 'Full Wet System',
    hurricane_shutters: false,
    flood_zone: 'X',
    loss_history_years: 3,
    prior_claims: 0,
  },
  status: 'pending_review',
  timestamp: new Date().toISOString(),
};

export const HumanReviewPanel: React.FC<HumanReviewPanelProps> = ({
  item = demoReviewItem,
  onApprove,
  onReject,
  onModify,
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [comments, setComments] = useState('');
  const [modifiedPremium, setModifiedPremium] = useState(item.premiumIndication);
  const [modifiedDecision, setModifiedDecision] = useState(item.aiDecision);
  const [additionalConditions, setAdditionalConditions] = useState('');
  const [reviewStatus, setReviewStatus] = useState<'pending' | 'approved' | 'modified' | 'rejected'>('pending');

  const handleApprove = () => {
    setReviewStatus('approved');
    onApprove?.(item.id, comments);
  };

  const handleReject = () => {
    setReviewStatus('rejected');
    onReject?.(item.id, comments);
  };

  const handleModifyAndApprove = () => {
    setReviewStatus('modified');
    setShowModifyModal(false);
    onModify?.(item.id, {
      premium: modifiedPremium,
      decision: modifiedDecision,
      conditions: additionalConditions,
      comments,
    });
  };

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'APPROVE': return 'bg-green-100 text-green-800 border-green-200';
      case 'REFER': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'DECLINE': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (reviewStatus !== 'pending') {
    return (
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className={`flex items-center justify-center gap-3 p-4 rounded-lg ${
          reviewStatus === 'approved' ? 'bg-green-50' :
          reviewStatus === 'modified' ? 'bg-blue-50' : 'bg-red-50'
        }`}>
          {reviewStatus === 'approved' && <CheckCircleIcon className="h-8 w-8 text-green-600" />}
          {reviewStatus === 'modified' && <PencilSquareIcon className="h-8 w-8 text-blue-600" />}
          {reviewStatus === 'rejected' && <XCircleIcon className="h-8 w-8 text-red-600" />}
          <div className="text-center">
            <p className={`font-semibold text-lg ${
              reviewStatus === 'approved' ? 'text-green-800' :
              reviewStatus === 'modified' ? 'text-blue-800' : 'text-red-800'
            }`}>
              {reviewStatus === 'approved' && 'Decision Approved'}
              {reviewStatus === 'modified' && 'Decision Modified & Approved'}
              {reviewStatus === 'rejected' && 'Decision Rejected'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Reviewed by Mike Chen at {new Date().toLocaleTimeString()}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Human Review Required</h3>
              <p className="text-sm text-gray-600">AI recommendation needs underwriter approval</p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getDecisionColor(item.aiDecision)}`}>
            AI Recommends: {item.aiDecision}
          </span>
        </div>
      </div>

      {/* Submission Summary */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-medium text-gray-900">{item.propertyName}</h4>
            <p className="text-sm text-gray-500">{item.submissionId}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">
              ${item.premiumIndication.toLocaleString()}
            </p>
            <p className="text-sm text-gray-500">Indicated Premium</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-500">Risk Score</p>
            <p className={`text-xl font-bold ${item.riskScore > 70 ? 'text-red-600' : item.riskScore > 50 ? 'text-yellow-600' : 'text-green-600'}`}>
              {item.riskScore}/100
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-500">AI Confidence</p>
            <p className={`text-xl font-bold ${getConfidenceColor(item.aiConfidence)}`}>
              {Math.round(item.aiConfidence * 100)}%
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <p className="text-sm text-gray-500">TIV</p>
            <p className="text-xl font-bold text-gray-900">
              ${(item.extractedData.total_insurable_value / 1000000).toFixed(1)}M
            </p>
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center gap-2 mb-3">
          <CpuChipIcon className="h-5 w-5 text-purple-500" />
          <h4 className="font-medium text-gray-900">AI Analysis</h4>
        </div>

        {/* Key Factors */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Key Factors:</p>
          <ul className="space-y-1">
            {item.keyFactors.map((factor, idx) => (
              <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                <CheckCircleIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                {factor}
              </li>
            ))}
          </ul>
        </div>

        {/* Concerns */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Concerns Flagged:</p>
          <ul className="space-y-1">
            {item.concerns.map((concern, idx) => (
              <li key={idx} className="text-sm text-amber-700 flex items-start gap-2">
                <ExclamationTriangleIcon className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                {concern}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Expandable Details */}
      <div className="border-b">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-50"
        >
          <span className="text-sm font-medium text-gray-700">View Extracted Data</span>
          {showDetails ? (
            <ChevronUpIcon className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-gray-400" />
          )}
        </button>
        {showDetails && (
          <div className="px-6 pb-4">
            <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
              <pre className="text-sm text-green-400">
                {JSON.stringify(item.extractedData, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Review Comments */}
      <div className="px-6 py-4 border-b">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Review Comments (Optional)
        </label>
        <textarea
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Add any notes or conditions for this decision..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          rows={2}
        />
      </div>

      {/* Action Buttons */}
      <div className="px-6 py-4 bg-gray-50">
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <UserIcon className="h-4 w-4" />
          <span>Reviewing as: Mike Chen (Senior Underwriter)</span>
        </div>
        <div className="flex items-center gap-3 justify-end flex-wrap">
          <button
            onClick={handleReject}
            className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 flex items-center gap-2 whitespace-nowrap"
          >
            <XCircleIcon className="h-5 w-5" />
            Reject
          </button>
          <button
            onClick={() => setShowModifyModal(true)}
            className="px-4 py-2 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 flex items-center gap-2 whitespace-nowrap"
          >
            <PencilSquareIcon className="h-5 w-5" />
            Modify
          </button>
          <button
            onClick={handleApprove}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 whitespace-nowrap font-medium shadow-sm"
          >
            <CheckCircleIcon className="h-5 w-5" />
            Approve
          </button>
        </div>
      </div>

      {/* Modify Modal */}
      {showModifyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Modify AI Decision</h3>
              <p className="text-sm text-gray-500">Adjust the recommendation before approving</p>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Decision</label>
                <select
                  value={modifiedDecision}
                  onChange={(e) => setModifiedDecision(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="APPROVE">APPROVE</option>
                  <option value="REFER">REFER to Senior Underwriter</option>
                  <option value="DECLINE">DECLINE</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Premium</label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-gray-500">$</span>
                  <input
                    type="number"
                    value={modifiedPremium}
                    onChange={(e) => setModifiedPremium(Number(e.target.value))}
                    className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Additional Conditions</label>
                <textarea
                  value={additionalConditions}
                  onChange={(e) => setAdditionalConditions(e.target.value)}
                  placeholder="e.g., Require hurricane shutters, annual roof inspection..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                />
              </div>
            </div>
            <div className="px-6 py-4 bg-gray-50 flex justify-end gap-3 rounded-b-xl">
              <button
                onClick={() => setShowModifyModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleModifyAndApprove}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save & Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HumanReviewPanel;
