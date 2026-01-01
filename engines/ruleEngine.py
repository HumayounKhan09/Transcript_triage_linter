'''
File Name: ruleEngine.py
Description: Rule Engine for processing transcripts
'''

from Data_Classes.transcript import transcript as Transcript
from Data_Classes.reasonCode import reasonCode


class ruleEngine:
    _ESCALATION_RULES = {
    "HARDSHIP_LANGUAGE": {
        "keywords": ["lost my job", "unemployed", "can't afford", "can't pay", "financial hardship", "struggling", "behind on payments", "medical bills", "reduced income", "laid off"],
        "single_words": ["unemployed", "struggling", "hardship"]
    },
    "LOAN_MOD_REQUEST": {
        "keywords": ["loan modification", "modify my loan", "modify the loan", "payment plan", "forbearance", "restructure", "lower my payment", "reduce my payment"],
        "single_words": ["forbearance"]
    },
    "BANKRUPTCY_OR_LAWYER": {
        "keywords": ["filed bankruptcy", "filing bankruptcy", "chapter 7", "chapter 13", "my lawyer", "my attorney", "retained counsel", "legal counsel"],
        "single_words": ["bankruptcy", "lawyer", "attorney"]
    },
    "LEGAL_THREAT": {
        "keywords": ["sue you", "legal action", "attorney general", "consumer protection", "better business bureau", "lawsuit", "take legal action", "report you"],
        "single_words": []
    },
    "DISPUTE_FEE_OR_CHARGE": {
        "keywords": ["dispute this charge", "don't owe this", "unauthorized charge", "never agreed", "incorrect fee", "wrong fee", "late fee is wrong"],
        "single_words": ["dispute"]
    },
    "SUPERVISOR_REQUEST": {
        "keywords": ["speak to supervisor", "talk to manager", "your supervisor", "escalate this", "someone above you", "your boss", "speak to someone else"],
        "single_words": ["supervisor", "manager"]
    },
    "ABUSIVE_LANGUAGE": {
        "keywords": ["you're an idiot", "you're stupid", "this is ridiculous"],
        "single_words": ["idiot", "stupid", "ridiculous", "useless"]
    },
    "THIRD_PARTY_CALLER": {
        "keywords": ["calling for my husband", "calling for my wife", "my mom's account", "my son's loan", "power of attorney", "calling on behalf"],
        "single_words": []
    }
}

    _NORMAL_RULES = {
        "PAYMENT_INTENT": {
            "keywords": ["make a payment", "pay my mortgage", "send a payment", "payment amount", "pay online", "what's my balance"],
            "single_words": ["payment", "balance"]
        },
        "ESCROW_QUESTION": {
            "keywords": ["escrow account", "property taxes", "insurance", "escrow analysis", "escrow shortage", "impound account", "tax escrow"],
            "single_words": ["escrow"]
        },
        "NEW_LOAN_INQUIRY": {
            "keywords": ["refinance", "new loan", "apply for mortgage", "current rates", "pre-approval", "home equity loan", "rate quote"],
            "single_words": ["refinance", "refinancing"]
        }
    }

    def __init__(self, transcript: Transcript):
        self._transcript = transcript
        self._normalized_text = transcript.get_normalized_text().lower()

    def _check_hardship(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["HARDSHIP_LANGUAGE"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["HARDSHIP_LANGUAGE"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _check_loan_mod_request(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["LOAN_MOD_REQUEST"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["LOAN_MOD_REQUEST"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _check_bankruptcy_or_lawyer(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["BANKRUPTCY_OR_LAWYER"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["BANKRUPTCY_OR_LAWYER"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points   
    
    def _check_legal_threat(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["LEGAL_THREAT"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["LEGAL_THREAT"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _dispute_fee(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["DISPUTE_FEE_OR_CHARGE"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["DISPUTE_FEE_OR_CHARGE"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _check_supervisor_request(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["SUPERVISOR_REQUEST"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["SUPERVISOR_REQUEST"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    def _check_abusive_language(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["ABUSIVE_LANGUAGE"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["ABUSIVE_LANGUAGE"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    def _check_third_party_caller(self)->int:
        points = 0
        for keyword in self._ESCALATION_RULES["THIRD_PARTY_CALLER"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._ESCALATION_RULES["THIRD_PARTY_CALLER"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points   
    
    def _check_payment_intent(self)->int:
        points = 0
        for keyword in self._NORMAL_RULES["PAYMENT_INTENT"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._NORMAL_RULES["PAYMENT_INTENT"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _check_escrow_question(self)->int:
        points = 0
        for keyword in self._NORMAL_RULES["ESCROW_QUESTION"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._NORMAL_RULES["ESCROW_QUESTION"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def _check_new_loan_inquiry(self)->int:
        points = 0
        for keyword in self._NORMAL_RULES["NEW_LOAN_INQUIRY"]["keywords"]:
            if keyword in self._normalized_text:
                points += 2
        for word in self._NORMAL_RULES["NEW_LOAN_INQUIRY"]["single_words"]:
            if word in self._normalized_text:
                points += 1
        return points
    
    def apply_rules(self) -> list[reasonCode]:
        reason_codes = []
        threshold = 2

        es = False
        hard= self._check_hardship() 
        loanMod = self._check_loan_mod_request()
        banc= self._check_bankruptcy_or_lawyer() 
        legal= self._check_legal_threat()
        dispFee= self._dispute_fee() 
        superv=  self._check_supervisor_request()  
        abusive =self._check_abusive_language() 
        tpc = self._check_third_party_caller() 
   
        
        # Check normal rules
        pay= self._check_payment_intent()
        escrow = self._check_escrow_question() 
        newLoan= self._check_new_loan_inquiry()
           

        # Check escalation rules
        if hard >= threshold:
            reason_codes.append(reasonCode("HARDSHIP_LANGUAGE", not es, hard))
        if loanMod >= threshold: 
            reason_codes.append(reasonCode("LOAN_MOD_REQUEST", not es, loanMod))
        if banc >= threshold:
            reason_codes.append(reasonCode("BANKRUPTCY_OR_LAWYER", not es, banc))
        if legal >= threshold:
            reason_codes.append(reasonCode("LEGAL_THREAT", not es, legal))
        if dispFee >= threshold:
            reason_codes.append(reasonCode("DISPUTE_FEE_OR_CHARGE", not es, dispFee))
        if superv >= threshold:
            reason_codes.append(reasonCode("SUPERVISOR_REQUEST", not es,superv))
        if abusive >= threshold:
            reason_codes.append(reasonCode("ABUSIVE_LANGUAGE", not es, abusive))
        if tpc >= threshold:
            reason_codes.append(reasonCode("THIRD_PARTY_CALLER", not es, tpc))
        
        # Check normal rules
        if pay >= threshold:
            reason_codes.append(reasonCode("PAYMENT_INTENT",  es, pay))
        if escrow >= threshold:
            reason_codes.append(reasonCode("ESCROW_QUESTION", es, escrow))
        if newLoan >= threshold:
            reason_codes.append(reasonCode("NEW_LOAN_INQUIRY", es, newLoan))
        
        return reason_codes




