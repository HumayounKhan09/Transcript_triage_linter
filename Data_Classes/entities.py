'''
File Name: entities.py
Description: Data Class for Entities
'''

class Entities:
    def __init__(self, amounts: list, dates: list, phones: list, loan_numbers: list, amount_contexts: list = None):
        self._amounts = amounts
        self._amount_contexts = amount_contexts if amount_contexts is not None else [""] * len(amounts)
        self._dates = dates
        self._phones = phones
        self._loan_numbers = loan_numbers

    #Getters
    def get_amounts(self) -> list:
        return self._amounts

    def get_amount_contexts(self) -> list[str]:
        return self._amount_contexts

    def get_dates(self) -> list:
        return self._dates

    def get_phones(self) -> list:
        return self._phones

    def get_loan_numbers(self) -> list:
        return self._loan_numbers

    #Defining __str__ method
    def __str__(self) -> str:
        return f"Entities(amounts={self._amounts}, dates={self._dates}, phones={self._phones}, loan_numbers={self._loan_numbers})"

    #Defining __repr__ method
    def __repr__(self) -> str:
        return self.__str__()
