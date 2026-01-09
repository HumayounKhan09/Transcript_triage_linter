"""
Unit tests for summaryGenerator.
"""

import pytest
from Data_Classes.entities import Entities
from Data_Classes.reasonCode import reasonCode
from engines.summaryGenerator import summaryGenerator


def make_entities(amounts=None, dates=None, phones=None, loan_numbers=None) -> Entities:
    return Entities(amounts or [], dates or [], phones or [], loan_numbers or [])


def make_reason(code: str, is_escalation: bool = True, score: int = 2) -> reasonCode:
    return reasonCode(code, is_escalation, score)


@pytest.fixture
def gen():
    return summaryGenerator()


# === extract_payment_bullet ===


class TestExtractPaymentBullet:
    """Tests for payment bullet generation."""

    def test_empty_amounts_returns_none(self, gen):
        assert gen.extract_payment_bullet(make_entities()) is None

    def test_single_amount_formatted(self, gen):
        bullet = gen.extract_payment_bullet(make_entities(amounts=[1234.5]))
        assert bullet == "Borrower mentioned payment amount of $1,234.50"

    def test_multiple_amounts_formatted(self, gen):
        bullet = gen.extract_payment_bullet(make_entities(amounts=[10, 2000.1]))
        assert bullet == "Borrower discussed multiple amounts: $10.00, $2,000.10"

    def test_large_amount_formatted(self, gen):
        bullet = gen.extract_payment_bullet(make_entities(amounts=[1000000]))
        assert "$1,000,000.00" in bullet


# === extract_request_bullet ===


class TestExtractRequestBullet:
    """Tests for request bullet generation."""

    def test_payment_intent(self, gen):
        assert gen.extract_request_bullet("payment", []) == "Borrower requested to make a payment"

    def test_hardship_with_loan_mod(self, gen):
        reasons = [make_reason("LOAN_MOD_REQUEST")]
        assert gen.extract_request_bullet("hardship", reasons) == "Requested loan modification due to financial hardship"

    def test_hardship_without_loan_mod(self, gen):
        assert gen.extract_request_bullet("hardship", []) == "Mentioned financial difficulties affecting payments"

    def test_escrow_intent(self, gen):
        assert gen.extract_request_bullet("escrow", []) == "Asked about escrow account details"

    def test_dispute_intent(self, gen):
        assert gen.extract_request_bullet("dispute", []) == "Disputed charges or fees on account"

    def test_new_loan_intent(self, gen):
        assert gen.extract_request_bullet("new-loan", []) == "Inquired about refinancing or new loan options"

    def test_unknown_intent(self, gen):
        assert gen.extract_request_bullet("unknown", []) == "General inquiry about account"


# === extract_escalation_bullet ===


class TestExtractEscalationBullet:
    """Tests for escalation bullet generation."""

    def test_no_escalation_codes_returns_none(self, gen):
        reasons = [make_reason("PAYMENT_INTENT", is_escalation=False)]
        assert gen.extract_escalation_bullet(reasons) is None

    def test_single_escalation_reason(self, gen):
        reasons = [make_reason("ABUSIVE_LANGUAGE")]
        bullet = gen.extract_escalation_bullet(reasons)
        assert bullet == "Call escalated due to: abusive language used"

    @pytest.mark.parametrize("code,expected_phrase", [
        ("HARDSHIP_LANGUAGE", "financial hardship mentioned"),
        ("LOAN_MOD_REQUEST", "loan modification requested"),
        ("BANKRUPTCY_OR_LAWYER", "bankruptcy or legal counsel referenced"),
        ("LEGAL_THREAT", "legal action threatened"),
        ("DISPUTE_FEE_OR_CHARGE", "fee dispute"),
        ("SUPERVISOR_REQUEST", "supervisor requested"),
        ("ABUSIVE_LANGUAGE", "abusive language used"),
        ("THIRD_PARTY_CALLER", "third party caller (unauthorized)"),
    ])
    def test_escalation_code_produces_correct_phrase(self, gen, code, expected_phrase):
        reasons = [make_reason(code)]
        bullet = gen.extract_escalation_bullet(reasons)
        assert expected_phrase in bullet

    def test_multiple_escalation_reasons(self, gen):
        reasons = [
            make_reason("SUPERVISOR_REQUEST"),
            make_reason("DISPUTE_FEE_OR_CHARGE"),
        ]
        bullet = gen.extract_escalation_bullet(reasons)
        assert "fee dispute" in bullet
        assert "supervisor requested" in bullet


# === format_bullet ===


class TestFormatBullet:
    """Tests for bullet formatting."""

    def test_empty_returns_empty(self, gen):
        assert gen.format_bullet("") == ""

    def test_capitalizes_first_letter(self, gen):
        assert gen.format_bullet("hello world") == "Hello world."

    def test_adds_period(self, gen):
        assert gen.format_bullet("hello world") == "Hello world."

    def test_no_double_period(self, gen):
        assert gen.format_bullet("hello world.") == "Hello world."

    def test_single_character(self, gen):
        assert gen.format_bullet("a") == "A."


# === generate_bullets ===


class TestGenerateBullets:
    """Tests for combined bullet generation."""

    def test_none_entities_raises_attribute_error(self, gen):
        with pytest.raises(AttributeError):
            gen.generate_bullets("payment", None, [])

    def test_request_only_when_no_amounts_or_escalation(self, gen):
        bullets = gen.generate_bullets("escrow", make_entities(), [])
        assert bullets == ["Asked about escrow account details."]

    def test_includes_payment_bullet_when_amounts(self, gen):
        entities = make_entities(amounts=[250.0])
        bullets = gen.generate_bullets("payment", entities, [])
        assert any("$250.00" in b for b in bullets)

    def test_includes_escalation_bullet_when_escalation(self, gen):
        reasons = [make_reason("HARDSHIP_LANGUAGE")]
        bullets = gen.generate_bullets("payment", make_entities(), reasons)
        assert any("escalated" in b.lower() for b in bullets)

    def test_all_three_bullet_types(self, gen):
        entities = make_entities(amounts=[250.0])
        reasons = [make_reason("HARDSHIP_LANGUAGE")]
        bullets = gen.generate_bullets("payment", entities, reasons)
        assert len(bullets) == 3
