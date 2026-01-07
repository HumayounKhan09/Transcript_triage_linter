"""
This is my first experinece wihh writing my own testing
"""

import datetime
from engines.transcriptParser import transcriptParser

#Things to test: 
#empty transcrippt
def test_empty_transcript():
    parser = transcriptParser()
    transcript = parser.parse_transcript("")
    assert transcript.get_raw_text() == ""
    assert transcript.get_normalized_text() == ""
    assert transcript.get_speakers() == []
    assert isinstance(transcript.get_timestamp(), str)
    assert transcript.get_timestamp() ==  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_no_speakers():
    parser = transcriptParser()
    raw_text = "This is a test transcript without any speaker labels."
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "this is a test transcript without any speaker labels."
    assert transcript.get_speakers() == []
    assert isinstance(transcript.get_timestamp(), str)
    assert transcript.get_timestamp() ==  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

def test_multiple_speakers():
    parser = transcriptParser()
    raw_text = "Speaker 1: Hello there.\nSpeaker 2: Hi! How are you?\nSpeaker 1: I'm good, thanks."
    transcript = parser.parse_transcript(raw_text)
    assert transcript.get_raw_text() == raw_text
    assert transcript.get_normalized_text() == "speaker 1: hello there. speaker 2: hi! how are you? speaker 1: i'm good, thanks."
    assert set(transcript.get_speakers()) == {"Speaker 1", "Speaker 2"}
    assert isinstance(transcript.get_timestamp(), str)
    assert transcript.get_timestamp() ==  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")    













