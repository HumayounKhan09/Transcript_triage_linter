"""
File Name: escalationEngine.py
Description: Engine to handle escalation logic
"""

# Imports
from Data_Classes.reasonCode import reasonCode

class escalationEngine:
    def __init__(self):
        pass

    def _count_escalation_reasons(self, reasonCodes: list[reasonCode]) -> int:
        escalation_count = 0
        for rc in reasonCodes:
            if rc.get_is_escalation():
                escalation_count += 1
        return escalation_count
    
    def _has_escalation_trigger(self, reasonCodes: list[reasonCode]) -> bool:
        for rc in reasonCodes:
            if rc.get_is_escalation():
                return True
        return False
    
    def _calculate_risk_level(self, reasonCodes: list[reasonCode]) -> str:
        total_score = self._count_escalation_reasons(reasonCodes)
        if total_score >= 2:
            return "HIGH"
        elif total_score >= 1:
            return "MEDIUM"
        else:
            return "LOW"
        
    def evaluate_escalation(self, reasonCodes: list[reasonCode]) -> dict:
        escalation_needed = self._has_escalation_trigger(reasonCodes)
        risk_level = self._calculate_risk_level(reasonCodes)
        return {
            "escalation_needed": escalation_needed,
            "risk_level": risk_level
        }
    
        
    