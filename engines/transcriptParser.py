"""
File Name: transcriptParser.py
Description: Parser for transcript data
"""
from Data_Classes.transcript import transcript
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
    
    
