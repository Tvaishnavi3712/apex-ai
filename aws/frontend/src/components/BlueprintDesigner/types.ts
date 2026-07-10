/**
 * Type definitions for BlueprintDesigner component
 */

export type FieldType = 'string' | 'number' | 'boolean' | 'date' | 'array' | 'object';

export type InferenceType = 'explicit' | 'inferred';

export interface BlueprintField {
  id: string;
  name: string;
  type: FieldType;
  inferenceType: InferenceType;
  instruction: string;
  required: boolean;
  validation?: ValidationRule;
}

export interface ValidationRule {
  type: 'pattern' | 'min' | 'max' | 'minLength' | 'maxLength' | 'enum' | 'custom';
  value: string | number | string[];
  message?: string;
}

export interface NestedField {
  name: string;
  type: FieldType;
  instruction?: string;
}

export interface ArrayFieldDefinition {
  id: string;
  name: string;
  description: string;
  properties: NestedField[];
}

export interface Blueprint {
  id: string;
  name: string;
  description: string;
  documentType: string;
  industry: string;
  stage: 'DEVELOPMENT' | 'LIVE';
  fields: BlueprintField[];
  definitions: ArrayFieldDefinition[];
  createdAt?: string;
  updatedAt?: string;
}

export interface BlueprintSchema {
  class: string;
  description: string;
  definitions: Record<string, {
    properties: Record<string, {
      type: string;
      inferenceType?: string;
      instruction?: string;
    }>;
  }>;
  properties: Record<string, {
    type: string;
    inferenceType?: string;
    instruction?: string;
    items?: {
      '$ref'?: string;
      type?: string;
    };
  }>;
}

export interface BlueprintDesignerProps {
  initialData?: Partial<ExtendedBlueprint>;
  onSave?: (blueprint: ExtendedBlueprint) => void;
  onDeploy?: (blueprint: Blueprint) => void;
  onTest?: (blueprint: Blueprint, documentUri: string) => void;
  isLoading?: boolean;
}

// =============================================================================
// Virtual Fields Types
// =============================================================================

export type ExpressionType = 'formula' | 'concatenate' | 'aggregate' | 'conditional' | 'lookup';

export interface VirtualColumn {
  id: string;
  name: string;
  type: FieldType;
  expressionType: ExpressionType;
  expression: string;
  description?: string;
  sourceFields: string[];
}

export interface VirtualTable {
  id: string;
  name: string;
  description?: string;
  sourceArray: string;
  groupBy?: string[];
  aggregations: VirtualColumn[];
}

// =============================================================================
// Annotation Types
// =============================================================================

export interface BoundingBox {
  x: number;      // 0-1 normalized (left edge)
  y: number;      // 0-1 normalized (top edge)
  width: number;  // 0-1 normalized
  height: number; // 0-1 normalized
  page: number;   // 1-indexed page number
}

export interface FieldAnnotation {
  id: string;
  fieldName: string;        // Links to BlueprintField.name
  boundingBox: BoundingBox;
  sampleText?: string;      // Extracted text from region
  confidence?: number;
}

// =============================================================================
// Extended Blueprint with new features
// =============================================================================

export interface ExtendedBlueprint extends Blueprint {
  virtualColumns: VirtualColumn[];
  virtualTables: VirtualTable[];
  annotations: FieldAnnotation[];
  sampleDocumentUrl?: string;
}

// =============================================================================
// Schema Generation Types
// =============================================================================

export interface GeneratedField {
  name: string;
  type: FieldType;
  required: boolean;
  instruction: string;
  exampleValue?: string;
}

export interface SchemaGenerationResult {
  documentType: string;
  confidence: number;
  description: string;
  fields: GeneratedField[];
  definitions: ArrayFieldDefinition[];
}

export interface ClassificationResult {
  documentType: string;
  blueprintId?: string;
  blueprintName?: string;
  confidence: number;
  reasoning?: string;
  alternatives: Array<{
    type: string;
    blueprintId?: string;
    confidence: number;
  }>;
}
