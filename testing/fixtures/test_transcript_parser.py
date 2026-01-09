"""
This is my first experinece wihh writing my own testing
"""

import datetime
from engines.transcriptParser import transcriptParser


def assert_timestamp_recent(timestamp_str: str, max_delta_seconds: int = 5):
    parsed = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    assert abs((now - parsed).total_seconds()) <= max_delta_seconds

#Things to test: 
#empty transcrippt
def test_empty_transcript():
    parser = transcriptParser()
    transcript = parser.parse_transcript("")
    assert transcript.get_raw_text() == ""
    assert transcript.get_normalized_text() == ""
    assert transcript.get_speakers() == []
    assert isinstance(transcript.get_timestamp(), str)
    assert_timestamp_recent(transcript.get_timestamp())

def test_no_speakers():
    parser = transcriptParser()
    raw_text = "This is a test transcript without any speaker labels."
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "this is a test transcript without any speaker labels."
    assert transcript.get_speakers() == []
    assert isinstance(transcript.get_timestamp(), str)
    assert_timestamp_recent(transcript.get_timestamp())

def test_multiple_speakers():
    parser = transcriptParser()
    raw_text = "Speaker 1: Hello there.\nSpeaker 2: Hi! How are you?\nSpeaker 1: I'm good, thanks."
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "speaker 1: hello there. speaker 2: hi! how are you? speaker 1: i'm good, thanks."
    assert set(transcript.get_speakers()) == {"Speaker 1", "Speaker 2"}
    assert isinstance(transcript.get_timestamp(), str)
    assert_timestamp_recent(transcript.get_timestamp())

def test_whitespace_only_transcript():
    parser = transcriptParser()
    raw_text = "   \n\t  "
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == ""
    assert transcript.get_speakers() == []
    assert_timestamp_recent(transcript.get_timestamp())

def test_windows_newlines_speakers():
    parser = transcriptParser()
    raw_text = "Speaker 1: Hello\r\nSpeaker 2: Hi\r\n"
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "speaker 1: hello speaker 2: hi"
    assert set(transcript.get_speakers()) == {"Speaker 1", "Speaker 2"}
    assert_timestamp_recent(transcript.get_timestamp())

def test_empty_speaker_label_ignored():
    parser = transcriptParser()
    raw_text = ": hello\n: hi"
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == ": hello : hi"
    assert transcript.get_speakers() == []
    assert_timestamp_recent(transcript.get_timestamp())

def test_multiple_colons_in_line():
    parser = transcriptParser()
    raw_text = "Agent: note: customer said: yes"
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "agent: note: customer said: yes"
    assert transcript.get_speakers() == ["Agent"]
    assert_timestamp_recent(transcript.get_timestamp())












