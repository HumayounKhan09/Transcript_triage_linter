'''
File Name: transcript.py
Description: Data Class for transcript
'''

from datetime import datetime

class transcript:
    def __init__(self, raw_text: str,normalized_text: str, speakers: list,timestamp: datetime):
        self._raw_text = raw_text
        self._normalized_text = normalized_text
        self._speakers = speakers
        self._timestamp = timestamp
    
    #Defining Getters
    def get_raw_text(self) -> str:
        return self._raw_text
    def get_normalized_text(self) -> str:
        return self._normalized_text
    def get_speakers(self) -> list:
        return self._speakers
    def get_timestamp(self) -> datetime:
        return self._timestamp
    
    #Defining Setters
    def set_raw_text(self, raw_text: str):
        self._raw_text = raw_text
    def set_normalized_text(self, normalized_text: str):
        self._normalized_text = normalized_text
    def set_speakers(self, speakers: list):
        self._speakers = speakers
    def set_timestamp(self, timestamp: datetime):
        self._timestamp = timestamp

    #Defining __str__ method
    def __str__(self) -> str:
        return f"Transcript(raw_text={self._raw_text}, normalized_text={self._normalized_text}, speakers={self._speakers}, timestamp={self._timestamp})"
    
    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()       