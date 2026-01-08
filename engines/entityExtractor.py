"""
File Name: entityExtractor.py
Description: Entity Extractor Engine
"""
from Data_Classes.entities import Entities
from Data_Classes.transcript import transcript as Transcript
import re  #This is the regex library

class entityExtractor:
    def __init__(self):
        pass

    def extract_amounts(self, text: str) -> list:
        """Extract monetary amounts from normalized mortgage transcripts.

        Returns ONLY numeric amounts (ints when whole dollars, floats if decimals).
        Handles:
          - $850,000 / USD 850000 / 850000 dollars
          - 850k / 1.25m / 3 million / 2.4 billion
          - Bare digits near mortgage-ish keywords: "mortgage amount 850" -> 850000
        """
        # --- 1) Money patterns with explicit currency/magnitude ---
        num = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
        prefix = r"(?:(?:US|CA|C)?\$\s*|(?:USD|CAD)\s*)"
        suffix = r"(?:\s*(?:USD|CAD|dollars?))\b"
        mag = r"(?:\s*(?:k\b|m\b|b\b|bn\b|thousand\b|million\b|billion\b))"

        money_pattern = rf"""
            (?<!\w)
            (
                {prefix}{num}(?:{mag})?(?:{suffix})?
              | {num}{mag}(?:{suffix})?
              | {num}{suffix}
            )
            (?!\w)
        """

        # --- 2) Bare digits near mortgage amount keywords (transcript-style) ---
        # We intentionally avoid matching "loan number" by requiring *amount-ish* keywords/phrases.
        ctx_kw = r"""(?:mortgage\s+amount|mortgage\s+balance|principal\s+balance|loan\s+amount|borrow(?:ing)?\s+amount|purchase\s+price|home\s+price|price)"""
        bare_pattern = rf"""\b{ctx_kw}\b\s*(?:is|:)?\s*({num})\b"""

        raw_hits = []
        raw_hits.extend([m.group(1) for m in re.finditer(money_pattern, text, flags=re.IGNORECASE | re.VERBOSE)])
        raw_hits.extend([m.group(1) for m in re.finditer(bare_pattern, text, flags=re.IGNORECASE | re.VERBOSE)])

        def to_number(raw: str):
            s = raw.strip().lower()
            # strip common currency tokens
            s = s.replace('usd', '').replace('cad', '').replace('dollars', '').replace('dollar', '')
            s = s.replace('$', '').strip()

            # magnitude
            mult = 1.0
            if re.search(r"\bbillion\b", s) or re.search(r"\bbn\b", s):
                mult = 1_000_000_000.0
                s = re.sub(r"\b(billion|bn)\b", "", s).strip()
            elif re.search(r"\bmillion\b", s):
                mult = 1_000_000.0
                s = re.sub(r"\bmillion\b", "", s).strip()
            elif re.search(r"\bthousand\b", s):
                mult = 1_000.0
                s = re.sub(r"\bthousand\b", "", s).strip()
            else:
                m2 = re.search(r"\b(k|m|b)\b", s)
                if m2:
                    tag = m2.group(1)
                    mult = 1_000.0 if tag == 'k' else 1_000_000.0 if tag == 'm' else 1_000_000_000.0
                    s = re.sub(r"\b(k|m|b)\b", "", s).strip()

            # clean commas/spaces
            s = s.replace(',', '').strip()
            if not s:
                return None

            try:
                val = float(s) * mult
            except ValueError:
                return None

            # Mortgage shorthand: if no explicit markers and it's "850" etc, interpret as thousands.
            has_marker = any(x in raw.lower() for x in ['$', 'usd', 'cad', 'dollar', 'k', 'm', 'b', 'thousand', 'million', 'billion', 'bn'])
            if not has_marker and 100.0 <= val < 10000.0:
                val *= 1000.0

            if abs(val - round(val)) < 1e-9:
                return int(round(val))
            return val

        nums = []
        for h in raw_hits:
            v = to_number(h)
            if v is not None:
                nums.append(v)

        # de-dupe while preserving order
        seen = set()
        uniq = []
        for v in nums:
            if v not in seen:
                seen.add(v)
                uniq.append(v)

        return uniq

    def extract_dates(self, text: str) -> list: 
        date_patterns = [
            r'\b(?:\d{1,2}[/-]){2}\d{2,4}\b',                # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-](?:\d{1,2}[/-]){2}\d{1,2}\b',      # YYYY/MM/DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',  # Month Day, Year
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4}\b',  # Day Month Year
            r'\b\d{1,2}[ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\b',  # Day Month
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\b'   # Month Day
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend([m.group(0) for m in re.finditer(pattern, text, flags=re.IGNORECASE)])
        return dates
    
    def extract_phones(self, text: str) -> list:
        phone_pattern = r'''
            (?<!\w)
            (?:\+?1[\s.-]?)?                # Optional country code
            (?:\(?\d{3}\)?[\s.-]?)          # Area code with optional parentheses
            \d{3}[\s.-]?                    # First 3 digits
            \d{4}                           # Last 4 digits
            (?!\w)
        '''
        return [m.group(0) for m in re.finditer(phone_pattern, text, flags=re.VERBOSE)]   
    
    
    def extract_loan_numbers(self, text: str) -> list:
        """Extract loan/account numbers from transcripts.

        Supports:
          - LN-123456 (legacy)
          - "loan number 12346" / "loan # 12346" / "account number is 12346"
        Returns strings (do NOT cast to int because leading zeros can matter).
        """
        patterns = [
            r'\bLN-\d{4,15}\b',
            r'\b(?:loan|account|reference|application|file)\s*(?:number|no\.?|#)\s*(?:is\s*)?(\d{4,20})\b',
        ]

        hits = []
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                if m.lastindex:
                    hits.append(m.group(1))
                else:
                    hits.append(m.group(0))

        # de-dupe while preserving order
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
        extEntities = Entities(
            amounts=self.extract_amounts(text),
            dates=self.extract_dates(text),
            phones=self.extract_phones(text),
            loan_numbers=self.extract_loan_numbers(text)
        )
        return extEntities