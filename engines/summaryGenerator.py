"""
File Name: summaryGenerator.py
Description: Engine to generate summary bullets from transcript
"""

from tkinter import NONE
from typing import Optional
from Data_Classes.entities import Entities


class summaryGenerator:
    def __init__(self):
        pass

    def extract_payment_bulllet( self, entities: Entities) -> Optional[str]:
        payment = entities.get_amounts()
        if len(payment) > 0:
            return f"Payment Amounts Mentioned: {', '.join(str(p) for p in payment)}."
        return NONE
    

    
  
    






      
        



    
        
