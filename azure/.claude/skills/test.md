# Skill: Create Tests

When asked to create tests:

## Python Unit Test (pytest)
```python
"""
Tests for {module_name}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the module being tested
from {module_path} import {function_or_class}


class Test{ClassName}:
    """Test suite for {ClassName}"""

    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample test data"""
        return {
            "field": "value"
        }

    @pytest.mark.unit
    def test_{function_name}_success(self, sample_data):
        """Test {function_name} with valid input"""
        result = {function_name}(**sample_data)

        assert result is not None
        assert "expected_field" in result
        assert result["status"] == "success"

    @pytest.mark.unit
    def test_{function_name}_failure(self):
        """Test {function_name} with invalid input"""
        with pytest.raises(ValueError):
            {function_name}(invalid_param="bad")

    @pytest.mark.unit
    @patch('{module_path}.external_dependency')
    def test_{function_name}_with_mock(self, mock_dep, sample_data):
        """Test {function_name} with mocked dependency"""
        mock_dep.return_value = {"mocked": "response"}

        result = {function_name}(**sample_data)

        mock_dep.assert_called_once()
        assert result["status"] == "success"
```

## Location
- Unit tests: `tests/unit/{category}/test_{module}.py`
- API tests: `tests/api/test_{router}.py`
- Integration tests: `tests/integration/test_{feature}.py`

## API Test (FastAPI TestClient)
```python
"""
API tests for {router_name}
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)


class TestApi{Resource}:
    """API tests for {resource} endpoints"""

    @pytest.fixture
    def sample_{resource}(self):
        return {
            "id": "test-123",
            "name": "Test Resource"
        }

    @pytest.mark.api
    def test_list_{resources}(self):
        """Test GET /{resources}"""
        response = client.get("/api/v1/{resources}")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.api
    def test_create_{resource}(self, sample_{resource}):
        """Test POST /{resources}"""
        response = client.post(
            "/api/v1/{resources}",
            json=sample_{resource}
        )

        assert response.status_code == 201
        assert response.json()["id"] is not None

    @pytest.mark.api
    def test_get_{resource}(self):
        """Test GET /{resources}/{id}"""
        response = client.get("/api/v1/{resources}/test-123")

        assert response.status_code in [200, 404]
```

## Integration Test
```python
"""
Integration tests for {feature}
"""

import pytest
import os
import json
from pathlib import Path


class Test{Feature}Integration:
    """Integration tests for {feature}"""

    @pytest.fixture
    def {feature}_files(self):
        """Get all {feature} files"""
        base_path = Path(__file__).parent.parent.parent / "{feature_path}"
        return list(base_path.rglob("*.{ext}"))

    @pytest.mark.integration
    def test_all_{features}_valid(self, {feature}_files):
        """Validate all {feature} files"""
        for file_path in {feature}_files:
            with open(file_path) as f:
                data = json.load(f)  # or yaml.safe_load(f)

            assert "required_field" in data
            assert data["required_field"] is not None
```

## Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# Specific category
pytest tests/unit/ -v
pytest tests/api/ -v
pytest tests/integration/ -v

# By marker
pytest -m unit
pytest -m api
pytest -m integration
```
