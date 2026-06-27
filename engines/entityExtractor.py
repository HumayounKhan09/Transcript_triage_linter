"""
File Name: entityExtractor.py
Description: Entity Extractor Engine
"""
import re
from Data_Classes.entities import Entities
from Data_Classes.transcript import transcript as Transcript

# ---------------------------------------------------------------------------
# Pre-compiled patterns — built once at import time, reused on every call
# ---------------------------------------------------------------------------
_NUM      = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_PREFIX   = r"(?:(?:US|CA|C)?\$\s*|(?:USD|CAD)\s*)"
_SUFFIX   = r"(?:\s*(?:USD|CAD|dollars?))\b"
_MAG      = r"(?:\s*(?:k\b|m\b|b\b|bn\b|thousand\b|million\b|billion\b))"
_CTX_KW   = r"(?:mortgage\s+amount|mortgage\s+balance|principal\s+balance|loan\s+amount|borrow(?:ing)?\s+amount|purchase\s+price|home\s+price|price)"

_MONEY_RE = re.compile(rf"""
    (?<!\w)
    (
        {_PREFIX}{_NUM}(?:{_MAG})?(?:{_SUFFIX})?
      | {_NUM}{_MAG}(?:{_SUFFIX})?
      | {_NUM}{_SUFFIX}
    )
    (?!\w)
""", re.IGNORECASE | re.VERBOSE)

_BARE_RE = re.compile(
    rf"""\b{_CTX_KW}\b\s*(?:is|:)?\s*({_NUM})\b""",
    re.IGNORECASE | re.VERBOSE,
)

_DATE_RES = [
    re.compile(r'\b(?:\d{1,2}[/-]){2}\d{2,4}\b'),
    re.compile(r'\b\d{4}[/-](?:\d{1,2}[/-]){2}\d{1,2}\b'),
    re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE),
    re.compile(r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4}\b', re.IGNORECASE),
    re.compile(r'\b\d{1,2}[ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\b', re.IGNORECASE),
    re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\b', re.IGNORECASE),
]

_PHONE_RE = re.compile(r"""
    (?<!\w)
    (?:\+?1[\s.-]?)?
    (?:\(?\d{3}\)?[\s.-]?)
    \d{3}[\s.-]?
    \d{4}
    (?!\w)
""", re.VERBOSE)

_LOAN_RES = [
    re.compile(r'\bLN-\d{4,15}\b'),
    re.compile(r'\b(?:loan|account|reference|application|file)\s*(?:number|no\.?|#)\s*(?:is\s*)?(\d{4,20})\b', re.IGNORECASE),
]

# Magnitude / currency tokens for to_number
_BN_RE     = re.compile(r"\b(billion|bn)\b")
_MIL_RE    = re.compile(r"\bmillion\b")
_THOU_RE   = re.compile(r"\bthousand\b")
_KMB_RE    = re.compile(r"\b(k|m|b)\b")


class entityExtractor:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_number(raw: str):
        s = raw.strip().lower()
        s = s.replace('usd', '').replace('cad', '').replace('dollars', '').replace('dollar', '')
        s = s.replace('$', '').strip()

        mult = 1.0
        if _BN_RE.search(s):
            mult = 1_000_000_000.0
            s = _BN_RE.sub('', s).strip()
        elif _MIL_RE.search(s):
            mult = 1_000_000.0
            s = _MIL_RE.sub('', s).strip()
        elif _THOU_RE.search(s):
            mult = 1_000.0
            s = _THOU_RE.sub('', s).strip()
        else:
            m2 = _KMB_RE.search(s)
            if m2:
                tag = m2.group(1)
                mult = 1_000.0 if tag == 'k' else 1_000_000.0 if tag == 'm' else 1_000_000_000.0
                s = _KMB_RE.sub('', s).strip()

        s = s.replace(',', '').strip()
        if not s:
            return None
        try:
            val = float(s) * mult
        except ValueError:
            return None

        has_marker = any(x in raw.lower() for x in ['$', 'usd', 'cad', 'dollar', 'k', 'm', 'b', 'thousand', 'million', 'billion', 'bn'])
        if not has_marker and 100.0 <= val < 10000.0:
            val *= 1000.0

        if abs(val - round(val)) < 1e-9:
            return int(round(val))
        return val

    def _extract_amounts_with_context(self, text: str) -> list[tuple]:
        raw_hits = []
        raw_contexts = []
        for m in _MONEY_RE.finditer(text):
            raw_hits.append(m.group(1))
            raw_contexts.append(text[max(0, m.start() - 40):m.end() + 40].strip())
        for m in _BARE_RE.finditer(text):
            raw_hits.append(m.group(1))
            raw_contexts.append(text[max(0, m.start() - 40):m.end() + 40].strip())

        seen = set()
        uniq = []
        for h, ctx in zip(raw_hits, raw_contexts):
            v = self._to_number(h)
            if v is not None and v not in seen:
                seen.add(v)
                uniq.append((v, ctx))
        return uniq

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_amounts(self, text: str) -> list:
        """Return flat list of numeric amounts (backward-compatible)."""
        return [v for v, _ in self._extract_amounts_with_context(text)]

    def extract_amounts_with_context(self, text: str) -> list[tuple]:
        """Return list of (amount, context_snippet) pairs."""
        return self._extract_amounts_with_context(text)

    def extract_dates(self, text: str) -> list:
        dates = []
        for pattern in _DATE_RES:
            dates.extend(m.group(0) for m in pattern.finditer(text))
        return dates

    def extract_phones(self, text: str) -> list:
        return [m.group(0) for m in _PHONE_RE.finditer(text)]

    def extract_loan_numbers(self, text: str) -> list:
        hits = []
        for pat in _LOAN_RES:
            for m in pat.finditer(text):
                hits.append(m.group(1) if m.lastindex else m.group(0))

        seen = set()
        uniq = []
        for h in hits:
            if h not in seen:
                seen.add(h)
                uniq.append(h)
        return uniq

    # Backwards-compatible alias (old misspelling)
    def extract_loan_numbesrs(self, text: str) -> list:
        return self.extract_loan_numbers(text)

    def extract_all_entities(self, transcript: Transcript) -> Entities:
        text = transcript.get_normalized_text()
        pairs = self._extract_amounts_with_context(text)
        return Entities(
            amounts=[v for v, _ in pairs],
            amount_contexts=[ctx for _, ctx in pairs],
            dates=self.extract_dates(text),
            phones=self.extract_phones(text),
            loan_numbers=self.extract_loan_numbers(text),
        )
