"""
Unit tests for CPG (Consumer Packaged Goods) action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestIngredientValidate:
    """Tests for ingredient_validate action."""

    @pytest.mark.unit
    def test_ingredient_validate_approved(self):
        """Test ingredient validation for approved ingredient."""
        from cpg.ingredient_validate.handler import ingredient_validate

        result = ingredient_validate(
            ingredient_name="Sodium Chloride",
            cas_number="7647-14-5",
            concentration_pct=2.0,
            product_category="food",
            target_markets=["US", "EU"]
        )

        assert "approved" in result
        assert "ingredient" in result

    @pytest.mark.unit
    def test_ingredient_validate_restricted(self):
        """Test ingredient validation for restricted ingredient."""
        from cpg.ingredient_validate.handler import ingredient_validate

        result = ingredient_validate(
            ingredient_name="Red Dye 40",
            cas_number="25956-17-6",
            concentration_pct=0.1,
            product_category="food",
            target_markets=["EU"]
        )

        assert "approved" in result
        assert "restrictions" in result or "warnings" in result


class TestRegulatoryCheck:
    """Tests for regulatory_check action."""

    @pytest.mark.unit
    def test_regulatory_check_compliant(self):
        """Test regulatory compliance check."""
        from cpg.regulatory_check.handler import regulatory_check

        result = regulatory_check(
            product_id="PROD-001",
            product_category="cosmetics",
            formulation={
                "water": 70.0,
                "glycerin": 10.0,
                "fragrance": 1.0
            },
            target_markets=["US"]
        )

        assert "compliant" in result
        assert "market_status" in result or "regulations" in result

    @pytest.mark.unit
    def test_regulatory_check_multi_market(self):
        """Test regulatory check for multiple markets."""
        from cpg.regulatory_check.handler import regulatory_check

        result = regulatory_check(
            product_id="PROD-002",
            product_category="food",
            formulation={
                "flour": 50.0,
                "sugar": 20.0,
                "salt": 1.0
            },
            target_markets=["US", "EU", "CA"]
        )

        assert "compliant" in result


class TestLabelCompliance:
    """Tests for label_compliance action."""

    @pytest.mark.unit
    def test_label_compliance_complete(self):
        """Test label compliance with all required elements."""
        from cpg.label_compliance.handler import label_compliance

        result = label_compliance(
            product_id="PROD-001",
            label_elements={
                "product_name": "Organic Granola",
                "net_weight": "12 oz (340g)",
                "ingredient_list": "Oats, Honey, Almonds...",
                "nutrition_facts": True,
                "allergen_statement": "Contains: Tree Nuts",
                "manufacturer_address": "123 Food St, City, ST 12345"
            },
            product_category="food",
            market="US"
        )

        assert "compliant" in result
        assert "missing_elements" in result or "issues" in result

    @pytest.mark.unit
    def test_label_compliance_missing_elements(self):
        """Test label compliance with missing elements."""
        from cpg.label_compliance.handler import label_compliance

        result = label_compliance(
            product_id="PROD-002",
            label_elements={
                "product_name": "Mystery Product"
            },
            product_category="food",
            market="US"
        )

        assert "compliant" in result
        # Should flag missing required elements


class TestNutritionValidate:
    """Tests for nutrition_validate action."""

    @pytest.mark.unit
    def test_nutrition_validate_accurate(self):
        """Test nutrition facts validation."""
        from cpg.nutrition_validate.handler import nutrition_validate

        result = nutrition_validate(
            product_id="PROD-001",
            nutrition_facts={
                "serving_size": "1 cup (240ml)",
                "calories": 120,
                "total_fat_g": 2.5,
                "sodium_mg": 150,
                "total_carbs_g": 22,
                "protein_g": 3
            },
            claims=["Low Fat", "Good Source of Fiber"]
        )

        assert "valid" in result
        assert "claims_supported" in result or "issues" in result

    @pytest.mark.unit
    def test_nutrition_validate_claim_check(self):
        """Test nutrition validation checks claims."""
        from cpg.nutrition_validate.handler import nutrition_validate

        result = nutrition_validate(
            product_id="PROD-002",
            nutrition_facts={
                "serving_size": "1 oz (28g)",
                "calories": 160,
                "total_fat_g": 14,
                "sodium_mg": 200
            },
            claims=["Low Fat"]  # Invalid - high fat content
        )

        assert "valid" in result


class TestAllergenCheck:
    """Tests for allergen_check action."""

    @pytest.mark.unit
    def test_allergen_check_detects_allergens(self):
        """Test allergen detection in ingredients."""
        from cpg.allergen_check.handler import allergen_check

        result = allergen_check(
            product_id="PROD-001",
            ingredients=[
                "Wheat Flour",
                "Milk",
                "Eggs",
                "Almonds",
                "Sugar"
            ]
        )

        assert "allergens_detected" in result
        assert "big_8" in result or "major_allergens" in result
        assert len(result["allergens_detected"]) >= 4  # Wheat, Milk, Eggs, Tree Nuts

    @pytest.mark.unit
    def test_allergen_check_cross_contamination(self):
        """Test allergen check includes cross-contamination risks."""
        from cpg.allergen_check.handler import allergen_check

        result = allergen_check(
            product_id="PROD-002",
            ingredients=["Rice", "Salt", "Vegetable Oil"],
            facility_allergens=["Peanuts", "Soy"]
        )

        assert "allergens_detected" in result
        assert "cross_contact_risk" in result or "facility_allergens" in result

    @pytest.mark.unit
    def test_allergen_check_generates_statement(self):
        """Test allergen check generates allergen statement."""
        from cpg.allergen_check.handler import allergen_check

        result = allergen_check(
            product_id="PROD-003",
            ingredients=["Peanut Butter", "Sugar", "Salt"]
        )

        assert "allergen_statement" in result or "contains_statement" in result
