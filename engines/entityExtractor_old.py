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
        num = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
        prefix = r"(?:(?:US|CA|C)?\$\s*|(?:USD|CAD)\s+)"         # $, US$, C$, CA$, USD , CAD 
        suffix = r"(?:\s*(?:USD|CAD|dollars?))\b"               # USD/CAD/dollar(s)
        mag = r"(?:\s*(?:[kmb]\b|thousand\b|million\b|billion\b|bn\b))"  # k/m/b, thousand/million/billion/bn

        pattern = rf"""
            (?<!\w)
            (
                {prefix}{num}(?:{mag})?(?:{suffix})?   # $1,200.50 / USD 1200 / US$1.2k / CAD 3 million
            | {num}{mag}(?:{suffix})?                # 2k / 3 million / 1.5bn / 10k USD
            | {num}{suffix}                          # 1200 CAD / 100 dollars / 1,200 USD
            )
            (?!\w)
        """

        return [m.group(1) for m in r.finditer(pattern, text, flags=r.IGNORECASE | r.VERBOSE)]

    
    def extract_dates(self, text: str) -> list: 
        date_patterns = [
            r'\b(?:\d{1,2}[/-]){2}\d{2,4}\b',                # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-](?:\d{1,2}[/-]){2}\d{1,2}\b',      # YYYY/MM/DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',  # Month Day, Year
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4}\b',  # Day Month Year
            r'\b\d{1,2}[ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\b',  # Day Month
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\b'   # Month Day
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend([m.group(0) for m in r.finditer(pattern, text, flags=r.IGNORECASE)])
        return dates
    
    def extract_phones(self, text: str) -> list:
        phone_pattern = r'''
            (?<!\w)
            (?:\+?1[\s.-]?)?                # Optional country code
            (?:\(?\d{3}\)?[\s.-]?)          # Area code with optional parentheses
            \d{3}[\s.-]?                    # First 3 digits
            \d{4}                           # Last 4 digits
            (?!\w)
        '''
        return [m.group(0) for m in r.finditer(phone_pattern, text, flags=r.VERBOSE)]   
    
    
    def extract_loan_numbesrs(self, text: str) -> list:
        loan_pattern = r'\bLN-\d{6,10}\b'
        return [m.group(0) for m in r.finditer(loan_pattern, text)]
    
    def extract_all_entities(self, transcript: Transcript) -> dict:
        text = transcript.get_normalized_text()
        entities = {
            "amounts": self.extract_amounts(text),
            "dates": self.extract_dates(text),
            "phones": self.extract_phones(text),
            "loan_numbers": self.extract_loan_numbesrs(text)
        }
        return entities