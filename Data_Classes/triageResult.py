'''
File Name: triageResult.py
Description: Data Class for triageResult
'''
from Data_Classes.reasonCode import reasonCode
from Data_Classes.entities import entities  

class triageResult:
    def __init__(self, intent: str, escalate: bool, risk_level: str, reason_codes: list[reasonCode], key_entities: list[entities], summary_bullet: list[str]):
        self._intent = intent
        self._escalate = escalate
        self._risk_level = risk_level
        self._reason_codes = reason_codes
        self._key_entities = key_entities
        self._summary_bullet = summary_bullet

    def to_json(self) -> dict:
        return {
            "intent": self._intent,
            "escalate": self._escalate,
            "risk_level": self._risk_level,
            "reason_codes": [rc.__dict__ for rc in self._reason_codes],
            "key_entities": [ke.__dict__ for ke in self._key_entities],
            "summary_bullet": self._summary_bullet
        }
    
  
      
