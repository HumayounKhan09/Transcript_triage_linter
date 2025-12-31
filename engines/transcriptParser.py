"""
File Name: transcriptParser.py
Description: Parser for transcript data
"""
from Data_Classes.transcript import transcript
from datetime import datetime
class transcriptParser:
    def __init__(self):
        pass

    def _normalize_text(self, raw_text: str) -> str:
        # Example normalization: lowercasing and removing extra spaces
        normalized = ' '.join(raw_text.lower().split())
        return normalized
    
        
    def _getSpeakers(self, raw_text: str) -> list:
        # Example speaker extraction: assuming speakers are denoted by "Speaker 1:", "Speaker 2:", etc.
        speakers = set()
        lines = raw_text.split('\n')
        for line in lines:
            if ':' in line:
                speaker = line.split(':')[0].strip()
                speakers.add(speaker)
        return list(speakers)
    
    def parse_transcript(self, raw_text: str) -> transcript:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        normalized_text = self._normalize_text(raw_text)
        speakers = self._getSpeakers(raw_text)
        return transcript(raw_text, normalized_text, speakers, timestamp)