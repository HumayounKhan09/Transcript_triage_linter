'''
File Name: intentClassifier.py
Description: Intent Classifier Engine
'''

#imports
from Data_Classes.reasonCode import reasonCode
# from Data_Classes.triageResult import _NORMAL_RULES

class intentClassifier:
    def __intit__(self):
        pass

    def classify(self, reasonCodes: list[reasonCode]) -> str:
        hard= 0
        loanMod = 0
        banc= 0
        legal= 0
        dispFee= 0
        superv=  0
        abusive = 0
        tpc = 0

        pay= 0
        escrow = 0
        newLoan= 0

        max = 0
        max_code = "NONE"

        for rc in reasonCodes:
            if rc.get_code() == "HARDSHIP":
                hard = rc.get_score()
                if hard > max:
                    max = hard
                    max_code = "HARDSHIP"

            elif rc.get_code() == "LOAN_MOD_REQUEST":
                loanMod = rc.get_score()
                if loanMod > max:
                    max = loanMod
                    max_code = "LOAN_MOD_REQUEST"   

            elif rc.get_code() == "BANKRUPTCY_OR_LAWYER":
                banc = rc.get_score()
                if banc > max:
                    max = banc
                    max_code = "BANKRUPTCY_OR_LAWYER"

            elif rc.get_code() == "LEGAL_THREAT":
                legal = rc.get_score()
                if legal > max:
                    max = legal
                    max_code = "LEGAL_THREAT"

            elif rc.get_code() == "DISPUTE_FEE":
                dispFee = rc.get_score()
                if dispFee > max:
                    max = dispFee
                    max_code = "DISPUTE_FEE"

            elif rc.get_code() == "SUPERVISOR_REQUEST":
                superv = rc.get_score()
                if superv > max:
                    max = superv
                    max_code = "SUPERVISOR_REQUEST"

            elif rc.get_code() == "ABUSIVE_LANGUAGE":
                abusive = rc.get_score()
                if abusive > max:
                    max = abusive
                    max_code = "ABUSIVE_LANGUAGE"

            elif rc.get_code() == "THIRD_PARTY_CALLER":
                tpc = rc.get_score()
                if tpc > max:
                    max = tpc
                    max_code = "THIRD_PARTY_CALLER"

            elif rc.get_code() == "PAYMENT_INTENT":
                pay = rc.get_score()
                if pay > max:
                    max = pay
                    max_code = "PAYMENT_INTENT"

            elif rc.get_code() == "ESCROW_QUESTION":
                escrow = rc.get_score()
                if escrow > max:
                    max = escrow
                    max_code = "ESCROW_QUESTION"

            elif rc.get_code() == "NEW_LOAN_INQUIRY":
                newLoan = rc.get_score()
                if newLoan > max:
                    max = newLoan
                    max_code = "NEW_LOAN_INQUIRY"

        return max_code
            
              
            


    