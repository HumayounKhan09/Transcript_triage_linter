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

    # Keywords that suggest what role a nearby amount plays
    _CONTEXT_LABELS = [
        (["monthly payment", "payment amount", "pay per month", "monthly mortgage"], "monthly payment"),
        (["principal balance", "loan balance", "remaining balance", "outstanding balance", "current balance"], "loan balance"),
        (["loan amount", "mortgage amount", "original loan", "borrow"], "loan amount"),
        (["purchase price", "home price", "sale price", "property value", "appraised"], "property value"),
        (["escrow shortage", "escrow deficiency"], "escrow shortage"),
        (["escrow", "impound", "property tax", "insurance premium"], "escrow amount"),
        (["late fee", "convenience fee", "processing fee", "fee"], "fee"),
        (["down payment", "down-payment"], "down payment"),
        (["payoff", "pay off", "pay-off"], "payoff amount"),
        (["forbearance", "deferral", "deferred"], "deferred amount"),
        (["arrears", "past due", "overdue", "behind"], "amount past due"),
    ]

    def _label_from_context(self, ctx: str) -> str:
        """Map a raw context snippet to a human-readable label."""
        lower = ctx.lower()
        for keywords, label in self._CONTEXT_LABELS:
            if any(kw in lower for kw in keywords):
                return label
        return ""

    def extract_payment_bullet(self, entities: Entities) -> Optional[str]:
        """Generate bullet about payment amounts, with context labels where available."""
        amounts = entities.get_amounts()
        if not amounts:
            return None

        contexts = entities.get_amount_contexts()

        def fmt(amount, ctx):
            label = self._label_from_context(ctx)
            s = f"${amount:,.2f}"
            return f"{s} ({label})" if label else s

        if len(amounts) == 1:
            formatted = fmt(amounts[0], contexts[0] if contexts else "")
            return f"Borrower mentioned payment amount of {formatted}"
        else:
            amt_str = ', '.join(fmt(a, contexts[i] if i < len(contexts) else "") for i, a in enumerate(amounts))
            return f"Borrower discussed multiple amounts: {amt_str}"

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






      
        



    
        
