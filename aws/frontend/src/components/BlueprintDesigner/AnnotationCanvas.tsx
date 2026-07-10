/**
 * Annotation Canvas Component
 * SVG overlay for drawing and displaying bounding boxes on PDF pages
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { BoundingBox, FieldAnnotation } from './types';

interface AnnotationCanvasProps {
  annotations: FieldAnnotation[];
  currentPage: number;
  selectedFieldName: string | null;
  isDrawing: boolean;
  onAnnotationCreate: (boundingBox: BoundingBox) => void;
  onAnnotationSelect: (annotation: FieldAnnotation) => void;
  onAnnotationDelete: (annotationId: string) => void;
}

// Color palette for different fields
const FIELD_COLORS = [
  '#3B82F6', // blue
  '#10B981', // green
  '#F59E0B', // amber
  '#EF4444', // red
  '#8B5CF6', // violet
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#F97316', // orange
];

const getFieldColor = (fieldName: string): string => {
  const hash = fieldName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return FIELD_COLORS[hash % FIELD_COLORS.length];
};

export const AnnotationCanvas: React.FC<AnnotationCanvasProps> = ({
  annotations,
  currentPage,
  selectedFieldName,
  isDrawing,
  onAnnotationCreate,
  onAnnotationSelect,
  onAnnotationDelete
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [drawCurrent, setDrawCurrent] = useState<{ x: number; y: number } | null>(null);
  const [hoveredAnnotation, setHoveredAnnotation] = useState<string | null>(null);

  // Filter annotations for current page
  const pageAnnotations = annotations.filter(a => a.boundingBox.page === currentPage);

  // Normalize mouse coordinates to 0-1 range
  const normalizeCoords = useCallback((event: React.MouseEvent): { x: number; y: number } => {
    if (!svgRef.current) return { x: 0, y: 0 };

    const rect = svgRef.current.getBoundingClientRect();
    return {
      x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height))
    };
  }, []);

  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    if (!isDrawing || !selectedFieldName) return;

    event.preventDefault();
    const coords = normalizeCoords(event);
    setDrawStart(coords);
    setDrawCurrent(coords);
  }, [isDrawing, selectedFieldName, normalizeCoords]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (!drawStart) return;

    event.preventDefault();
    const coords = normalizeCoords(event);
    setDrawCurrent(coords);
  }, [drawStart, normalizeCoords]);

  const handleMouseUp = useCallback((event: React.MouseEvent) => {
    if (!drawStart || !drawCurrent || !selectedFieldName) {
      setDrawStart(null);
      setDrawCurrent(null);
      return;
    }

    // Calculate bounding box
    const x = Math.min(drawStart.x, drawCurrent.x);
    const y = Math.min(drawStart.y, drawCurrent.y);
    const width = Math.abs(drawCurrent.x - drawStart.x);
    const height = Math.abs(drawCurrent.y - drawStart.y);

    // Only create if box is big enough (at least 1% of page)
    if (width > 0.01 && height > 0.01) {
      onAnnotationCreate({
        x,
        y,
        width,
        height,
        page: currentPage
      });
    }

    setDrawStart(null);
    setDrawCurrent(null);
  }, [drawStart, drawCurrent, currentPage, selectedFieldName, onAnnotationCreate]);

  const handleAnnotationClick = useCallback((event: React.MouseEvent, annotation: FieldAnnotation) => {
    event.stopPropagation();
    onAnnotationSelect(annotation);
  }, [onAnnotationSelect]);

  const handleDeleteClick = useCallback((event: React.MouseEvent, annotationId: string) => {
    event.stopPropagation();
    onAnnotationDelete(annotationId);
  }, [onAnnotationDelete]);

  // Keyboard handling for delete
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.key === 'Delete' || event.key === 'Backspace') && hoveredAnnotation) {
        onAnnotationDelete(hoveredAnnotation);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hoveredAnnotation, onAnnotationDelete]);

  // Calculate drawing rect coordinates
  const getDrawingRect = () => {
    if (!drawStart || !drawCurrent) return null;

    return {
      x: Math.min(drawStart.x, drawCurrent.x) * 100,
      y: Math.min(drawStart.y, drawCurrent.y) * 100,
      width: Math.abs(drawCurrent.x - drawStart.x) * 100,
      height: Math.abs(drawCurrent.y - drawStart.y) * 100
    };
  };

  const drawingRect = getDrawingRect();

  return (
    <svg
      ref={svgRef}
      className="w-full h-full"
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      style={{
        cursor: isDrawing && selectedFieldName ? 'crosshair' : 'default'
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Existing annotations */}
      {pageAnnotations.map((annotation) => {
        const color = getFieldColor(annotation.fieldName);
        const isHovered = hoveredAnnotation === annotation.id;

        return (
          <g
            key={annotation.id}
            onMouseEnter={() => setHoveredAnnotation(annotation.id)}
            onMouseLeave={() => setHoveredAnnotation(null)}
            onClick={(e) => handleAnnotationClick(e, annotation)}
            style={{ cursor: 'pointer' }}
          >
            {/* Bounding box */}
            <rect
              x={annotation.boundingBox.x * 100}
              y={annotation.boundingBox.y * 100}
              width={annotation.boundingBox.width * 100}
              height={annotation.boundingBox.height * 100}
              fill={color}
              fillOpacity={isHovered ? 0.3 : 0.15}
              stroke={color}
              strokeWidth={isHovered ? 0.5 : 0.3}
              strokeDasharray={isHovered ? 'none' : '0.5 0.5'}
            />

            {/* Field label */}
            <rect
              x={annotation.boundingBox.x * 100}
              y={annotation.boundingBox.y * 100 - 2.5}
              width={Math.min(annotation.fieldName.length * 0.8 + 1, 20)}
              height={2.5}
              fill={color}
              rx={0.3}
            />
            <text
              x={annotation.boundingBox.x * 100 + 0.5}
              y={annotation.boundingBox.y * 100 - 0.7}
              fill="white"
              fontSize="1.5"
              fontFamily="system-ui"
            >
              {annotation.fieldName.length > 20
                ? annotation.fieldName.slice(0, 18) + '...'
                : annotation.fieldName
              }
            </text>

            {/* Delete button (visible on hover) */}
            {isHovered && (
              <g
                onClick={(e) => handleDeleteClick(e, annotation.id)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  cx={annotation.boundingBox.x * 100 + annotation.boundingBox.width * 100}
                  cy={annotation.boundingBox.y * 100}
                  r={1.5}
                  fill="#EF4444"
                  stroke="white"
                  strokeWidth={0.2}
                />
                <text
                  x={annotation.boundingBox.x * 100 + annotation.boundingBox.width * 100}
                  y={annotation.boundingBox.y * 100 + 0.5}
                  fill="white"
                  fontSize="1.5"
                  textAnchor="middle"
                  fontFamily="system-ui"
                >
                  ×
                </text>
              </g>
            )}
          </g>
        );
      })}

      {/* Drawing preview */}
      {drawingRect && selectedFieldName && (
        <rect
          x={drawingRect.x}
          y={drawingRect.y}
          width={drawingRect.width}
          height={drawingRect.height}
          fill={getFieldColor(selectedFieldName)}
          fillOpacity={0.2}
          stroke={getFieldColor(selectedFieldName)}
          strokeWidth={0.3}
          strokeDasharray="1 0.5"
        />
      )}
    </svg>
  );
};

export default AnnotationCanvas;
