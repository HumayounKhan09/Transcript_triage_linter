"""
Integration tests for TriagePipeline.

Tests end-to-end transcript processing using real transcript files.
"""

import json
import os
import pytest
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from engines.triageResult import TriagePipeline
from Data_Classes.triageResult import triageResult


@pytest.fixture(scope="module")
def pipeline():
    return TriagePipeline()


@pytest.fixture(scope="module")
def expected():
    path = os.path.join(os.path.dirname(__file__), "expected_results.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def transcripts_dir():
    return os.path.join(ROOT_DIR, "transcripts")


@pytest.fixture(scope="module")
def all_paths(transcripts_dir):
    return sorted([
        os.path.join(transcripts_dir, f) 
        for f in os.listdir(transcripts_dir) if f.endswith(".txt")
    ])


@pytest.fixture(scope="module")
def batch_results(pipeline, all_paths):
    return pipeline.process_batch(all_paths)


def get_expected(expected, filename):
    for item in expected["transcripts"]:
        if item["filename"] == filename:
            return item
    return None


# === process_single ===


class TestProcessSingle:
    """Tests for single transcript processing."""

    def test_returns_triage_result(self, pipeline, transcripts_dir):
        path = os.path.join(transcripts_dir, "test_payment_simple_rambling.txt")
        assert isinstance(pipeline.process_single(path), triageResult)

    def test_file_not_found_raises_error(self, pipeline):
        with pytest.raises(FileNotFoundError):
            pipeline.process_single("/nonexistent/file.txt")

    @pytest.mark.parametrize("filename,expected_intent", [
        ("test_payment_simple_rambling.txt", "PAYMENT_INTENT"),
        ("test_legal_threat_angry_escalation.txt", "LEGAL_THREAT"),
        ("test_escrow_confused_customer.txt", "ESCROW_QUESTION"),
        ("test_new_loan_inquiry_detailed.txt", "NEW_LOAN_INQUIRY"),
    ])
    def test_intent_classification(self, pipeline, transcripts_dir, filename, expected_intent):
        path = os.path.join(transcripts_dir, filename)
        result = pipeline.process_single(path)
        assert result._intent == expected_intent

    @pytest.mark.parametrize("filename,expected_escalate", [
        ("test_payment_simple_rambling.txt", False),
        ("test_legal_threat_angry_escalation.txt", True),
        ("test_escrow_confused_customer.txt", False),
        ("test_abusive_language_escalating.txt", True),
    ])
    def test_escalation_detection(self, pipeline, transcripts_dir, filename, expected_escalate):
        path = os.path.join(transcripts_dir, filename)
        result = pipeline.process_single(path)
        assert result._escalate == expected_escalate

    @pytest.mark.parametrize("filename,expected_risk", [
        ("test_payment_simple_rambling.txt", "LOW"),
        ("test_dispute_escalates_slowly.txt", "MEDIUM"),
        ("test_legal_threat_angry_escalation.txt", "HIGH"),
    ])
    def test_risk_level(self, pipeline, transcripts_dir, filename, expected_risk):
        path = os.path.join(transcripts_dir, filename)
        result = pipeline.process_single(path)
        assert result._risk_level == expected_risk

    def test_extracts_amounts(self, pipeline, transcripts_dir):
        path = os.path.join(transcripts_dir, "test_payment_simple_rambling.txt")
        result = pipeline.process_single(path)
        assert 2450 in result._entities.get_amounts()

    def test_extracts_loan_numbers(self, pipeline, transcripts_dir):
        path = os.path.join(transcripts_dir, "test_third_party_persistent.txt")
        result = pipeline.process_single(path)
        assert "345678" in result._entities.get_loan_numbers()


# === process_batch ===


class TestProcessBatch:
    """Tests for batch transcript processing."""

    def test_returns_list(self, batch_results):
        assert isinstance(batch_results, list)

    def test_correct_count(self, batch_results, expected):
        assert len(batch_results) == expected["batch_metrics"]["total_transcripts"]

    def test_all_are_triage_results(self, batch_results):
        assert all(isinstance(r, triageResult) for r in batch_results)

    def test_escalated_count(self, batch_results, expected):
        count = sum(1 for r in batch_results if r._escalate)
        assert count == expected["batch_metrics"]["escalated_count"]

    def test_risk_level_counts(self, batch_results, expected):
        high = sum(1 for r in batch_results if r._risk_level == "HIGH")
        medium = sum(1 for r in batch_results if r._risk_level == "MEDIUM")
        low = sum(1 for r in batch_results if r._risk_level == "LOW")
        assert high == expected["batch_metrics"]["high_risk_count"]
        assert medium == expected["batch_metrics"]["medium_risk_count"]
        assert low == expected["batch_metrics"]["low_risk_count"]

    def test_empty_list_returns_empty(self, pipeline):
        assert pipeline.process_batch([]) == []


# === Result Consistency ===


class TestResultConsistency:
    """Tests for cross-field consistency."""

    def test_high_risk_implies_escalation(self, batch_results):
        for r in batch_results:
            if r._risk_level == "HIGH":
                assert r._escalate is True

    def test_low_risk_implies_no_escalation(self, batch_results):
        for r in batch_results:
            if r._risk_level == "LOW":
                assert r._escalate is False

    def test_summary_bullets_not_empty(self, batch_results):
        for r in batch_results:
            assert len(r._summary_bullet) > 0

    def test_entities_not_none(self, batch_results):
        for r in batch_results:
            assert r._entities is not None
