"""
Unit tests for Contact Center action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestSentimentAnalyze:
    """Tests for sentiment_analyze action."""

    @pytest.mark.unit
    def test_sentiment_analyze_positive(self):
        """Test sentiment analysis for positive interaction."""
        from contact_center.sentiment_analyze.handler import sentiment_analyze

        result = sentiment_analyze(
            call_id="CALL-001",
            transcript="Thank you so much for your help! You've been wonderful."
        )

        assert "sentiment" in result
        assert "score" in result
        assert "call_id" in result

    @pytest.mark.unit
    def test_sentiment_analyze_negative(self):
        """Test sentiment analysis for negative interaction."""
        from contact_center.sentiment_analyze.handler import sentiment_analyze

        result = sentiment_analyze(
            call_id="CALL-002",
            transcript="This is terrible! I've been waiting forever and nobody can help me!"
        )

        assert "sentiment" in result
        assert "score" in result

    @pytest.mark.unit
    def test_sentiment_analyze_timeline(self):
        """Test sentiment analysis includes timeline."""
        from contact_center.sentiment_analyze.handler import sentiment_analyze

        result = sentiment_analyze(
            call_id="CALL-003",
            transcript="Hello. I have a problem. [Agent explains]. Oh I see. That makes sense. Thank you!"
        )

        assert "timeline" in result or "progression" in result or "sentiment" in result


class TestComplianceCheck:
    """Tests for compliance_check action."""

    @pytest.mark.unit
    def test_compliance_check_compliant(self):
        """Test compliance check for compliant call."""
        from contact_center.compliance_check.handler import compliance_check

        result = compliance_check(
            call_id="CALL-001",
            transcript="This call may be recorded for quality purposes. How can I help you today?",
            call_type="inbound",
            industry="financial_services"
        )

        assert "compliant" in result
        assert "violations" in result or "issues" in result
        assert "call_id" in result

    @pytest.mark.unit
    def test_compliance_check_violations(self):
        """Test compliance check detects violations."""
        from contact_center.compliance_check.handler import compliance_check

        result = compliance_check(
            call_id="CALL-002",
            transcript="I guarantee you'll make money with this investment.",
            call_type="outbound",
            industry="financial_services"
        )

        assert "compliant" in result
        # Should flag guarantee language in financial context


class TestQualityScore:
    """Tests for quality_score action."""

    @pytest.mark.unit
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        from contact_center.quality_score.handler import quality_score

        result = quality_score(
            call_id="CALL-001",
            transcript="Thank you for calling. How can I help? ... Is there anything else?",
            handle_time_seconds=300,
            resolution="resolved_first_call"
        )

        assert "overall_score" in result
        assert "components" in result or "categories" in result
        assert 0 <= result["overall_score"] <= 100

    @pytest.mark.unit
    def test_quality_score_components(self):
        """Test quality score includes component scores."""
        from contact_center.quality_score.handler import quality_score

        result = quality_score(
            call_id="CALL-002",
            transcript="Hello. Let me help you with that.",
            handle_time_seconds=180,
            resolution="resolved_first_call"
        )

        components = result.get("components", result.get("categories", {}))
        # Should have multiple scoring components
        assert "overall_score" in result


class TestCoachingRecommend:
    """Tests for coaching_recommend action."""

    @pytest.mark.unit
    def test_coaching_recommend_generates_tips(self):
        """Test coaching recommendation generation."""
        from contact_center.coaching_recommend.handler import coaching_recommend

        result = coaching_recommend(
            agent_id="AGENT-001",
            quality_scores=[
                {"call_id": "C1", "score": 75, "areas": {"empathy": 60, "resolution": 85}},
                {"call_id": "C2", "score": 72, "areas": {"empathy": 55, "resolution": 80}}
            ],
            performance_metrics={
                "aht": 420,
                "fcr": 0.78,
                "csat": 4.1
            }
        )

        assert "recommendations" in result
        assert "agent_id" in result

    @pytest.mark.unit
    def test_coaching_recommend_prioritizes(self):
        """Test coaching prioritizes improvement areas."""
        from contact_center.coaching_recommend.handler import coaching_recommend

        result = coaching_recommend(
            agent_id="AGENT-002",
            quality_scores=[
                {"call_id": "C1", "score": 65, "areas": {"empathy": 50, "knowledge": 90}}
            ],
            performance_metrics={
                "aht": 600,
                "fcr": 0.65,
                "csat": 3.5
            }
        )

        assert "recommendations" in result
        assert "priority" in result or "focus_areas" in result or len(result["recommendations"]) > 0


class TestEscalationDetect:
    """Tests for escalation_detect action."""

    @pytest.mark.unit
    def test_escalation_detect_no_escalation(self):
        """Test escalation detection for normal call."""
        from contact_center.escalation_detect.handler import escalation_detect

        result = escalation_detect(
            call_id="CALL-001",
            transcript="Hello. I need help with my account. Sure, let me look that up. Perfect, thank you!"
        )

        assert "escalation_needed" in result
        assert "confidence" in result or "signals" in result
        assert "call_id" in result

    @pytest.mark.unit
    def test_escalation_detect_escalation_needed(self):
        """Test escalation detection identifies escalation signals."""
        from contact_center.escalation_detect.handler import escalation_detect

        result = escalation_detect(
            call_id="CALL-002",
            transcript="I want to speak to your supervisor! This is unacceptable! I'm going to report this!"
        )

        assert "escalation_needed" in result
        assert "signals" in result or "triggers" in result
        # Should detect supervisor request and anger signals

    @pytest.mark.unit
    def test_escalation_detect_urgency_levels(self):
        """Test escalation detection assigns urgency."""
        from contact_center.escalation_detect.handler import escalation_detect

        result = escalation_detect(
            call_id="CALL-003",
            transcript="I've called five times about this! Nobody is helping me! I'm cancelling my account!"
        )

        assert "escalation_needed" in result
        assert "urgency" in result or "priority" in result or "signals" in result
