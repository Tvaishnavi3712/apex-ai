/**
 * Agent Chat - AI Copilot interface for Agent Hub
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button, Card, Badge } from '../common';
import { PaperAirplaneIcon, PaperClipIcon, SparklesIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  actions?: {
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    result?: any;
  }[];
}

interface AgentChatProps {
  sessionId: string;
  agentName?: string;
  onSendMessage: (message: string, attachments?: File[]) => Promise<void>;
  messages: Message[];
  isLoading?: boolean;
  context?: any;
}

export const AgentChat: React.FC<AgentChatProps> = ({
  sessionId,
  agentName = 'Apex Agent',
  onSendMessage,
  messages,
  isLoading = false,
  context,
}) => {
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && attachments.length === 0) return;

    await onSendMessage(input, attachments);
    setInput('');
    setAttachments([]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments((prev) => [...prev, ...files]);
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  const suggestedPrompts = [
    "Process the latest invoices in the queue",
    "Show me pending approvals over $10,000",
    "Check compliance status for vendor ABC Corp",
    "Generate a summary of today's processing",
  ];

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-apex-500 to-purple-600 flex items-center justify-center">
            <SparklesIcon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">{agentName}</h2>
            <p className="text-sm text-gray-500">AI-powered assistant</p>
          </div>
        </div>
        <Badge variant="success" dot>Active</Badge>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-apex-100 flex items-center justify-center">
              <SparklesIcon className="h-8 w-8 text-apex-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              How can I help you today?
            </h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              I can help you process documents, check compliance, route approvals, and more.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {suggestedPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt)}
                  className="px-4 py-2 text-sm bg-white border border-gray-200 rounded-full hover:border-apex-300 hover:bg-apex-50 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={clsx(
                'flex gap-4',
                message.role === 'user' ? 'flex-row-reverse' : ''
              )}
            >
              <div
                className={clsx(
                  'w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center',
                  message.role === 'user'
                    ? 'bg-gray-200'
                    : 'bg-gradient-to-br from-apex-500 to-purple-600'
                )}
              >
                {message.role === 'user' ? (
                  <span className="text-sm font-medium text-gray-600">U</span>
                ) : (
                  <SparklesIcon className="h-4 w-4 text-white" />
                )}
              </div>

              <div
                className={clsx(
                  'max-w-[70%] rounded-2xl px-4 py-3',
                  message.role === 'user'
                    ? 'bg-apex-600 text-white'
                    : 'bg-white border border-gray-200'
                )}
              >
                <div className={clsx(
                  'prose prose-sm max-w-none',
                  message.role === 'user' && 'prose-invert'
                )}>
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {/* Action Status */}
                {message.actions && message.actions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100 space-y-2">
                    {message.actions.map((action, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 text-sm"
                      >
                        <span className={clsx(
                          'w-2 h-2 rounded-full',
                          action.status === 'completed' && 'bg-success-500',
                          action.status === 'running' && 'bg-apex-500 animate-pulse',
                          action.status === 'failed' && 'bg-danger-500',
                          action.status === 'pending' && 'bg-gray-300'
                        )} />
                        <span className="font-mono text-gray-600">{action.name}</span>
                        <Badge
                          variant={
                            action.status === 'completed' ? 'success' :
                            action.status === 'failed' ? 'danger' :
                            action.status === 'running' ? 'info' : 'default'
                          }
                          size="sm"
                        >
                          {action.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}

                <p className={clsx(
                  'text-xs mt-2',
                  message.role === 'user' ? 'text-apex-200' : 'text-gray-400'
                )}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-apex-500 to-purple-600 flex items-center justify-center">
              <SparklesIcon className="h-4 w-4 text-white animate-pulse" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="px-6 py-2 bg-white border-t border-gray-100">
          <div className="flex gap-2 flex-wrap">
            {attachments.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full text-sm"
              >
                <PaperClipIcon className="h-4 w-4 text-gray-500" />
                <span className="truncate max-w-[150px]">{file.name}</span>
                <button
                  onClick={() => removeAttachment(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            multiple
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <PaperClipIcon className="h-6 w-6" />
          </button>

          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask me anything..."
              rows={1}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-apex-500 focus:border-transparent"
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            disabled={(!input.trim() && attachments.length === 0) || isLoading}
            icon={<PaperAirplaneIcon className="h-5 w-5" />}
          >
            Send
          </Button>
        </form>
      </div>
    </div>
  );
};

export default AgentChat;
