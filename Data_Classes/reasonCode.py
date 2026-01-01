'''
File Name: reasonCode.py
Description: Data Class for Reason Code
'''

class reasonCode:
    def __init__(self,code:str, is_escalation: bool, score: int):
        self._code = code
        self._is_escalation = is_escalation
        self._score = score

    #Getters
    def get_code(self) -> str:
        return self._code
    
    def get_is_escalation(self) -> bool:
        return self._is_escalation
    
    def get_score(self) -> int:
        return self._score
    
    #Setters
    def set_code(self, code: str):
        self._code = code

    def set_is_escalation(self, is_escalation: bool):
        self._is_escalation = is_escalation

    def set_score(self, score: int):
        self._score = score

        
    #Defining __str__ method
    def __str__(self) -> str:
        return f"ReasonCode(code={self._code}, is_escalation={self._is_escalation}, score={self._score})"
    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()
