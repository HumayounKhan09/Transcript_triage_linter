"""
File Name: summaryGenerator.py
Description: Engine to generate summary bullets from transcript
"""

from typing import Optional
from Data_Classes.entities import Entities


class summaryGenerator:
    def __init__(self):
        # Define escalation codes for reference
        self.escalation_codes = [
            "HARDSHIP_LANGUAGE",
            "LOAN_MOD_REQUEST", 
            "BANKRUPTCY_OR_LAWYER",
            "LEGAL_THREAT",
            "DISPUTE_FEE_OR_CHARGE",
            "SUPERVISOR_REQUEST",
            "ABUSIVE_LANGUAGE",
            "THIRD_PARTY_CALLER"
        ]

    def extract_payment_bullet(self, entities: Entities) -> Optional[str]:
        """Generate bullet about payment amounts"""
        amounts = entities.get_amounts()
        if len(amounts) > 0:
            if len(amounts) == 1:
                return f"Borrower mentioned payment amount of ${amounts[0]:,.2f}"
            else:
                amt_str = ', '.join([f"${a:,.2f}" for a in amounts])
                return f"Borrower discussed multiple amounts: {amt_str}"
        return None

    def extract_request_bullet(self, intent: str, reason_codes: list) -> Optional[str]:
        """Generate bullet about what customer requested based on intent"""
        code_names = [rc.get_code() for rc in reason_codes]
        
        if intent == "payment":
            return "Borrower requested to make a payment"
        elif intent == "hardship":
            if "LOAN_MOD_REQUEST" in code_names:
                return "Requested loan modification due to financial hardship"
            else:
                return "Mentioned financial difficulties affecting payments"
        elif intent == "escrow":
            return "Asked about escrow account details"
        elif intent == "dispute":
            return "Disputed charges or fees on account"
        elif intent == "new-loan":
            return "Inquired about refinancing or new loan options"
        else:
            return "General inquiry about account"

    def extract_escalation_bullet(self, reason_codes: list) -> Optional[str]:
        """Generate bullet explaining why call was escalated"""
        code_names = [rc.get_code() for rc in reason_codes]
        
        # Filter to only escalation codes
        escalation_triggers = [code for code in code_names if code in self.escalation_codes]
        
        if not escalation_triggers:
            return None
        
        # Build human-readable reasons
        reasons = []
        if "HARDSHIP_LANGUAGE" in escalation_triggers:
            reasons.append("financial hardship mentioned")
        if "LOAN_MOD_REQUEST" in escalation_triggers:
            reasons.append("loan modification requested")
        if "BANKRUPTCY_OR_LAWYER" in escalation_triggers:
            reasons.append("bankruptcy or legal counsel referenced")
        if "LEGAL_THREAT" in escalation_triggers:
            reasons.append("legal action threatened")
        if "DISPUTE_FEE_OR_CHARGE" in escalation_triggers:
            reasons.append("fee dispute")
        if "SUPERVISOR_REQUEST" in escalation_triggers:
            reasons.append("supervisor requested")
        if "ABUSIVE_LANGUAGE" in escalation_triggers:
            reasons.append("abusive language used")
        if "THIRD_PARTY_CALLER" in escalation_triggers:
            reasons.append("third party caller (unauthorized)")
        
        if len(reasons) == 1:
            return f"Call escalated due to: {reasons[0]}"
        else:
            return f"Call escalated due to: {', '.join(reasons)}"

    def format_bullet(self, text: str) -> str:
        """Format a bullet point nicely"""
        if not text:
            return ""
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Ensure it ends with period
        if not text.endswith('.'):
            text += '.'
        
        return text

    def generate_bullets(self, intent: str, entities: Entities, reason_codes: list) -> list[str]:
        """Generate 2-4 summary bullets for the call"""
        bullets = []
        
        # Always try to add request bullet (what they want)
        request_bullet = self.extract_request_bullet(intent, reason_codes)
        if request_bullet:
            bullets.append(self.format_bullet(request_bullet))
        
        # Add payment bullet if amounts were mentioned
        payment_bullet = self.extract_payment_bullet(entities)
        if payment_bullet:
            bullets.append(self.format_bullet(payment_bullet))
        
        # Add escalation bullet if escalation occurred
        escalation_bullet = self.extract_escalation_bullet(reason_codes)
        if escalation_bullet:
            bullets.append(self.format_bullet(escalation_bullet))
        
        # If we have no bullets at all, add a generic one
        if not bullets:
            bullets.append("Customer contacted regarding account inquiry.")
        
        return bullets






      
        



    
        
