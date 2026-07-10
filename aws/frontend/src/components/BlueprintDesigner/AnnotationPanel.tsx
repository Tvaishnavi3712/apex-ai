/**
 * Annotation Panel Component
 * Main container for visual PDF annotation functionality
 */

import React, { useState, useCallback } from 'react';
import {
  ArrowUpTrayIcon,
  PencilIcon,
  HandRaisedIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { PDFViewer } from './PDFViewer';
import { AnnotationCanvas } from './AnnotationCanvas';
import { AnnotationList } from './AnnotationList';
import { BoundingBox, FieldAnnotation, BlueprintField } from './types';

interface AnnotationPanelProps {
  sampleDocumentUrl?: string;
  annotations: FieldAnnotation[];
  fields: BlueprintField[];
  onAnnotationsChange: (annotations: FieldAnnotation[]) => void;
  onUploadSample: (file: File) => void;
  isUploading?: boolean;
}

export const AnnotationPanel: React.FC<AnnotationPanelProps> = ({
  sampleDocumentUrl,
  annotations,
  fields,
  onAnnotationsChange,
  onUploadSample,
  isUploading = false
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [zoom, setZoom] = useState(1);
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [selectedFieldName, setSelectedFieldName] = useState<string | null>(null);
  const [selectedAnnotationId, setSelectedAnnotationId] = useState<string | undefined>();

  // Handle file upload
  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUploadSample(file);
    }
  }, [onUploadSample]);

  // Handle new annotation creation
  const handleAnnotationCreate = useCallback((boundingBox: BoundingBox) => {
    if (!selectedFieldName) return;

    const newAnnotation: FieldAnnotation = {
      id: `ann_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      fieldName: selectedFieldName,
      boundingBox
    };

    onAnnotationsChange([...annotations, newAnnotation]);
  }, [selectedFieldName, annotations, onAnnotationsChange]);

  // Handle annotation selection
  const handleAnnotationSelect = useCallback((annotation: FieldAnnotation) => {
    setSelectedAnnotationId(annotation.id);
    setCurrentPage(annotation.boundingBox.page);
  }, []);

  // Handle annotation deletion
  const handleAnnotationDelete = useCallback((annotationId: string) => {
    onAnnotationsChange(annotations.filter(a => a.id !== annotationId));
    if (selectedAnnotationId === annotationId) {
      setSelectedAnnotationId(undefined);
    }
  }, [annotations, onAnnotationsChange, selectedAnnotationId]);

  // Handle page navigation
  const handleGoToPage = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  // Toggle drawing mode
  const toggleDrawingMode = useCallback(() => {
    setIsDrawingMode(prev => !prev);
    if (isDrawingMode) {
      setSelectedFieldName(null);
    }
  }, [isDrawingMode]);

  // No sample document uploaded
  if (!sampleDocumentUrl) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <ArrowUpTrayIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Upload a Sample Document
          </h3>
          <p className="text-gray-500 mb-6">
            Upload a PDF document to annotate field locations visually.
            This helps improve extraction accuracy.
          </p>

          <label className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Uploading...
              </>
            ) : (
              <>
                <ArrowUpTrayIcon className="w-5 h-5 mr-2" />
                Choose PDF File
              </>
            )}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileChange}
              disabled={isUploading}
            />
          </label>

          <p className="text-xs text-gray-400 mt-4">
            Supported: PDF files up to 50MB
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* Left side: PDF Viewer */}
      <div className="flex-1 flex flex-col">
        {/* Drawing mode toolbar */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b">
          <div className="flex items-center space-x-4">
            {/* Draw mode toggle */}
            <button
              onClick={toggleDrawingMode}
              className={`
                flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                ${isDrawingMode
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border'
                }
              `}
            >
              {isDrawingMode ? (
                <>
                  <PencilIcon className="w-4 h-4 mr-1.5" />
                  Drawing Mode
                </>
              ) : (
                <>
                  <HandRaisedIcon className="w-4 h-4 mr-1.5" />
                  Select Mode
                </>
              )}
            </button>

            {/* Field selector (only in drawing mode) */}
            {isDrawingMode && (
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600">Field:</label>
                <select
                  value={selectedFieldName || ''}
                  onChange={(e) => setSelectedFieldName(e.target.value || null)}
                  className="text-sm border rounded-lg px-2 py-1 bg-white"
                >
                  <option value="">Select a field...</option>
                  {fields.map((field) => (
                    <option key={field.id} value={field.name}>
                      {field.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Instructions */}
          {isDrawingMode && selectedFieldName && (
            <p className="text-sm text-gray-500">
              Click and drag on the PDF to annotate "{selectedFieldName}"
            </p>
          )}
        </div>

        {/* PDF Viewer with annotation overlay */}
        <div className="flex-1 relative">
          <PDFViewer
            documentUrl={sampleDocumentUrl}
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            onDocumentLoad={setTotalPages}
            zoom={zoom}
            onZoomChange={setZoom}
          >
            <AnnotationCanvas
              annotations={annotations}
              currentPage={currentPage}
              selectedFieldName={selectedFieldName}
              isDrawing={isDrawingMode}
              onAnnotationCreate={handleAnnotationCreate}
              onAnnotationSelect={handleAnnotationSelect}
              onAnnotationDelete={handleAnnotationDelete}
            />
          </PDFViewer>
        </div>
      </div>

      {/* Right side: Annotation List */}
      <div className="w-80 border-l bg-white flex flex-col">
        <div className="px-4 py-3 border-b">
          <h3 className="font-medium text-gray-900">Field Annotations</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {annotations.length} annotation{annotations.length !== 1 ? 's' : ''}
          </p>
        </div>

        <AnnotationList
          annotations={annotations}
          fields={fields}
          onAnnotationSelect={handleAnnotationSelect}
          onAnnotationDelete={handleAnnotationDelete}
          onGoToPage={handleGoToPage}
          selectedAnnotationId={selectedAnnotationId}
        />

        {/* Upload new sample */}
        <div className="border-t p-4">
          <label className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 cursor-pointer hover:bg-gray-50 transition-colors">
            <ArrowUpTrayIcon className="w-4 h-4 mr-2" />
            Upload Different Document
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileChange}
              disabled={isUploading}
            />
          </label>
        </div>
      </div>
    </div>
  );
};

export default AnnotationPanel;
