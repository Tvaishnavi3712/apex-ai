import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge, StatusBadge } from '../Badge';

describe('Badge Component', () => {
  describe('Basic Rendering', () => {
    it('renders badge with text', () => {
      render(<Badge>Label</Badge>);
      expect(screen.getByText('Label')).toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('renders default variant', () => {
      render(<Badge variant="default" data-testid="badge">Default</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-gray-100', 'text-gray-800');
    });

    it('renders success variant', () => {
      render(<Badge variant="success" data-testid="badge">Success</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-green-100', 'text-green-800');
    });

    it('renders warning variant', () => {
      render(<Badge variant="warning" data-testid="badge">Warning</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');
    });

    it('renders danger variant', () => {
      render(<Badge variant="danger" data-testid="badge">Danger</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-red-100', 'text-red-800');
    });

    it('renders info variant', () => {
      render(<Badge variant="info" data-testid="badge">Info</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
    });

    it('renders purple variant', () => {
      render(<Badge variant="purple" data-testid="badge">Purple</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-purple-100', 'text-purple-800');
    });
  });

  describe('Dot Indicator', () => {
    it('shows dot when dot prop is true', () => {
      render(<Badge dot data-testid="badge">With Dot</Badge>);
      const badge = screen.getByTestId('badge');
      const dot = badge.querySelector('span.rounded-full');
      expect(dot).toBeInTheDocument();
    });

    it('does not show dot by default', () => {
      render(<Badge data-testid="badge">No Dot</Badge>);
      const badge = screen.getByTestId('badge');
      const dot = badge.querySelector('span.rounded-full.w-2');
      expect(dot).not.toBeInTheDocument();
    });
  });

  describe('Custom Styles', () => {
    it('accepts additional className', () => {
      render(<Badge className="custom-class" data-testid="badge">Custom</Badge>);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('custom-class');
    });
  });
});

describe('StatusBadge Component', () => {
  describe('Status Mappings', () => {
    it('renders active status with success variant', () => {
      render(<StatusBadge status="active" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-green-100');
      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('renders pending status with warning variant', () => {
      render(<StatusBadge status="pending" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-yellow-100');
      expect(screen.getByText('Pending')).toBeInTheDocument();
    });

    it('renders failed status with danger variant', () => {
      render(<StatusBadge status="failed" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-red-100');
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });

    it('renders draft status with default variant', () => {
      render(<StatusBadge status="draft" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-gray-100');
      expect(screen.getByText('Draft')).toBeInTheDocument();
    });

    it('renders completed status with success variant', () => {
      render(<StatusBadge status="completed" data-testid="badge" />);
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    it('renders running status with info variant', () => {
      render(<StatusBadge status="running" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-blue-100');
      expect(screen.getByText('Running')).toBeInTheDocument();
    });

    it('renders archived status correctly', () => {
      render(<StatusBadge status="archived" data-testid="badge" />);
      expect(screen.getByText('Archived')).toBeInTheDocument();
    });
  });

  describe('Unknown Status', () => {
    it('renders unknown status with default variant', () => {
      render(<StatusBadge status="unknown_status" data-testid="badge" />);
      const badge = screen.getByTestId('badge');
      expect(badge).toHaveClass('bg-gray-100');
    });
  });
});
