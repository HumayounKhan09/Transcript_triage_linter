"""
Unit tests for transcriptParser.
"""

import datetime
import pytest
from engines.transcriptParser import transcriptParser


def parse(raw_text: str):
    return transcriptParser().parse_transcript(raw_text)


def assert_timestamp_recent(timestamp_str: str, max_delta_seconds: int = 5):
    parsed = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    assert abs((now - parsed).total_seconds()) <= max_delta_seconds


# === Basic Behavior ===


class TestBasicBehavior:
    """Tests for basic parser behavior."""

    def test_none_input_raises_attribute_error(self):
        with pytest.raises(AttributeError):
            parse(None) #type: ignore

    def test_empty_text_normalized_empty(self):
        assert parse("").get_normalized_text() == ""

    def test_empty_text_speakers_empty(self):
        assert parse("").get_speakers() == []

    def test_empty_text_timestamp_recent(self):
        assert_timestamp_recent(parse("").get_timestamp())

    def test_whitespace_only_normalized_empty(self):
        assert parse("   \n\t  ").get_normalized_text() == ""


# === Text Normalization ===


class TestTextNormalization:
    """Tests for text normalization."""

    def test_lowercased(self):
        transcript = parse("HELLO WORLD")
        assert transcript.get_normalized_text() == "hello world"

    def test_extra_spaces_collapsed(self):
        transcript = parse("hello    world")
        assert transcript.get_normalized_text() == "hello world"

    def test_newlines_normalized_to_spaces(self):
        transcript = parse("hello\nworld")
        assert transcript.get_normalized_text() == "hello world"

    def test_windows_newlines_normalized(self):
        transcript = parse("hello\r\nworld")
        assert transcript.get_normalized_text() == "hello world"

    def test_tabs_normalized(self):
        transcript = parse("hello\tworld")
        assert transcript.get_normalized_text() == "hello world"

    def test_leading_trailing_whitespace_trimmed(self):
        transcript = parse("   hello   ")
        assert transcript.get_normalized_text() == "hello"


# === Speaker Extraction ===


class TestSpeakerExtraction:
    """Tests for speaker extraction."""

    def test_no_speakers_when_no_colon(self):
        transcript = parse("This is a test transcript")
        assert transcript.get_speakers() == []

    def test_single_speaker_extracted(self):
        transcript = parse("Agent: Hello there")
        assert transcript.get_speakers() == ["Agent"]

    def test_multiple_speakers_extracted(self):
        transcript = parse("Speaker 1: Hello\nSpeaker 2: Hi")
        assert set(transcript.get_speakers()) == {"Speaker 1", "Speaker 2"}

    def test_speakers_deduplicated(self):
        transcript = parse("Agent: Hello\nAgent: How can I help?")
        speakers = transcript.get_speakers()
        assert speakers.count("Agent") == 1

    def test_empty_speaker_label_ignored(self):
        transcript = parse(": hello")
        assert transcript.get_speakers() == []

    def test_multiple_colons_uses_first_segment(self):
        transcript = parse("Agent: note: customer said: yes")
        assert transcript.get_speakers() == ["Agent"]

    def test_speaker_with_numbers(self):
        transcript = parse("Agent 1: Hello")
        assert "Agent 1" in transcript.get_speakers()

    def test_speaker_with_special_characters(self):
        transcript = parse("O'Brien: Hello")
        assert "O'Brien" in transcript.get_speakers()


# === Raw Text Preservation ===


class TestRawTextPreservation:
    """Tests for raw text preservation."""

    def test_raw_text_unchanged(self):
        raw = "Speaker 1: Hello!\nSpeaker 2: Hi there!"
        transcript = parse(raw)
        assert transcript.get_raw_text() == raw

    def test_unicode_preserved(self):
        transcript = parse("Agent: 你好 مرحبا")
        assert "你好" in transcript.get_normalized_text()
        assert "مرحبا" in transcript.get_normalized_text()


# === Timestamp ===


class TestTimestamp:
    """Tests for timestamp generation."""

    def test_timestamp_format(self):
        transcript = parse("Hello")
        timestamp = transcript.get_timestamp()
        # Should match YYYY-MM-DD HH:MM:SS format
        datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")  # Will raise if invalid

    def test_timestamp_is_current(self):
        transcript = parse("Hello")
        assert_timestamp_recent(transcript.get_timestamp())
