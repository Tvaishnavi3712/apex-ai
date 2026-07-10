/**
 * PDF Viewer Component
 * Renders PDF documents with page navigation for annotation
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, MagnifyingGlassMinusIcon, MagnifyingGlassPlusIcon } from '@heroicons/react/24/outline';

interface PDFViewerProps {
  documentUrl: string;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onDocumentLoad?: (numPages: number) => void;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  children?: React.ReactNode; // For overlay content (annotation canvas)
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  documentUrl,
  currentPage,
  totalPages,
  onPageChange,
  onDocumentLoad,
  zoom,
  onZoomChange,
  children
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // For this implementation, we'll use an iframe/embed approach
  // In production, you'd use @react-pdf-viewer/core
  const pdfUrl = `${documentUrl}#page=${currentPage}&zoom=${zoom * 100}`;

  const handleZoomIn = useCallback(() => {
    onZoomChange(Math.min(zoom + 0.25, 3));
  }, [zoom, onZoomChange]);

  const handleZoomOut = useCallback(() => {
    onZoomChange(Math.max(zoom - 0.25, 0.5));
  }, [zoom, onZoomChange]);

  const handlePrevPage = useCallback(() => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  }, [currentPage, onPageChange]);

  const handleNextPage = useCallback(() => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  }, [currentPage, totalPages, onPageChange]);

  useEffect(() => {
    setIsLoading(true);
    // Simulate document load - in real implementation, this comes from PDF.js
    const timer = setTimeout(() => {
      setIsLoading(false);
      if (onDocumentLoad && totalPages === 0) {
        // Default to 1 page if not known
        onDocumentLoad(1);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [documentUrl, onDocumentLoad, totalPages]);

  return (
    <div className="flex flex-col h-full bg-gray-100">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b">
        {/* Page Navigation */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handlePrevPage}
            disabled={currentPage <= 1}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Previous page"
          >
            <ChevronLeftIcon className="w-5 h-5" />
          </button>

          <span className="text-sm text-gray-600">
            Page {currentPage} of {totalPages || '?'}
          </span>

          <button
            onClick={handleNextPage}
            disabled={currentPage >= totalPages}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Next page"
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 0.5}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50"
            title="Zoom out"
          >
            <MagnifyingGlassMinusIcon className="w-5 h-5" />
          </button>

          <span className="text-sm text-gray-600 w-16 text-center">
            {Math.round(zoom * 100)}%
          </span>

          <button
            onClick={handleZoomIn}
            disabled={zoom >= 3}
            className="p-1 rounded hover:bg-gray-100 disabled:opacity-50"
            title="Zoom in"
          >
            <MagnifyingGlassPlusIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* PDF Content */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto relative"
        style={{ background: '#525659' }}
      >
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100/80 z-10">
            <div className="flex flex-col items-center">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <span className="mt-2 text-sm text-gray-600">Loading document...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-center">
              <p className="text-red-500 mb-2">Failed to load document</p>
              <p className="text-sm text-gray-500">{error}</p>
            </div>
          </div>
        )}

        {/* PDF Container with Overlay */}
        <div
          className="relative mx-auto my-4"
          style={{
            width: `${zoom * 100}%`,
            maxWidth: '100%',
            minHeight: '800px',
            background: 'white',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}
        >
          {/* PDF Embed - Replace with react-pdf in production */}
          <embed
            src={pdfUrl}
            type="application/pdf"
            className="w-full h-full"
            style={{ minHeight: '800px' }}
            onLoad={() => setIsLoading(false)}
            onError={() => setError('Failed to load PDF')}
          />

          {/* Annotation Overlay */}
          {children && (
            <div className="absolute inset-0 pointer-events-auto">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
