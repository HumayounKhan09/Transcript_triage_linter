"""
This is my first experinece wihh writing my own testing
"""

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












