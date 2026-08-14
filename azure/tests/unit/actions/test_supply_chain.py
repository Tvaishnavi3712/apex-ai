"""
Unit tests for Supply Chain action handlers.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestForecastAnalyze:
    """Tests for forecast_analyze action."""

    @pytest.mark.unit
    def test_forecast_analyze_returns_metrics(self):
        """Test forecast analysis returns forecast metrics."""
        from supply_chain.forecast_analyze.handler import forecast_analyze

        result = forecast_analyze(
            product_id="SKU-001",
            forecast_period="2024-Q1",
            historical_periods=12
        )

        assert "forecast" in result
        assert "confidence_interval" in result or "accuracy" in result
        assert "product_id" in result

    @pytest.mark.unit
    def test_forecast_analyze_includes_trends(self):
        """Test forecast analysis includes trend data."""
        from supply_chain.forecast_analyze.handler import forecast_analyze

        result = forecast_analyze(
            product_id="SKU-002",
            forecast_period="2024-Q2",
            historical_periods=24
        )

        assert "trend" in result or "seasonality" in result


class TestInventoryAnalyze:
    """Tests for inventory_analyze action."""

    @pytest.mark.unit
    def test_inventory_analyze_returns_status(self):
        """Test inventory analysis returns status metrics."""
        from supply_chain.inventory_analyze.handler import inventory_analyze

        result = inventory_analyze(
            product_id="SKU-001",
            location_id="WH-001"
        )

        assert "current_stock" in result
        assert "status" in result
        assert "product_id" in result

    @pytest.mark.unit
    def test_inventory_analyze_includes_recommendations(self):
        """Test inventory analysis includes action recommendations."""
        from supply_chain.inventory_analyze.handler import inventory_analyze

        result = inventory_analyze(
            product_id="SKU-002",
            location_id="WH-002"
        )

        assert "recommendation" in result or "action" in result or "status" in result


class TestEOQCalculate:
    """Tests for eoq_calculate action."""

    @pytest.mark.unit
    def test_eoq_calculate_basic(self):
        """Test EOQ calculation returns order quantity."""
        from supply_chain.eoq_calculate.handler import eoq_calculate

        result = eoq_calculate(
            product_id="SKU-001",
            annual_demand=10000,
            ordering_cost=50.00,
            holding_cost_rate=0.25,
            unit_cost=10.00
        )

        assert "eoq" in result
        assert "annual_orders" in result
        assert "total_cost" in result
        assert result["eoq"] > 0

    @pytest.mark.unit
    def test_eoq_calculate_formula_accuracy(self):
        """Test EOQ calculation follows Wilson formula."""
        from supply_chain.eoq_calculate.handler import eoq_calculate

        result = eoq_calculate(
            product_id="SKU-002",
            annual_demand=1000,
            ordering_cost=100.00,
            holding_cost_rate=0.20,
            unit_cost=50.00
        )

        # EOQ = sqrt(2 * D * S / H)
        # D=1000, S=100, H=0.20*50=10
        # EOQ = sqrt(200000/10) = sqrt(20000) ≈ 141
        assert "eoq" in result
        assert 100 < result["eoq"] < 200


class TestReorderPoint:
    """Tests for reorder_point action."""

    @pytest.mark.unit
    def test_reorder_point_calculation(self):
        """Test reorder point calculation."""
        from supply_chain.reorder_point.handler import reorder_point

        result = reorder_point(
            product_id="SKU-001",
            lead_time_days=14,
            daily_demand=100,
            service_level=0.95
        )

        assert "reorder_point" in result
        assert "safety_stock" in result
        assert result["reorder_point"] > 0

    @pytest.mark.unit
    def test_reorder_point_includes_safety_stock(self):
        """Test reorder point includes safety stock calculation."""
        from supply_chain.reorder_point.handler import reorder_point

        result = reorder_point(
            product_id="SKU-002",
            lead_time_days=7,
            daily_demand=50,
            service_level=0.99,
            demand_std_dev=10
        )

        assert "safety_stock" in result
        # Higher service level should have higher safety stock
        assert result["safety_stock"] > 0


class TestQualityMetrics:
    """Tests for quality_metrics action."""

    @pytest.mark.unit
    def test_quality_metrics_returns_scores(self):
        """Test quality metrics returns performance scores."""
        from supply_chain.quality_metrics.handler import quality_metrics

        result = quality_metrics(
            vendor_id="VEND-001",
            start_date="2024-01-01",
            end_date="2024-03-31"
        )

        assert "incoming_quality_pct" in result
        assert "ppm_defects" in result
        assert "vendor_id" in result

    @pytest.mark.unit
    def test_quality_metrics_includes_cars(self):
        """Test quality metrics includes corrective action data."""
        from supply_chain.quality_metrics.handler import quality_metrics

        result = quality_metrics(
            vendor_id="VEND-002",
            start_date="2024-01-01",
            end_date="2024-06-30"
        )

        assert "open_cars" in result or "car_closure_pct" in result


class TestDeliveryMetrics:
    """Tests for delivery_metrics action."""

    @pytest.mark.unit
    def test_delivery_metrics_returns_rates(self):
        """Test delivery metrics returns performance rates."""
        from supply_chain.delivery_metrics.handler import delivery_metrics

        result = delivery_metrics(
            vendor_id="VEND-001",
            start_date="2024-01-01",
            end_date="2024-03-31"
        )

        assert "on_time_delivery_pct" in result
        assert "complete_shipment_pct" in result
        assert "vendor_id" in result

    @pytest.mark.unit
    def test_delivery_metrics_includes_lead_time(self):
        """Test delivery metrics includes lead time analysis."""
        from supply_chain.delivery_metrics.handler import delivery_metrics

        result = delivery_metrics(
            vendor_id="VEND-002",
            start_date="2024-01-01",
            end_date="2024-06-30"
        )

        assert "avg_lead_time_days" in result


class TestScorecardGenerate:
    """Tests for scorecard_generate action."""

    @pytest.mark.unit
    def test_scorecard_generate_returns_score(self):
        """Test scorecard generation returns overall score."""
        from supply_chain.scorecard_generate.handler import scorecard_generate

        result = scorecard_generate(
            vendor_id="VEND-001",
            period="2024-Q1",
            delivery_metrics={
                "on_time_delivery_pct": 95,
                "complete_shipment_pct": 98,
                "documentation_accuracy_pct": 99
            },
            quality_metrics={
                "incoming_quality_pct": 99,
                "ppm_defects": 500,
                "car_closure_pct": 85
            }
        )

        assert "overall_score" in result
        assert "rating" in result
        assert "vendor_id" in result
        assert 0 <= result["overall_score"] <= 100

    @pytest.mark.unit
    def test_scorecard_generate_includes_categories(self):
        """Test scorecard includes category scores."""
        from supply_chain.scorecard_generate.handler import scorecard_generate

        result = scorecard_generate(
            vendor_id="VEND-002",
            period="2024-Q2",
            delivery_metrics={
                "on_time_delivery_pct": 90,
                "complete_shipment_pct": 95,
                "documentation_accuracy_pct": 97
            },
            quality_metrics={
                "incoming_quality_pct": 97,
                "ppm_defects": 1000,
                "car_closure_pct": 80
            }
        )

        assert "category_scores" in result
        assert "delivery" in result["category_scores"]
        assert "quality" in result["category_scores"]

    @pytest.mark.unit
    def test_scorecard_generate_rating_levels(self):
        """Test scorecard generates appropriate ratings."""
        from supply_chain.scorecard_generate.handler import scorecard_generate

        # Test excellent rating
        result = scorecard_generate(
            vendor_id="VEND-003",
            period="2024-Q3",
            delivery_metrics={
                "on_time_delivery_pct": 99,
                "complete_shipment_pct": 99,
                "documentation_accuracy_pct": 99
            },
            quality_metrics={
                "incoming_quality_pct": 99.5,
                "ppm_defects": 100,
                "car_closure_pct": 95
            }
        )

        assert result["rating"] in ["excellent", "good", "acceptable", "needs_improvement", "critical"]
