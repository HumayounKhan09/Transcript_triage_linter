"""
Unit tests for entityExtractor.
"""

import pytest
from Data_Classes.transcript import transcript as Transcript
from engines.entityExtractor import entityExtractor


def make_transcript(raw_text: str) -> Transcript:
    normalized = " ".join(raw_text.lower().split())
    return Transcript(raw_text, normalized, [], "2024-01-01 00:00:00")


@pytest.fixture
def extractor():
    return entityExtractor()


# === extract_amounts ===


class TestExtractAmounts:
    """Tests for monetary amount extraction."""

    def test_empty_text_returns_empty_list(self, extractor):
        assert extractor.extract_amounts("") == []

    def test_none_raises_type_error(self, extractor):
        with pytest.raises(TypeError):
            extractor.extract_amounts(None)

    def test_dollar_sign_simple(self, extractor):
        assert extractor.extract_amounts("$5,000") == [5000]

    def test_dollar_sign_with_cents(self, extractor):
        assert extractor.extract_amounts("$99.99 fee") == [99.99]

    def test_usd_prefix(self, extractor):
        assert extractor.extract_amounts("USD 5000") == [5000]

    def test_cad_prefix(self, extractor):
        assert extractor.extract_amounts("CAD 100,000") == [100000]

    def test_dollars_suffix(self, extractor):
        assert extractor.extract_amounts("5000 dollars") == [5000]

    def test_thousand_keyword(self, extractor):
        assert extractor.extract_amounts("5 thousand dollars") == [5000.0]

    def test_million_keyword(self, extractor):
        assert extractor.extract_amounts("1.25 million") == [1250000.0]

    def test_billion_keyword(self, extractor):
        assert extractor.extract_amounts("2 billion") == [2000000000]

    def test_mortgage_context_scales_to_thousands(self, extractor):
        """Bare values 100-9999 in mortgage context scale to thousands."""
        assert extractor.extract_amounts("mortgage amount is 850") == [850000]

    def test_deduplication(self, extractor):
        """Equivalent values should be deduped."""
        assert extractor.extract_amounts("USD 5,000 and $5000") == [5000]

    def test_ignores_loan_number_context(self, extractor):
        assert extractor.extract_amounts("loan number 123456") == []

    def test_multiple_amounts(self, extractor):
        result = extractor.extract_amounts("$850,000, then 3 million")
        assert 850000 in result
        assert 3000000 in result

    @pytest.mark.xfail(reason="Regex requires space before magnitude suffix")
    def test_k_suffix_no_space(self, extractor):
        """$500k should work but currently requires space."""
        assert extractor.extract_amounts("$500k") == [500000.0]

    @pytest.mark.xfail(reason="Regex requires space before magnitude suffix")
    def test_m_suffix_no_space(self, extractor):
        """$1.5m should work but currently requires space."""
        assert extractor.extract_amounts("$1.5m") == [1500000.0]

    def test_k_suffix_with_space(self, extractor):
        """$500 k works with space."""
        assert extractor.extract_amounts("$500 k") == [500000]

    def test_m_suffix_with_space(self, extractor):
        """$1.5 m works with space."""
        assert extractor.extract_amounts("$1.5 m") == [1500000]

    @pytest.mark.xfail(reason="CA$ prefix not matched by regex")
    def test_ca_dollar_sign(self, extractor):
        """CA$ format should work but doesn't."""
        assert extractor.extract_amounts("CA$100,000") == [100000]


# === extract_dates ===


class TestExtractDates:
    """Tests for date extraction."""

    def test_empty_text_returns_empty_list(self, extractor):
        assert extractor.extract_dates("") == []

    def test_none_raises_type_error(self, extractor):
        with pytest.raises(TypeError):
            extractor.extract_dates(None)

    def test_numeric_format_mm_dd_yyyy(self, extractor):
        assert extractor.extract_dates("Due 01/15/2024") == ["01/15/2024"]

    def test_month_day_year(self, extractor):
        result = extractor.extract_dates("Due Jan 5, 2023")
        assert "Jan 5, 2023" in result

    def test_day_month_format(self, extractor):
        result = extractor.extract_dates("Payment on 15 Jan")
        assert "15 Jan" in result

    def test_month_day_format(self, extractor):
        result = extractor.extract_dates("Payment on Jan 15")
        assert "Jan 15" in result

    @pytest.mark.xfail(reason="Overlapping patterns produce duplicate partial matches")
    def test_no_duplicate_partial_matches(self, extractor):
        """Should not return both 'Jan 5, 2023' and 'Jan 5'."""
        result = extractor.extract_dates("Due Jan 5, 2023")
        assert result == ["Jan 5, 2023"]


# === extract_phones ===


class TestExtractPhones:
    """Tests for phone number extraction."""

    def test_empty_text_returns_empty_list(self, extractor):
        assert extractor.extract_phones("") == []

    def test_none_raises_type_error(self, extractor):
        with pytest.raises(TypeError):
            extractor.extract_phones(None)

    def test_dashes_format(self, extractor):
        assert extractor.extract_phones("Call 555-123-4567") == ["555-123-4567"]

    def test_with_country_code(self, extractor):
        result = extractor.extract_phones("Call +1 555-123-4567")
        assert "+1 555-123-4567" in result

    def test_parentheses_format(self, extractor):
        result = extractor.extract_phones("Call (555) 123-4567")
        assert "(555) 123-4567" in result

    def test_multiple_numbers(self, extractor):
        result = extractor.extract_phones("Call 555-123-4567 or 555-987-6543")
        assert len(result) == 2


# === extract_loan_numbers ===


class TestExtractLoanNumbers:
    """Tests for loan number extraction."""

    def test_empty_text_returns_empty_list(self, extractor):
        assert extractor.extract_loan_numbers("") == []

    def test_none_raises_type_error(self, extractor):
        with pytest.raises(TypeError):
            extractor.extract_loan_numbers(None)

    def test_ln_prefix_format(self, extractor):
        assert extractor.extract_loan_numbers("LN-123456") == ["LN-123456"]

    def test_loan_number_phrase(self, extractor):
        assert extractor.extract_loan_numbers("loan number 0001234") == ["0001234"]

    def test_account_number_phrase(self, extractor):
        assert extractor.extract_loan_numbers("account # 0001234") == ["0001234"]

    def test_deduplication(self, extractor):
        result = extractor.extract_loan_numbers("loan number 0001234 and account # 0001234")
        assert result == ["0001234"]

    def test_minimum_length_4_digits(self, extractor):
        assert extractor.extract_loan_numbers("loan number 1234") == ["1234"]

    def test_too_short_excluded(self, extractor):
        assert extractor.extract_loan_numbers("loan number 123") == []

    def test_backwards_compat_alias(self, extractor):
        """Misspelled method name should still work."""
        assert extractor.extract_loan_numbesrs("loan number 0001234") == ["0001234"]


# === extract_all_entities ===


class TestExtractAllEntities:
    """Tests for combined entity extraction."""

    def test_none_transcript_raises_attribute_error(self, extractor):
        with pytest.raises(AttributeError):
            extractor.extract_all_entities(None)

    def test_extracts_all_entity_types(self, extractor):
        text = "$5,000 due 01/15/2024, call 555-123-4567, loan # 0001234"
        entities = extractor.extract_all_entities(make_transcript(text))
        assert 5000 in entities.get_amounts()
        assert "01/15/2024" in entities.get_dates()
        assert "555-123-4567" in entities.get_phones()
        assert "0001234" in entities.get_loan_numbers()
