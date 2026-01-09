"""
Integration tests for CLI.

Tests command-line interface functionality.
"""

import json
import os
import shutil
import tempfile
import pytest
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT_DIR)

from engines.cli import CLI


@pytest.fixture
def cli():
    return CLI()


@pytest.fixture(scope="module")
def expected():
    path = os.path.join(os.path.dirname(__file__), "expected_results.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def transcripts_dir():
    return os.path.join(ROOT_DIR, "transcripts")


@pytest.fixture
def sample_path(transcripts_dir):
    return os.path.join(transcripts_dir, "test_payment_simple_rambling.txt")


@pytest.fixture
def temp_dir(transcripts_dir):
    """Temp directory with symlink to transcripts."""
    temp = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp, "results"), exist_ok=True)
    os.symlink(transcripts_dir, os.path.join(temp, "transcripts"))
    yield temp
    shutil.rmtree(temp)


# === Argument Validation ===


class TestValidateArgs:
    """Tests for argument validation."""

    def test_single_without_format_fails(self, cli):
        class Args:
            single = "test.txt"
            batch = False
            list = False
            format = None
        assert cli.validate_args(Args()) is False

    def test_batch_without_format_fails(self, cli):
        class Args:
            single = None
            batch = True
            list = False
            format = None
        assert cli.validate_args(Args()) is False

    def test_nonexistent_file_fails(self, cli):
        class Args:
            single = "/nonexistent.txt"
            batch = False
            list = False
            format = "json"
        assert cli.validate_args(Args()) is False

    def test_valid_single_passes(self, cli, sample_path):
        class Args:
            single = sample_path
            batch = False
            list = False
            format = "json"
        assert cli.validate_args(Args()) is True


# === Single Mode ===


class TestRunSingleMode:
    """Tests for single transcript processing."""

    def test_creates_json_output(self, cli, sample_path, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_single_mode(sample_path, "json")
            assert os.path.exists("results/test_payment_simple_rambling.json")
        finally:
            os.chdir(original)

    def test_creates_csv_output(self, cli, sample_path, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_single_mode(sample_path, "csv")
            assert os.path.exists("results/test_payment_simple_rambling.csv")
        finally:
            os.chdir(original)

    def test_both_creates_two_files(self, cli, sample_path, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_single_mode(sample_path, "both")
            assert os.path.exists("results/test_payment_simple_rambling.json")
            assert os.path.exists("results/test_payment_simple_rambling.csv")
        finally:
            os.chdir(original)

    def test_json_is_valid(self, cli, sample_path, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_single_mode(sample_path, "json")
            with open("results/test_payment_simple_rambling.json") as f:
                data = json.load(f)
            assert "intent" in data
            assert "escalate" in data
            assert "risk_level" in data
        finally:
            os.chdir(original)

    def test_invalid_format_raises_error(self, cli, sample_path):
        with pytest.raises(ValueError):
            cli.run_single_mode(sample_path, "invalid")


# === Batch Mode ===


class TestRunBatchMode:
    """Tests for batch transcript processing."""

    def test_creates_json_output(self, cli, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_batch_mode("json")
            assert os.path.exists("results/batch_results.json")
        finally:
            os.chdir(original)

    def test_creates_csv_output(self, cli, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_batch_mode("csv")
            assert os.path.exists("results/batch_results.csv")
        finally:
            os.chdir(original)

    def test_json_has_correct_count(self, cli, temp_dir, expected):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_batch_mode("json")
            with open("results/batch_results.json") as f:
                data = json.load(f)
            assert len(data) == expected["batch_metrics"]["total_transcripts"]
        finally:
            os.chdir(original)

    def test_json_items_have_required_fields(self, cli, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            cli.run_batch_mode("json")
            with open("results/batch_results.json") as f:
                data = json.load(f)
            for item in data:
                assert "filename" in item
                assert "intent" in item
        finally:
            os.chdir(original)

    def test_invalid_format_raises_error(self, cli, temp_dir):
        original = os.getcwd()
        os.chdir(temp_dir)
        try:
            with pytest.raises(ValueError):
                cli.run_batch_mode("invalid")
        finally:
            os.chdir(original)


# === Print Methods ===


class TestPrintMethods:
    """Tests for terminal output methods."""

    def test_print_summary_outputs_intent(self, cli, sample_path, capsys):
        result = cli.pipeline.process_single(sample_path)
        cli.print_summary(result)
        captured = capsys.readouterr()
        assert "Intent:" in captured.out
        assert "PAYMENT_INTENT" in captured.out

    def test_print_batch_stats_outputs_total(self, cli, transcripts_dir, capsys):
        paths = [os.path.join(transcripts_dir, f) for f in os.listdir(transcripts_dir) if f.endswith(".txt")][:3]
        results = cli.pipeline.process_batch(paths)
        cli.print_batch_stats(results)
        captured = capsys.readouterr()
        assert "Total processed:" in captured.out

    def test_print_batch_stats_empty_results(self, cli, capsys):
        cli.print_batch_stats([])
        captured = capsys.readouterr()
        assert "Total processed: 0" in captured.out
