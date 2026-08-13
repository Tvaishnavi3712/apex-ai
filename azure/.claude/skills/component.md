# Skill: Create React Component

When asked to create a new frontend component:

## Component Structure
```tsx
/**
 * {ComponentName} - {Brief description}
 */

import React, { useState, useCallback } from 'react';
import { Card, CardHeader, Button, Badge } from '@/components/common';
import {
  // Import relevant Heroicons
} from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface {ComponentName}Props {
  // Define props with types
}

export const {ComponentName}: React.FC<{ComponentName}Props> = ({
  // Destructure props
}) => {
  // State hooks
  const [state, setState] = useState<Type>(initialValue);

  // Callbacks
  const handleAction = useCallback(() => {
    // Handler logic
  }, [dependencies]);

  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  );
};

export default {ComponentName};
```

## Location
Save components to: `frontend/src/components/{Category}/{ComponentName}.tsx`

## Categories
- `common/` - Reusable UI components (Button, Card, Badge, Modal, Input)
- `BlueprintDesigner/` - Blueprint creation components
- `RunbookBuilder/` - Runbook creation components
- `WorkRoom/` - Agent chat and work queue
- `ControlRoom/` - Monitoring and metrics
- `Layout/` - Sidebar, header, layout wrapper

## Common Imports
```tsx
import { Card, CardHeader, Button, Badge, StatusBadge } from '@/components/common';
import { Modal } from '@/components/common/Modal';
import { Input, TextArea, Select } from '@/components/common/Input';
```

## Heroicons Usage
```tsx
import {
  PlusIcon,
  TrashIcon,
  PencilSquareIcon,
  PlayIcon,
  StopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  CpuChipIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
```

## Styling
- Use Tailwind CSS classes
- Use `clsx` for conditional classes
- Follow existing color scheme:
  - Primary: `apex-500`, `apex-600`
  - Success: `green-500`, `green-600`
  - Warning: `yellow-500`, `amber-500`
  - Danger: `red-500`, `red-600`
  - Neutral: `gray-100` to `gray-900`

## State Management
```tsx
import { useApexStore } from '@/lib/store';

// In component
const { items, addItem, updateItem } = useApexStore();
```
