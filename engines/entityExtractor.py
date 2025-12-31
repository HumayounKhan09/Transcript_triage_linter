"""
File Name: entityExtractor.py
Description: Entity Extractor Engine
"""
from Data_Classes.transcript import transcript as Transcript
import re as r #This is the regex library

class entityExtractor:
    def __init__(self):
        pass

    def extract_amounts(self, text: str) -> list: 
        return []
    
    def extract_dates(self, text: str) -> list: 
        return []
    
    def extract_phones(self, text: str) -> list:
        return []
    
    def extract_loan_numbesrs(self, text: str) -> list:
        return [] 
    
    def extract_all_entities(self, transcript: Transcript) -> dict:
        text = transcript.get_normalized_text()
        entities = {
            "amounts": self.extract_amounts(text),
            "dates": self.extract_dates(text),
            "phones": self.extract_phones(text),
            "loan_numbers": self.extract_loan_numbesrs(text)
        }
        return entities