import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardFooter } from '../Card';

describe('Card Component', () => {
  describe('Basic Rendering', () => {
    it('renders card with children', () => {
      render(<Card>Card content</Card>);
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('renders with default styling', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow-sm');
    });
  });

  describe('Padding Options', () => {
    it('renders with no padding when padding is none', () => {
      render(<Card padding="none" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).not.toHaveClass('p-4', 'p-6');
    });

    it('renders with small padding', () => {
      render(<Card padding="sm" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-4');
    });

    it('renders with medium padding by default', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-6');
    });

    it('renders with large padding', () => {
      render(<Card padding="lg" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('p-8');
    });
  });

  describe('Hover Effects', () => {
    it('applies hover styles when hover is true', () => {
      render(<Card hover data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('hover:shadow-md', 'transition-shadow');
    });

    it('does not apply hover styles by default', () => {
      render(<Card data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).not.toHaveClass('hover:shadow-md');
    });
  });

  describe('Custom Styles', () => {
    it('accepts additional className', () => {
      render(<Card className="custom-class" data-testid="card">Content</Card>);
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-class');
    });
  });
});

describe('CardHeader Component', () => {
  it('renders header with title', () => {
    render(<CardHeader title="Header Title" />);
    expect(screen.getByText('Header Title')).toBeInTheDocument();
  });

  it('renders header with subtitle', () => {
    render(<CardHeader title="Title" subtitle="Subtitle text" />);
    expect(screen.getByText('Subtitle text')).toBeInTheDocument();
  });

  it('renders header with action element', () => {
    render(
      <CardHeader
        title="Title"
        action={<button>Action</button>}
      />
    );
    expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
  });

  it('applies correct header styling', () => {
    render(<CardHeader title="Title" data-testid="header" />);
    const header = screen.getByTestId('header');
    expect(header).toHaveClass('border-b');
  });
});

describe('CardFooter Component', () => {
  it('renders footer with children', () => {
    render(<CardFooter>Footer content</CardFooter>);
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  it('applies correct footer styling', () => {
    render(<CardFooter data-testid="footer">Content</CardFooter>);
    const footer = screen.getByTestId('footer');
    expect(footer).toHaveClass('border-t');
  });
});

describe('Card Composition', () => {
  it('renders complete card with header, body, and footer', () => {
    render(
      <Card>
        <CardHeader title="Card Title" subtitle="Card subtitle" />
        <div>Main content</div>
        <CardFooter>
          <button>Save</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card subtitle')).toBeInTheDocument();
    expect(screen.getByText('Main content')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });
});
