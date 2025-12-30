'''
File Name: reasonCode.py
Description: Data Class for Reason Code
'''

class reasonCode:
    def __init__(self,code:str, is_escalation: bool, confidence: float):
        self._code = code
        self._is_escalation = is_escalation
        self._confidence = confidence

    #Getters
    def get_code(self) -> str:
        return self._code
    
    def get_is_escalation(self) -> bool:
        return self._is_escalation
    
    def get_confidence(self) -> float:
        return self._confidence
    
    #Setters
    def set_code(self, code: str):
        self._code = code

    def set_is_escalation(self, is_escalation: bool):
        self._is_escalation = is_escalation

    def set_confidence(self, confidence: float):
        self._confidence = confidence

        
    #Defining __str__ method
    def __str__(self) -> str:
        return f"ReasonCode(code={self._code}, is_escalation={self._is_escalation}, confidence={self._confidence})"
    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()
    