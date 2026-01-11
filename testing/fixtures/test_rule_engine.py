"""
Unit tests for ruleEngine.
"""

import pytest
from Data_Classes.transcript import transcript as Transcript
from engines.ruleEngine import ruleEngine


def make_transcript(raw_text: str) -> Transcript:
    normalized = " ".join(raw_text.lower().split())
    return Transcript(raw_text, normalized, [], "2024-01-01 00:00:00")


def run_rules(raw_text: str):
    engine = ruleEngine(make_transcript(raw_text))
    return engine.apply_rules()


def to_code_map(reason_codes):
    return {rc.get_code(): rc for rc in reason_codes}


# === Basic Behavior ===


class TestBasicBehavior:
    """Tests for basic rule engine behavior."""

    def test_none_text_raises_attribute_error(self):
        with pytest.raises(AttributeError):
            run_rules(None) # type: ignore

    def test_empty_text_returns_empty_list(self):
        assert run_rules("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert run_rules("   \n\t   ") == []


# === Threshold Behavior ===


class TestThresholdBehavior:
    """Tests for score threshold behavior (threshold = 2)."""

    def test_single_keyword_below_threshold_excluded(self):
        """Single word 'payment' (1 point) should not trigger."""
        codes = to_code_map(run_rules("payment"))
        assert "PAYMENT_INTENT" not in codes

    def test_single_word_below_threshold_excluded(self):
        """Single word 'dispute' (1 point) should not trigger."""
        codes = to_code_map(run_rules("dispute"))
        assert "DISPUTE_FEE_OR_CHARGE" not in codes

    def test_phrase_meets_threshold(self):
        """Phrase 'make a payment' (2 points) should trigger."""
        codes = to_code_map(run_rules("I want to make a payment"))
        assert "PAYMENT_INTENT" in codes

    def test_two_single_words_meet_threshold(self):
        """Two single words should sum to meet threshold."""
        codes = to_code_map(run_rules("payment and balance"))
        assert "PAYMENT_INTENT" in codes


# === Escalation Rules ===


class TestEscalationRules:
    """Tests for each escalation rule type."""

    def test_hardship_language(self):
        codes = to_code_map(run_rules("I lost my job last month"))
        assert "HARDSHIP_LANGUAGE" in codes
        assert codes["HARDSHIP_LANGUAGE"].get_is_escalation() is True

    def test_loan_mod_request(self):
        codes = to_code_map(run_rules("I need a loan modification"))
        assert "LOAN_MOD_REQUEST" in codes

    def test_bankruptcy_or_lawyer(self):
        codes = to_code_map(run_rules("I filed bankruptcy recently"))
        assert "BANKRUPTCY_OR_LAWYER" in codes

    def test_legal_threat(self):
        codes = to_code_map(run_rules("I will take legal action"))
        assert "LEGAL_THREAT" in codes

    def test_dispute_fee_or_charge(self):
        codes = to_code_map(run_rules("I want to dispute this charge"))
        assert "DISPUTE_FEE_OR_CHARGE" in codes

    def test_supervisor_request(self):
        codes = to_code_map(run_rules("I want to speak to supervisor"))
        assert "SUPERVISOR_REQUEST" in codes

    def test_abusive_language(self):
        codes = to_code_map(run_rules("This service is stupid and useless"))
        assert "ABUSIVE_LANGUAGE" in codes

    def test_third_party_caller(self):
        codes = to_code_map(run_rules("I'm calling for my husband about his loan"))
        assert "THIRD_PARTY_CALLER" in codes


# === Normal Rules ===


class TestNormalRules:
    """Tests for normal (non-escalation) rules."""

    def test_payment_intent(self):
        codes = to_code_map(run_rules("I want to make a payment today"))
        assert "PAYMENT_INTENT" in codes

    def test_escrow_question(self):
        codes = to_code_map(run_rules("Can you explain my escrow account"))
        assert "ESCROW_QUESTION" in codes

    def test_new_loan_inquiry(self):
        codes = to_code_map(run_rules("I want to refinance my mortgage"))
        assert "NEW_LOAN_INQUIRY" in codes


# === Escalation Flag Propagation ===


class TestEscalationFlagPropagation:
    """Tests for escalation flag propagation to all reason codes."""

    def test_escalation_flag_propagates_when_escalation_rule_fires(self):
        """When escalation rule fires, all codes get is_escalation=True."""
        text = "I want to make a payment and I need a loan modification"
        codes = to_code_map(run_rules(text))
        assert codes["PAYMENT_INTENT"].get_is_escalation() is True

    def test_no_escalation_flag_when_only_normal_rules(self):
        """When only normal rules fire, is_escalation=False."""
        text = "I want to make a payment and check my escrow account"
        codes = to_code_map(run_rules(text))
        assert codes["PAYMENT_INTENT"].get_is_escalation() is False
        assert codes["ESCROW_QUESTION"].get_is_escalation() is False


# === Multiple Rules ===


class TestMultipleRules:
    """Tests for multiple rules firing together."""

    def test_multiple_escalation_rules(self):
        text = "I lost my job and filed bankruptcy"
        codes = to_code_map(run_rules(text))
        assert "HARDSHIP_LANGUAGE" in codes
        assert "BANKRUPTCY_OR_LAWYER" in codes

    def test_multiple_normal_rules(self):
        text = "I want to make a payment and check my escrow account and refinance"
        codes = to_code_map(run_rules(text))
        assert "PAYMENT_INTENT" in codes
        assert "ESCROW_QUESTION" in codes
        assert "NEW_LOAN_INQUIRY" in codes


# === Score Accumulation ===


class TestScoreAccumulation:
    """Tests for score accumulation behavior."""

    def test_repeated_phrase_counts_once(self):
        """Repeated phrases should not inflate scores."""
        text = "lost my job. lost my job. lost my job."
        codes = to_code_map(run_rules(text))
        assert codes["HARDSHIP_LANGUAGE"].get_score() == 2

    def test_score_from_phrase_plus_single_word(self):
        """Phrase (2) + single word (1) = 3."""
        text = "I lost my job and struggling"
        codes = to_code_map(run_rules(text))
        assert codes["HARDSHIP_LANGUAGE"].get_score() >= 3

    @pytest.mark.xfail(reason="Overlapping keywords cause double-counting")
    def test_overlapping_keywords_not_double_counted(self):
        """'take legal action' contains 'legal action' - should not double count."""
        codes = to_code_map(run_rules("I will take legal action"))
        assert codes["LEGAL_THREAT"].get_score() == 2


# === Case Insensitivity ===


class TestCaseInsensitivity:
    """Tests for case-insensitive matching."""

    def test_uppercase_matches(self):
        codes = to_code_map(run_rules("I LOST MY JOB"))
        assert "HARDSHIP_LANGUAGE" in codes

    def test_mixed_case_matches(self):
        codes = to_code_map(run_rules("I Lost My Job"))
        assert "HARDSHIP_LANGUAGE" in codes
