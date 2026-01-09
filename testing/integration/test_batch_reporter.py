"""
Integration tests for batchReporter.

Tests batch reporting with real processed transcript results.
"""

import json
import os
import pytest
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from engines.triageResult import TriagePipeline
from engines.batchReporter import batchReporter


@pytest.fixture(scope="module")
def reporter():
    return batchReporter()


@pytest.fixture(scope="module")
def expected():
    path = os.path.join(os.path.dirname(__file__), "expected_results.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def expected_csv():
    path = os.path.join(os.path.dirname(__file__), "expected_batch_output.csv")
    with open(path) as f:
        return f.read()


@pytest.fixture(scope="module")
def batch_results():
    pipeline = TriagePipeline()
    transcripts_dir = os.path.join(ROOT_DIR, "transcripts")
    paths = sorted([
        os.path.join(transcripts_dir, f) 
        for f in os.listdir(transcripts_dir) if f.endswith(".txt")
    ])
    return pipeline.process_batch(paths)


# === count_reason_codes ===


class TestCountReasonCodes:
    """Tests for reason code counting."""

    def test_returns_dict(self, reporter, batch_results):
        assert isinstance(reporter.count_reason_codes(batch_results), dict)

    def test_empty_list_returns_empty_dict(self, reporter):
        assert reporter.count_reason_codes([]) == {}

    def test_top_code_is_escrow_question(self, reporter, batch_results, expected):
        result = reporter.count_reason_codes(batch_results)
        top_code = max(result, key=result.get)
        assert top_code == expected["batch_metrics"]["top_reason_code"]

    @pytest.mark.parametrize("code", [
        "ESCROW_QUESTION", "PAYMENT_INTENT", "BANKRUPTCY_OR_LAWYER",
        "HARDSHIP_LANGUAGE", "ABUSIVE_LANGUAGE", "LEGAL_THREAT",
    ])
    def test_reason_code_count(self, reporter, batch_results, expected, code):
        result = reporter.count_reason_codes(batch_results)
        assert result.get(code, 0) == expected["batch_metrics"]["reason_code_counts"][code]


# === calculate_escalation_rate ===


class TestCalculateEscalationRate:
    """Tests for escalation rate calculation."""

    def test_returns_float(self, reporter, batch_results):
        assert isinstance(reporter.calculate_escalation_rate(batch_results), float)

    def test_empty_list_returns_zero(self, reporter):
        assert reporter.calculate_escalation_rate([]) == 0.0

    def test_correct_rate(self, reporter, batch_results, expected):
        result = reporter.calculate_escalation_rate(batch_results)
        assert abs(result - expected["batch_metrics"]["escalation_rate"]) < 0.1

    def test_within_valid_range(self, reporter, batch_results):
        result = reporter.calculate_escalation_rate(batch_results)
        assert 0.0 <= result <= 100.0


# === get_top_intents ===


class TestGetTopIntents:
    """Tests for top intents retrieval."""

    def test_returns_list_of_tuples(self, reporter, batch_results):
        result = reporter.get_top_intents(batch_results)
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_sorted_descending(self, reporter, batch_results):
        result = reporter.get_top_intents(batch_results, top_n=10)
        counts = [item[1] for item in result]
        assert counts == sorted(counts, reverse=True)

    def test_empty_list_returns_empty(self, reporter):
        assert reporter.get_top_intents([]) == []

    def test_respects_top_n(self, reporter, batch_results):
        assert len(reporter.get_top_intents(batch_results, top_n=3)) <= 3
        assert len(reporter.get_top_intents(batch_results, top_n=5)) <= 5


# === common_patterns ===


class TestCommonPatterns:
    """Tests for common pattern detection."""

    def test_returns_list_of_strings(self, reporter, batch_results):
        result = reporter.common_patterns(batch_results)
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_correct_count(self, reporter, batch_results, expected):
        result = reporter.common_patterns(batch_results)
        assert len(result) == expected["batch_metrics"]["common_patterns_count"]

    def test_empty_list_returns_empty(self, reporter):
        assert reporter.common_patterns([]) == []


# === build_report_dataframe ===


class TestBuildReportDataframe:
    """Tests for DataFrame generation."""

    def test_returns_dataframe(self, reporter, batch_results):
        import pandas as pd
        assert isinstance(reporter.build_report_dataframe(batch_results), pd.DataFrame)

    def test_correct_row_count(self, reporter, batch_results, expected):
        df = reporter.build_report_dataframe(batch_results)
        assert len(df) == expected["batch_metrics"]["total_transcripts"]

    def test_has_required_columns(self, reporter, batch_results):
        df = reporter.build_report_dataframe(batch_results)
        required = ["Intent", "Escalated", "Risk Level", "Reason Codes", "Summary Bullets"]
        assert all(col in df.columns for col in required)


# === generate_csv ===


class TestGenerateCsv:
    """Tests for CSV generation."""

    def test_returns_string(self, reporter, batch_results):
        assert isinstance(reporter.generate_csv(batch_results), str)

    def test_contains_summary_metrics(self, reporter, batch_results):
        csv = reporter.generate_csv(batch_results)
        assert "SUMMARY METRICS" in csv

    def test_contains_total_transcripts(self, reporter, batch_results, expected):
        csv = reporter.generate_csv(batch_results)
        count = expected["batch_metrics"]["total_transcripts"]
        assert f"Total Transcripts,{count}" in csv

    def test_contains_data_header(self, reporter, batch_results):
        csv = reporter.generate_csv(batch_results)
        assert "filename,intent,escalate,risk_level,reason_codes,summary" in csv

    def test_correct_data_row_count(self, reporter, batch_results, expected):
        csv = reporter.generate_csv(batch_results)
        data_lines = [l for l in csv.split("\n") if l.startswith("transcript_")]
        assert len(data_lines) == expected["batch_metrics"]["total_transcripts"]

    def test_matches_expected_header(self, reporter, batch_results, expected_csv):
        csv = reporter.generate_csv(batch_results)
        result_header = csv.split("\n")[:7]
        expected_header = expected_csv.split("\n")[:7]
        assert result_header == expected_header
