/**
 * Human Review Page - Human-in-the-Loop Approval Workflow
 * Underwriters review and approve AI decisions here
 */

import React, { useState } from 'react';
import Head from 'next/head';
import { Card, CardHeader, Badge } from '@/components/common';
import { HumanReviewPanel } from '@/components/AgentHub/HumanReviewPanel';
import {
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  UserGroupIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

// Demo pending reviews
const pendingReviews = [
  {
    id: 'review-001',
    submissionId: 'CRE-2024-001848',
    propertyName: 'Bayshore Mixed-Use Complex',
    propertyType: 'Mixed-Use',
    location: 'Miami, FL',
    tiv: 54000000,
    aiDecision: 'REFER' as const,
    aiConfidence: 0.82,
    riskScore: 67,
    premiumIndication: 142000,
    waitTime: '2h 15m',
    priority: 'high',
    concerns: ['Hurricane exposure', 'TIV > $25M'],
  },
  {
    id: 'review-002',
    submissionId: 'CRE-2024-001852',
    propertyName: 'Downtown Tech Campus',
    propertyType: 'Office Complex',
    location: 'San Francisco, CA',
    tiv: 89000000,
    aiDecision: 'REFER' as const,
    aiConfidence: 0.78,
    riskScore: 58,
    premiumIndication: 215000,
    waitTime: '45m',
    priority: 'normal',
    concerns: ['Earthquake zone', 'TIV > $25M'],
  },
  {
    id: 'review-003',
    submissionId: 'CRE-2024-001855',
    propertyName: 'Harbor Industrial Complex',
    propertyType: 'Industrial',
    location: 'Long Beach, CA',
    tiv: 32000000,
    aiDecision: 'DECLINE' as const,
    aiConfidence: 0.91,
    riskScore: 84,
    premiumIndication: 0,
    waitTime: '30m',
    priority: 'urgent',
    concerns: ['Flood Zone A', 'Poor loss history', 'Hazardous materials'],
  },
];

export default function HumanReviewPage() {
  const [selectedReview, setSelectedReview] = useState<string | null>('review-001');
  const [filter, setFilter] = useState<'all' | 'refer' | 'decline'>('all');

  const filteredReviews = pendingReviews.filter((r) => {
    if (filter === 'all') return true;
    if (filter === 'refer') return r.aiDecision === 'REFER';
    if (filter === 'decline') return r.aiDecision === 'DECLINE';
    return true;
  });

  const stats = {
    pending: pendingReviews.length,
    avgWaitTime: '1h 10m',
    reviewedToday: 12,
    approvalRate: '78%',
  };

  return (
    <>
      <Head>
        <title>Human Review | APEX AI Platform</title>
      </Head>

      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <ClipboardDocumentCheckIcon className="h-6 w-6 text-amber-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Human Review Queue</h1>
              <p className="text-gray-500">AI decisions requiring underwriter approval</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Signed in as:</span>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full">
              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-medium">
                MC
              </div>
              <span className="text-sm font-medium text-gray-700">Mike Chen</span>
              <Badge variant="outline">Senior Underwriter</Badge>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Review</p>
                <p className="text-2xl font-bold text-amber-600">{stats.pending}</p>
              </div>
              <ExclamationTriangleIcon className="h-8 w-8 text-amber-200" />
            </div>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Wait Time</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avgWaitTime}</p>
              </div>
              <ClockIcon className="h-8 w-8 text-gray-200" />
            </div>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Reviewed Today</p>
                <p className="text-2xl font-bold text-green-600">{stats.reviewedToday}</p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-green-200" />
            </div>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Approval Rate</p>
                <p className="text-2xl font-bold text-blue-600">{stats.approvalRate}</p>
              </div>
              <UserGroupIcon className="h-8 w-8 text-blue-200" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Left Panel - Review Queue */}
          <div className="col-span-1">
            <Card>
              <CardHeader
                title="Review Queue"
                subtitle={`${filteredReviews.length} items pending`}
                action={
                  <div className="flex items-center gap-2">
                    <FunnelIcon className="h-4 w-4 text-gray-400" />
                    <select
                      value={filter}
                      onChange={(e) => setFilter(e.target.value as any)}
                      className="text-sm border-none bg-transparent focus:ring-0"
                    >
                      <option value="all">All</option>
                      <option value="refer">Referrals</option>
                      <option value="decline">Declines</option>
                    </select>
                  </div>
                }
              />
              <div className="space-y-2">
                {filteredReviews.map((review) => (
                  <button
                    key={review.id}
                    onClick={() => setSelectedReview(review.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedReview === review.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className="font-medium text-gray-900 text-sm truncate">
                        {review.propertyName}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        review.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                        review.priority === 'high' ? 'bg-amber-100 text-amber-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {review.priority}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                      <span>{review.propertyType}</span>
                      <span>•</span>
                      <span>{review.location}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        review.aiDecision === 'REFER' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {review.aiDecision}
                      </span>
                      <div className="flex items-center gap-1 text-xs text-gray-400">
                        <ClockIcon className="h-3 w-3" />
                        {review.waitTime}
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {review.concerns.slice(0, 2).map((concern, idx) => (
                        <span key={idx} className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
                          {concern}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </Card>
          </div>

          {/* Right Panel - Review Details */}
          <div className="col-span-2">
            {selectedReview ? (
              <HumanReviewPanel />
            ) : (
              <Card className="h-full flex items-center justify-center">
                <div className="text-center py-12">
                  <ClipboardDocumentCheckIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Select an item to review</p>
                </div>
              </Card>
            )}
          </div>
        </div>

        {/* Workflow Explanation */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Human-in-the-Loop Workflow</h3>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-blue-600 font-bold">1</span>
                </div>
                <span className="text-xs text-gray-600 text-center">AI Extracts<br/>& Analyzes</span>
              </div>
              <div className="w-12 h-0.5 bg-blue-200" />
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-blue-600 font-bold">2</span>
                </div>
                <span className="text-xs text-gray-600 text-center">AI Makes<br/>Recommendation</span>
              </div>
              <div className="w-12 h-0.5 bg-blue-200" />
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-amber-600 font-bold">3</span>
                </div>
                <span className="text-xs text-gray-600 text-center">Human<br/>Reviews</span>
              </div>
              <div className="w-12 h-0.5 bg-blue-200" />
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-green-600 font-bold">4</span>
                </div>
                <span className="text-xs text-gray-600 text-center">Approve /<br/>Modify / Reject</span>
              </div>
              <div className="w-12 h-0.5 bg-blue-200" />
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-purple-600 font-bold">5</span>
                </div>
                <span className="text-xs text-gray-600 text-center">Decision<br/>Executed</span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">
                <strong>68%</strong> auto-approved by AI
              </p>
              <p className="text-sm text-gray-600">
                <strong>32%</strong> require human review
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
