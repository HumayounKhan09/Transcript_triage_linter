'''
File Name: triageResult.py
Description: Data Class for triageResult
'''
from Data_Classes.reasonCode import reasonCode
from Data_Classes.entities import Entities  

class triageResult:
    def __init__(self, intent: str, escalate: bool, risk_level: str, reason_codes: list[reasonCode], entities: Entities, summary_bullet: list[str]):
        self._intent = intent
        self._escalate = escalate
        self._risk_level = risk_level
        self._reason_codes = reason_codes
        self._entities = entities
        self._summary_bullet = summary_bullet

    #Getters
    def get_reason_codes(self) -> list[reasonCode]:
        return self._reason_codes

    def to_json(self) -> dict:
        return {
            "intent": self._intent,
            "escalate": self._escalate,
            "risk_level": self._risk_level,
            "reason_codes": [rc.__dict__ for rc in self._reason_codes],
            "entities": self._entities,
            "summary_bullet": self._summary_bullet
        }
    
    #Defining __str__ method
    def __str__(self) -> str:
        return f"triageResult(intent={self._intent}, escalate={self._escalate}, risk_level={self._risk_level}, reason_codes={self._reason_codes}, entities={self._entities}, summary_bullet={self._summary_bullet})"
    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()   
    
 
    
  
      
