import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BlueprintDesigner } from '../BlueprintDesigner';
import { Blueprint } from '../types';

// Mock uuid
jest.mock('uuid', () => ({
  v4: jest.fn(() => 'test-uuid-123'),
}));

describe('BlueprintDesigner Component', () => {
  const mockOnSave = jest.fn();
  const mockOnDeploy = jest.fn();
  const mockOnTest = jest.fn();

  const defaultProps = {
    onSave: mockOnSave,
    onDeploy: mockOnDeploy,
    onTest: mockOnTest,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('renders with empty state', () => {
      render(<BlueprintDesigner {...defaultProps} />);

      expect(screen.getByPlaceholderText('Blueprint Name')).toBeInTheDocument();
      expect(screen.getByText('Definition')).toBeInTheDocument();
      expect(screen.getByText('Fields')).toBeInTheDocument();
      expect(screen.getByText('Rules')).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });

    it('renders with initial data', () => {
      const initialData: Partial<Blueprint> = {
        name: 'Test Blueprint',
        description: 'Test description',
        documentType: 'invoice',
        industry: 'financial_services',
        stage: 'DEVELOPMENT',
        fields: [],
      };

      render(<BlueprintDesigner {...defaultProps} initialData={initialData} />);

      expect(screen.getByDisplayValue('Test Blueprint')).toBeInTheDocument();
    });

    it('shows DEVELOPMENT stage badge by default', () => {
      render(<BlueprintDesigner {...defaultProps} />);
      expect(screen.getByText('DEVELOPMENT')).toBeInTheDocument();
    });

    it('shows LIVE stage badge when blueprint is live', () => {
      render(
        <BlueprintDesigner
          {...defaultProps}
          initialData={{ stage: 'LIVE' }}
        />
      );
      expect(screen.getByText('LIVE')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('switches to Fields tab', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const fieldsTab = screen.getByText('Fields');
      await userEvent.click(fieldsTab);

      expect(screen.getByText('Extraction Fields')).toBeInTheDocument();
    });

    it('switches to Rules tab', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const rulesTab = screen.getByText('Rules');
      await userEvent.click(rulesTab);

      expect(screen.getByText('Validation Rules')).toBeInTheDocument();
    });

    it('switches to Preview tab', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const previewTab = screen.getByText('Preview');
      await userEvent.click(previewTab);

      expect(screen.getByText('BDA Schema Preview')).toBeInTheDocument();
    });
  });

  describe('Definition Tab', () => {
    it('allows entering blueprint name', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText('Blueprint Name');
      await userEvent.type(nameInput, 'My Invoice Blueprint');

      expect(nameInput).toHaveValue('My Invoice Blueprint');
    });

    it('allows entering description', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const descInput = screen.getByPlaceholderText(/Describe what this blueprint/);
      await userEvent.type(descInput, 'Extracts invoice data');

      expect(descInput).toHaveValue('Extracts invoice data');
    });

    it('allows selecting document type', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const docTypeSelect = screen.getByLabelText('Document Type');
      await userEvent.selectOptions(docTypeSelect, 'receipt');

      expect(docTypeSelect).toHaveValue('receipt');
    });

    it('allows selecting industry', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const industrySelect = screen.getByLabelText('Industry');
      await userEvent.selectOptions(industrySelect, 'manufacturing');

      expect(industrySelect).toHaveValue('manufacturing');
    });

    it('renders quick start templates', () => {
      render(<BlueprintDesigner {...defaultProps} />);

      expect(screen.getByText('Quick Start Templates')).toBeInTheDocument();
      expect(screen.getByText('Invoice')).toBeInTheDocument();
      expect(screen.getByText('Receipt')).toBeInTheDocument();
      expect(screen.getByText('Purchase Order')).toBeInTheDocument();
    });
  });

  describe('Save and Deploy Actions', () => {
    it('calls onSave when Save Draft is clicked', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText('Blueprint Name');
      await userEvent.type(nameInput, 'Test Blueprint');

      const saveButton = screen.getByText('Save Draft');
      await userEvent.click(saveButton);

      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Blueprint',
        })
      );
    });

    it('disables Deploy button when blueprint is invalid', () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const deployButton = screen.getByText('Deploy to BDA');
      expect(deployButton).toBeDisabled();
    });

    it('enables Deploy button when blueprint has name and fields', async () => {
      const validBlueprint: Partial<Blueprint> = {
        name: 'Valid Blueprint',
        fields: [
          {
            id: '1',
            name: 'invoice_number',
            type: 'string',
            inferenceType: 'explicit',
            instruction: 'Extract invoice number',
            required: true,
          },
        ],
      };

      render(<BlueprintDesigner {...defaultProps} initialData={validBlueprint} />);

      const deployButton = screen.getByText('Deploy to BDA');
      expect(deployButton).not.toBeDisabled();
    });

    it('shows loading state when isLoading is true', () => {
      render(<BlueprintDesigner {...defaultProps} isLoading={true} />);

      const saveButton = screen.getByText('Save Draft').closest('button');
      expect(saveButton).toHaveAttribute('disabled');
    });
  });

  describe('Unsaved Changes', () => {
    it('shows unsaved changes badge when blueprint is modified', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText('Blueprint Name');
      await userEvent.type(nameInput, 'New Name');

      expect(screen.getByText('Unsaved changes')).toBeInTheDocument();
    });

    it('hides unsaved changes badge after saving', async () => {
      render(<BlueprintDesigner {...defaultProps} />);

      const nameInput = screen.getByPlaceholderText('Blueprint Name');
      await userEvent.type(nameInput, 'New Name');

      const saveButton = screen.getByText('Save Draft');
      await userEvent.click(saveButton);

      expect(screen.queryByText('Unsaved changes')).not.toBeInTheDocument();
    });
  });

  describe('Test Modal', () => {
    it('opens test modal when Test button is clicked', async () => {
      const validBlueprint: Partial<Blueprint> = {
        name: 'Test Blueprint',
        fields: [
          {
            id: '1',
            name: 'field1',
            type: 'string',
            inferenceType: 'explicit',
            instruction: 'Test',
            required: false,
          },
        ],
      };

      render(<BlueprintDesigner {...defaultProps} initialData={validBlueprint} />);

      const testButton = screen.getByText('Test');
      await userEvent.click(testButton);

      expect(screen.getByText('Test Blueprint')).toBeInTheDocument();
      expect(screen.getByLabelText('Document S3 URI')).toBeInTheDocument();
    });

    it('closes test modal when Cancel is clicked', async () => {
      const validBlueprint: Partial<Blueprint> = {
        name: 'Test Blueprint',
        fields: [{ id: '1', name: 'f', type: 'string', inferenceType: 'explicit', instruction: '', required: false }],
      };

      render(<BlueprintDesigner {...defaultProps} initialData={validBlueprint} />);

      await userEvent.click(screen.getByText('Test'));
      await userEvent.click(screen.getByText('Cancel'));

      expect(screen.queryByLabelText('Document S3 URI')).not.toBeInTheDocument();
    });

    it('calls onTest with document URI when Run Test is clicked', async () => {
      const validBlueprint: Partial<Blueprint> = {
        name: 'Test Blueprint',
        fields: [{ id: '1', name: 'f', type: 'string', inferenceType: 'explicit', instruction: '', required: false }],
      };

      render(<BlueprintDesigner {...defaultProps} initialData={validBlueprint} />);

      await userEvent.click(screen.getByText('Test'));

      const uriInput = screen.getByLabelText('Document S3 URI');
      await userEvent.type(uriInput, 's3://bucket/doc.pdf');

      await userEvent.click(screen.getByText('Run Test'));

      expect(mockOnTest).toHaveBeenCalledWith(
        expect.objectContaining({ name: 'Test Blueprint' }),
        's3://bucket/doc.pdf'
      );
    });
  });
});

describe('FieldList Integration', () => {
  it('shows field count badge in Fields tab', async () => {
    const blueprintWithFields: Partial<Blueprint> = {
      name: 'Test',
      fields: [
        { id: '1', name: 'field1', type: 'string', inferenceType: 'explicit', instruction: '', required: false },
        { id: '2', name: 'field2', type: 'number', inferenceType: 'explicit', instruction: '', required: false },
      ],
    };

    render(<BlueprintDesigner onSave={jest.fn()} initialData={blueprintWithFields} />);

    const fieldsTab = screen.getByText('Fields').closest('button');
    expect(within(fieldsTab!).getByText('2')).toBeInTheDocument();
  });
});

describe('BlueprintPreview Integration', () => {
  it('generates correct schema preview', async () => {
    const blueprint: Partial<Blueprint> = {
      name: 'InvoiceBlueprint',
      description: 'Test description',
      fields: [
        {
          id: '1',
          name: 'invoice_number',
          type: 'string',
          inferenceType: 'explicit',
          instruction: 'Extract invoice number',
          required: true,
        },
      ],
    };

    render(<BlueprintDesigner onSave={jest.fn()} initialData={blueprint} />);

    await userEvent.click(screen.getByText('Preview'));

    expect(screen.getByText(/InvoiceBlueprint/)).toBeInTheDocument();
    expect(screen.getByText(/invoice_number/)).toBeInTheDocument();
  });

  it('shows schema stats', async () => {
    const blueprint: Partial<Blueprint> = {
      name: 'Test',
      fields: [
        { id: '1', name: 'f1', type: 'string', inferenceType: 'explicit', instruction: '', required: true },
        { id: '2', name: 'f2', type: 'number', inferenceType: 'explicit', instruction: '', required: false },
      ],
      definitions: [],
    };

    render(<BlueprintDesigner onSave={jest.fn()} initialData={blueprint} />);

    await userEvent.click(screen.getByText('Preview'));

    expect(screen.getByText('Fields')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
