'''
File Name: ruleEngine.py
Description: Rule Engine for processing transcripts
'''

import re
from Data_Classes.transcript import transcript as Transcript
from Data_Classes.reasonCode import reasonCode


_THRESHOLD = 2

# ---------------------------------------------------------------------------
# Rule definitions — stored as tuples of (keywords, single_words) for fast
# string `in` checks (Python's built-in string search is faster than regex
# for short literal phrases against long text).
# ---------------------------------------------------------------------------
_ESCALATION_RULES = {
    "HARDSHIP_LANGUAGE": (
        ["lost my job", "unemployed", "can't afford", "can't pay", "financial hardship",
         "struggling", "behind on payments", "medical bills", "reduced income", "laid off"],
        ["unemployed", "struggling", "hardship"],
    ),
    "LOAN_MOD_REQUEST": (
        ["loan modification", "modify my loan", "modify the loan", "payment plan",
         "forbearance", "restructure", "lower my payment", "reduce my payment"],
        ["forbearance"],
    ),
    "BANKRUPTCY_OR_LAWYER": (
        ["filed bankruptcy", "filing bankruptcy", "chapter 7", "chapter 13",
         "my lawyer", "my attorney", "retained counsel", "legal counsel"],
        ["bankruptcy", "lawyer", "attorney"],
    ),
    "LEGAL_THREAT": (
        ["sue you", "legal action", "attorney general", "consumer protection",
         "better business bureau", "lawsuit", "take legal action", "report you"],
        [],
    ),
    "DISPUTE_FEE_OR_CHARGE": (
        ["dispute this charge", "don't owe this", "unauthorized charge", "never agreed",
         "incorrect fee", "wrong fee", "late fee is wrong"],
        ["dispute"],
    ),
    "SUPERVISOR_REQUEST": (
        ["speak to supervisor", "talk to manager", "your supervisor", "escalate this",
         "someone above you", "your boss", "speak to someone else"],
        ["supervisor", "manager"],
    ),
    "ABUSIVE_LANGUAGE": (
        ["you're an idiot", "you're stupid", "this is ridiculous"],
        ["idiot", "stupid", "ridiculous", "useless"],
    ),
    "THIRD_PARTY_CALLER": (
        ["calling for my husband", "calling for my wife", "my mom's account",
         "my son's loan", "power of attorney", "calling on behalf"],
        [],
    ),
}

_NORMAL_RULES = {
    "PAYMENT_INTENT": (
        ["make a payment", "pay my mortgage", "send a payment", "payment amount",
         "pay online", "what's my balance"],
        ["payment", "balance"],
    ),
    "ESCROW_QUESTION": (
        ["escrow account", "property taxes", "insurance", "escrow analysis",
         "escrow shortage", "impound account", "tax escrow"],
        ["escrow"],
    ),
    "NEW_LOAN_INQUIRY": (
        ["refinance", "new loan", "apply for mortgage", "current rates",
         "pre-approval", "home equity loan", "rate quote"],
        ["refinance", "refinancing"],
    ),
}


def _score(keywords: list, single_words: list, text: str) -> int:
    """Score a rule against normalised text using fast string containment checks."""
    pts = sum(2 for kw in keywords if kw in text)
    pts += sum(1 for w in single_words if w in text)
    return pts


class ruleEngine:
    # Keep originals accessible for any code that inspects them
    ESCALATION_RULES = {
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

    NORMAL_RULES = {
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

    def apply_rules(self) -> list[reasonCode]:
        text = self._normalized_text
        reason_codes = []

        scores = {name: _score(kws, words, text) for name, (kws, words) in _ESCALATION_RULES.items()}
        scores.update({name: _score(kws, words, text) for name, (kws, words) in _NORMAL_RULES.items()})

        any_escalation = any(scores[name] >= _THRESHOLD for name in _ESCALATION_RULES)

        for name in _ESCALATION_RULES:
            if scores[name] >= _THRESHOLD:
                reason_codes.append(reasonCode(name, any_escalation, scores[name]))

        for name in _NORMAL_RULES:
            if scores[name] >= _THRESHOLD:
                reason_codes.append(reasonCode(name, any_escalation, scores[name]))

        return reason_codes
