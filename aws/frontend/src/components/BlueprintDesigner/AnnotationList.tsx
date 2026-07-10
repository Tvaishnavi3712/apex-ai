/**
 * Annotation List Component
 * Displays list of field annotations with edit/delete capabilities
 */

import React from 'react';
import { TrashIcon, EyeIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { FieldAnnotation, BlueprintField } from './types';

interface AnnotationListProps {
  annotations: FieldAnnotation[];
  fields: BlueprintField[];
  onAnnotationSelect: (annotation: FieldAnnotation) => void;
  onAnnotationDelete: (annotationId: string) => void;
  onGoToPage: (page: number) => void;
  selectedAnnotationId?: string;
}

export const AnnotationList: React.FC<AnnotationListProps> = ({
  annotations,
  fields,
  onAnnotationSelect,
  onAnnotationDelete,
  onGoToPage,
  selectedAnnotationId
}) => {
  // Group annotations by field
  const annotationsByField = annotations.reduce((acc, annotation) => {
    if (!acc[annotation.fieldName]) {
      acc[annotation.fieldName] = [];
    }
    acc[annotation.fieldName].push(annotation);
    return acc;
  }, {} as Record<string, FieldAnnotation[]>);

  // Fields without annotations
  const unannotatedFields = fields.filter(
    field => !annotationsByField[field.name]
  );

  return (
    <div className="h-full overflow-auto">
      {/* Annotated fields */}
      {Object.keys(annotationsByField).length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-500 mb-2 px-3">
            Annotated Fields ({Object.keys(annotationsByField).length})
          </h4>
          <div className="space-y-1">
            {Object.entries(annotationsByField).map(([fieldName, fieldAnnotations]) => (
              <div key={fieldName} className="border-b border-gray-100 last:border-0">
                {fieldAnnotations.map((annotation) => (
                  <div
                    key={annotation.id}
                    className={`
                      flex items-center justify-between px-3 py-2 cursor-pointer
                      hover:bg-gray-50 transition-colors
                      ${selectedAnnotationId === annotation.id ? 'bg-blue-50' : ''}
                    `}
                    onClick={() => onAnnotationSelect(annotation)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <DocumentTextIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-900 truncate">
                          {fieldName}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5 flex items-center space-x-2">
                        <span>Page {annotation.boundingBox.page}</span>
                        {annotation.sampleText && (
                          <span className="text-gray-400 truncate max-w-[150px]">
                            "{annotation.sampleText}"
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-1 ml-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onGoToPage(annotation.boundingBox.page);
                        }}
                        className="p-1 text-gray-400 hover:text-blue-500 rounded"
                        title="Go to page"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onAnnotationDelete(annotation.id);
                        }}
                        className="p-1 text-gray-400 hover:text-red-500 rounded"
                        title="Delete annotation"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unannotated fields */}
      {unannotatedFields.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2 px-3">
            Fields Without Annotations ({unannotatedFields.length})
          </h4>
          <div className="space-y-1">
            {unannotatedFields.map((field) => (
              <div
                key={field.id}
                className="flex items-center px-3 py-2 text-gray-400"
              >
                <DocumentTextIcon className="w-4 h-4 mr-2 opacity-50" />
                <span className="text-sm">{field.name}</span>
                <span className="text-xs ml-auto text-gray-300">
                  Not annotated
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {annotations.length === 0 && fields.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
          <DocumentTextIcon className="w-12 h-12 mb-3 opacity-50" />
          <p className="text-sm">No fields defined yet</p>
          <p className="text-xs mt-1">Add fields in the Fields tab first</p>
        </div>
      )}

      {annotations.length === 0 && fields.length > 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
          <DocumentTextIcon className="w-12 h-12 mb-3 opacity-50" />
          <p className="text-sm">No annotations yet</p>
          <p className="text-xs mt-1">Select a field and draw on the PDF</p>
        </div>
      )}
    </div>
  );
};

export default AnnotationList;
