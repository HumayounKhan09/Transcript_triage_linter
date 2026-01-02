"""
File Name: summaryGenerator.py
Description: Engine to generate summary bullets from transcript
"""

from html import entities
from tkinter import NONE
from Data_Classes.entities import Entities


class summaryGenerator:
    def __init__(self):
        pass

    def _extract_payment_info(self, entities: Entities) -> str:
        amounts = entities.get_amounts()
        if amounts:
            return f"Payment amount mentioned: {', '.join(amounts)}."
        return NONE
    



    
        
