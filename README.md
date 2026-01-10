# Transcript Triage Linter

A Python-based NLP pipeline for analyzing mortgage servicing call transcripts. Automatically classifies customer intent, detects escalation triggers, extracts key entities, and generates actionable summaries.

## Features

- **Intent Classification** — Identifies customer intent (payment, hardship, escrow inquiry, etc.)
- **Escalation Detection** — Flags calls requiring supervisor attention (legal threats, abusive language, etc.)
- **Risk Assessment** — Categorizes calls as LOW, MEDIUM, or HIGH risk
- **Entity Extraction** — Pulls out monetary amounts, dates, phone numbers, and loan numbers
- **Summary Generation** — Creates bullet-point summaries for call documentation
- **Batch Processing** — Process multiple transcripts with aggregate reporting

## Architecture

```
Transcript_triage_linter/
├── cli.py                    # Entry point
├── Data_Classes/
│   ├── entities.py           # Extracted entities model
│   ├── reasonCode.py         # Reason code model
│   ├── transcript.py         # Parsed transcript model
│   └── triageResult.py       # Final result model
├── engines/
│   ├── transcriptParser.py   # Text normalization & speaker extraction
│   ├── entityExtractor.py    # Regex-based entity extraction
│   ├── ruleEngine.py         # Keyword-based rule matching
│   ├── intentClassifier.py   # Intent classification from reason codes
│   ├── escalationEngine.py   # Risk level calculation
│   ├── summaryGenerator.py   # Bullet point generation
│   ├── batchReporter.py      # Batch metrics & CSV reporting
│   ├── triageResult.py       # Pipeline orchestration
│   └── cli.py                # CLI implementation
├── transcripts/              # Sample transcript files
├── results/                  # Output directory
└── testing/
    ├── fixtures/             # Unit tests
    └── integration/          # Integration tests
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Transcript_triage_linter.git
cd Transcript_triage_linter

# Install dependencies
pip install pandas pytest
```

## Usage

### Single Transcript

```bash
# JSON output
python cli.py --single transcripts/test_payment_simple_rambling.txt --format json

# CSV output
python cli.py --single transcripts/test_payment_simple_rambling.txt --format csv

# Both formats
python cli.py --single transcripts/test_payment_simple_rambling.txt --format both
```

### Batch Processing

```bash
# Process all transcripts in transcripts/ directory
python cli.py --batch --format csv
```

### List Available Transcripts

```bash
python cli.py --list
```

## Output Example

### JSON Output
```json
{
  "intent": "PAYMENT_INTENT",
  "escalate": false,
  "risk_level": "LOW",
  "reason_codes": ["PAYMENT_INTENT"],
  "entities": {
    "amounts": [2450],
    "dates": [],
    "phones": [],
    "loan_numbers": ["123456"]
  },
  "summary_bullet": [
    "Borrower requested to make a payment.",
    "Borrower mentioned payment amount of $2,450.00."
  ]
}
```

### Batch CSV Output
```
SUMMARY METRICS
Total Transcripts,12
Escalation Rate,66.7%
Top Intent,PAYMENT_INTENT (3)
Top Reason Code,ESCROW_QUESTION (7)

filename,intent,escalate,risk_level,reason_codes,summary
transcript_001.txt,PAYMENT_INTENT,False,LOW,PAYMENT_INTENT,Borrower requested to make a payment...
```

## Rule Categories

### Escalation Rules (Trigger supervisor review)
| Code | Keywords |
|------|----------|
| `HARDSHIP_LANGUAGE` | "lost my job", "can't afford", "financial hardship" |
| `LOAN_MOD_REQUEST` | "loan modification", "forbearance", "payment plan" |
| `BANKRUPTCY_OR_LAWYER` | "filed bankruptcy", "my attorney", "chapter 7" |
| `LEGAL_THREAT` | "sue you", "legal action", "attorney general" |
| `SUPERVISOR_REQUEST` | "speak to supervisor", "your manager" |
| `ABUSIVE_LANGUAGE` | "idiot", "stupid", "ridiculous" |
| `THIRD_PARTY_CALLER` | "calling for my husband", "power of attorney" |

### Normal Rules
| Code | Keywords |
|------|----------|
| `PAYMENT_INTENT` | "make a payment", "pay my mortgage" |
| `ESCROW_QUESTION` | "escrow account", "property taxes" |
| `NEW_LOAN_INQUIRY` | "refinance", "current rates" |

## Testing

```bash
# Run all tests
python -m pytest testing/ -v

# Run unit tests only
python -m pytest testing/fixtures/ -v

# Run integration tests only
python -m pytest testing/integration/ -v

# Show expected failures as actual failures
python -m pytest testing/ -v --runxfail
```

### Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Unit Tests | 133 | Entity extraction, rule matching, classification |
| Integration Tests | 91 | End-to-end pipeline, batch reporting, CLI |
| **Total** | **224** | |

## Known Issues (Errata)

The following edge cases are documented with `@pytest.mark.xfail` tests:

| Issue | Description | Workaround |
|-------|-------------|------------|
| Magnitude suffix spacing | `$500k` not recognized | Use `$500 k` or `500 thousand` |
| CA$ prefix | `CA$100` not matched | Use `CAD 100` instead |
| Date pattern overlap | `"Jan 5, 2023"` may return `["Jan 5, 2023", "Jan 5"]` | First match is complete date |
| Keyword overlap | `"take legal action"` scores 4 instead of 2 | Does not affect classification |

## Pipeline Flow

```
┌─────────────────┐
│  Raw Transcript │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ transcriptParser│  → Normalize text, extract speakers
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ruleEngine| │entityExtractor│  → Match keywords, extract entities
└────┬───┘ └──────┬───────┘
     │            │
     ▼            │
┌────────────────┐│
│intentClassifier││  → Determine primary intent
└────────┬───────┘│
         │        │
         ▼        ▼
  ┌─────────────────┐
  │escalationEngine │  → Calculate risk level
  └────────┬────────┘
           │
           ▼
 ┌─────────────────┐
 │summaryGenerator │  → Generate bullet points
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  TriageResult   │  → Final output
 └─────────────────┘
```

## License

MIT License

## Author

Humayoun
