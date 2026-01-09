"""
Unit tests for intentClassifier.
"""

import pytest
from Data_Classes.reasonCode import reasonCode
from engines.intentClassifier import intentClassifier


def make_reason(code: str, score: int) -> reasonCode:
    return reasonCode(code, False, score)


@pytest.fixture
def classifier():
    return intentClassifier()


def classify(codes):
    return intentClassifier().classify(codes)


# === Basic Classification ===


class TestBasicClassification:
    """Tests for basic intent classification."""

    def test_none_input_raises_type_error(self, classifier):
        with pytest.raises(TypeError):
            classifier.classify(None)

    def test_invalid_object_raises_attribute_error(self, classifier):
        with pytest.raises(AttributeError):
            classifier.classify([{"code": "PAYMENT_INTENT", "score": 2}])

    def test_empty_list_returns_none(self):
        assert classify([]) == "NONE"

    def test_zero_score_returns_none(self):
        assert classify([make_reason("PAYMENT_INTENT", 0)]) == "NONE"

    def test_negative_score_returns_none(self):
        assert classify([make_reason("PAYMENT_INTENT", -1)]) == "NONE"


# === Code Recognition ===


class TestCodeRecognition:
    """Tests for recognized intent codes."""

    @pytest.mark.parametrize("code", [
        "HARDSHIP_LANGUAGE",
        "LOAN_MOD_REQUEST",
        "BANKRUPTCY_OR_LAWYER",
        "LEGAL_THREAT",
        "DISPUTE_FEE_OR_CHARGE",
        "SUPERVISOR_REQUEST",
        "ABUSIVE_LANGUAGE",
        "THIRD_PARTY_CALLER",
        "PAYMENT_INTENT",
        "ESCROW_QUESTION",
        "NEW_LOAN_INQUIRY",
    ])
    def test_single_code_recognized(self, code):
        assert classify([make_reason(code, 2)]) == code

    def test_unknown_code_returns_none(self):
        assert classify([make_reason("UNKNOWN_CODE", 10)]) == "NONE"

    
        """HARDSHIP_LANGUAGE from ruleEngine should be recognized."""
        assert classify([make_reason("HARDSHIP_LANGUAGE", 5)]) == "HARDSHIP_LANGUAGE"

    
    def test_dispute_fee_or_charge_recognized(self):
        """DISPUTE_FEE_OR_CHARGE from ruleEngine should be recognized."""
        assert classify([make_reason("DISPUTE_FEE_OR_CHARGE", 5)]) == "DISPUTE_FEE_OR_CHARGE"


# === Score Priority ===


class TestScorePriority:
    """Tests for score-based intent selection."""

    def test_highest_score_wins(self):
        codes = [
            make_reason("PAYMENT_INTENT", 2),
            make_reason("ESCROW_QUESTION", 4),
            make_reason("LEGAL_THREAT", 3),
        ]
        assert classify(codes) == "ESCROW_QUESTION"

    def test_tie_preserves_first_encountered(self):
        codes = [
            make_reason("PAYMENT_INTENT", 2),
            make_reason("ESCROW_QUESTION", 2),
        ]
        assert classify(codes) == "PAYMENT_INTENT"

    def test_known_code_wins_over_unknown_with_higher_score(self):
        codes = [
            make_reason("UNKNOWN_CODE", 10),
            make_reason("PAYMENT_INTENT", 1),
        ]
        assert classify(codes) == "PAYMENT_INTENT"
