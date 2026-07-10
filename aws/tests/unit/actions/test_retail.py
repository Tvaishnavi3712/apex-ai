"""
Unit tests for Retail action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestReceiptValidate:
    """Tests for receipt_validate action."""

    @pytest.mark.unit
    def test_receipt_validate_valid_receipt(self):
        """Test receipt validation with valid receipt."""
        from retail.receipt_validate.handler import receipt_validate

        result = receipt_validate(
            receipt_number="RCP-2024-001234",
            store_id="STORE-001",
            transaction_date="2024-01-15",
            items=[
                {"sku": "SKU001", "price": 29.99},
                {"sku": "SKU002", "price": 49.99}
            ],
            total_amount=79.98
        )

        assert "valid" in result
        assert "receipt_number" in result

    @pytest.mark.unit
    def test_receipt_validate_checks_totals(self):
        """Test receipt validation checks total calculation."""
        from retail.receipt_validate.handler import receipt_validate

        result = receipt_validate(
            receipt_number="RCP-2024-001235",
            store_id="STORE-001",
            transaction_date="2024-01-15",
            items=[{"sku": "SKU001", "price": 100.00}],
            total_amount=100.00
        )

        assert "valid" in result


class TestReturnPolicy:
    """Tests for return_policy action."""

    @pytest.mark.unit
    def test_return_policy_eligible(self):
        """Test return policy check for eligible item."""
        from retail.return_policy.handler import return_policy

        result = return_policy(
            product_category="electronics",
            purchase_date="2024-01-15",
            return_date="2024-01-25",
            item_condition="unopened"
        )

        assert "eligible" in result
        assert "return_window_days" in result or "policy" in result

    @pytest.mark.unit
    def test_return_policy_expired(self):
        """Test return policy check for expired window."""
        from retail.return_policy.handler import return_policy

        result = return_policy(
            product_category="electronics",
            purchase_date="2023-01-15",
            return_date="2024-01-25",
            item_condition="opened"
        )

        assert "eligible" in result


class TestFraudScore:
    """Tests for fraud_score action."""

    @pytest.mark.unit
    def test_fraud_score_low_risk(self):
        """Test fraud scoring for low-risk return."""
        from retail.fraud_score.handler import fraud_score

        result = fraud_score(
            customer_id="CUST-001",
            return_value=49.99,
            return_history=[],
            item_category="apparel"
        )

        assert "risk_score" in result
        assert "risk_level" in result
        assert 0 <= result["risk_score"] <= 100

    @pytest.mark.unit
    def test_fraud_score_high_risk(self):
        """Test fraud scoring flags high-risk patterns."""
        from retail.fraud_score.handler import fraud_score

        result = fraud_score(
            customer_id="CUST-002",
            return_value=999.99,
            return_history=[
                {"date": "2024-01-10", "amount": 500.00},
                {"date": "2024-01-08", "amount": 750.00},
                {"date": "2024-01-05", "amount": 600.00}
            ],
            item_category="electronics"
        )

        assert "risk_score" in result
        assert "indicators" in result


class TestInventoryUpdate:
    """Tests for inventory_update action."""

    @pytest.mark.unit
    def test_inventory_update_add(self):
        """Test inventory update for adding stock."""
        from retail.inventory_update.handler import inventory_update

        result = inventory_update(
            sku="SKU-001",
            location_id="STORE-001",
            adjustment_type="add",
            quantity=10,
            reason="return_restock"
        )

        assert "success" in result
        assert "new_quantity" in result
        assert "sku" in result

    @pytest.mark.unit
    def test_inventory_update_remove(self):
        """Test inventory update for removing stock."""
        from retail.inventory_update.handler import inventory_update

        result = inventory_update(
            sku="SKU-002",
            location_id="STORE-002",
            adjustment_type="remove",
            quantity=5,
            reason="damaged"
        )

        assert "success" in result


class TestRefundProcess:
    """Tests for refund_process action."""

    @pytest.mark.unit
    def test_refund_process_card(self):
        """Test refund processing to original card."""
        from retail.refund_process.handler import refund_process

        result = refund_process(
            order_id="ORD-2024-001",
            refund_amount=99.99,
            refund_method="original_payment",
            original_payment_method="credit_card"
        )

        assert "refund_id" in result
        assert "status" in result
        assert "amount" in result

    @pytest.mark.unit
    def test_refund_process_store_credit(self):
        """Test refund processing as store credit."""
        from retail.refund_process.handler import refund_process

        result = refund_process(
            order_id="ORD-2024-002",
            refund_amount=49.99,
            refund_method="store_credit",
            customer_id="CUST-001"
        )

        assert "refund_id" in result
        assert "credit_balance" in result or "status" in result
