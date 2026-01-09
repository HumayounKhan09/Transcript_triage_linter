"""
Unit tests for escalationEngine.
"""

import pytest
from Data_Classes.reasonCode import reasonCode
from engines.escalationEngine import escalationEngine


def make_reason(code: str, is_escalation: bool, score: int = 2) -> reasonCode:
    return reasonCode(code, is_escalation, score)


@pytest.fixture
def engine():
    return escalationEngine()


# === evaluate_escalation ===


class TestEvaluateEscalation:
    """Tests for escalation evaluation."""

    def test_none_input_raises_type_error(self, engine):
        with pytest.raises(TypeError):
            engine.evaluate_escalation(None)

    def test_empty_list_no_escalation(self, engine):
        result = engine.evaluate_escalation([])
        assert result["escalation_needed"] is False

    def test_empty_list_low_risk(self, engine):
        result = engine.evaluate_escalation([])
        assert result["risk_level"] == "LOW"

    def test_single_trigger_escalation_needed(self, engine):
        reasons = [make_reason("LEGAL_THREAT", True)]
        result = engine.evaluate_escalation(reasons)
        assert result["escalation_needed"] is True

    def test_single_trigger_medium_risk(self, engine):
        reasons = [make_reason("LEGAL_THREAT", True)]
        result = engine.evaluate_escalation(reasons)
        assert result["risk_level"] == "MEDIUM"

    def test_two_triggers_high_risk(self, engine):
        reasons = [
            make_reason("LEGAL_THREAT", True),
            make_reason("BANKRUPTCY_OR_LAWYER", True),
        ]
        result = engine.evaluate_escalation(reasons)
        assert result["risk_level"] == "HIGH"

    def test_three_plus_triggers_still_high_risk(self, engine):
        reasons = [
            make_reason("LEGAL_THREAT", True),
            make_reason("BANKRUPTCY_OR_LAWYER", True),
            make_reason("ABUSIVE_LANGUAGE", True),
        ]
        result = engine.evaluate_escalation(reasons)
        assert result["risk_level"] == "HIGH"

    def test_non_escalation_codes_low_risk(self, engine):
        reasons = [
            make_reason("PAYMENT_INTENT", False),
            make_reason("ESCROW_QUESTION", False),
        ]
        result = engine.evaluate_escalation(reasons)
        assert result["escalation_needed"] is False
        assert result["risk_level"] == "LOW"

    def test_mixed_codes_escalation_determined_by_triggers(self, engine):
        reasons = [
            make_reason("LEGAL_THREAT", True),
            make_reason("PAYMENT_INTENT", False),
        ]
        result = engine.evaluate_escalation(reasons)
        assert result["escalation_needed"] is True
        assert result["risk_level"] == "MEDIUM"


# === Internal Methods ===


class TestInternalMethods:
    """Tests for internal helper methods."""

    def test_count_escalation_reasons(self, engine):
        reasons = [
            make_reason("LEGAL_THREAT", True),
            make_reason("PAYMENT_INTENT", False),
            make_reason("BANKRUPTCY_OR_LAWYER", True),
        ]
        assert engine._count_escalation_reasons(reasons) == 2

    def test_has_escalation_trigger_true(self, engine):
        reasons = [make_reason("LEGAL_THREAT", True)]
        assert engine._has_escalation_trigger(reasons) is True

    def test_has_escalation_trigger_false(self, engine):
        reasons = [make_reason("PAYMENT_INTENT", False)]
        assert engine._has_escalation_trigger(reasons) is False

    def test_calculate_risk_level_thresholds(self, engine):
        assert engine._calculate_risk_level([]) == "LOW"
        assert engine._calculate_risk_level([make_reason("X", True)]) == "MEDIUM"
        assert engine._calculate_risk_level([make_reason("X", True), make_reason("Y", True)]) == "HIGH"
