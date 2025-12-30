'''
File Name: entities.py
Description: Data Class for Entities
'''

class entities:
    def __init__(self, name: str, entity_type: str, relevance: float):
        self._name = name
        self._entity_type = entity_type
        self._relevance = relevance

    #Getters
    def get_name(self) -> str:
        return self._name
    
    def get_entity_type(self) -> str:
        return self._entity_type
    
    def get_relevance(self) -> float:
        return self._relevance
    
    #Setters
    def set_name(self, name: str):
        self._name = name

    def set_entity_type(self, entity_type: str):
        self._entity_type = entity_type

    def set_relevance(self, relevance: float):
        self._relevance = relevance

        
    #Defining __str__ method
    def __str__(self) -> str:
        return f"Entities(name={self._name}, entity_type={self._entity_type}, relevance={self._relevance})"
    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()