# Transcript Triage Linter

A Python-based NLP pipeline for analyzing mortgage servicing call transcripts. Automatically classifies customer intent, detects escalation triggers, extracts key entities, and generates actionable summaries.

## Features

- **Intent Classification** — Identifies customer intent (payment, hardship, escrow inquiry, etc.)
- **Escalation Detection** — Flags calls requiring supervisor attention (legal threats, abusive language, etc.)
- **Risk Assessment** — Categorizes calls as LOW, MEDIUM, or HIGH risk
- **Entity Extraction** — Pulls out monetary amounts with semantic context labels, dates, phone numbers, and loan numbers
- **Context-Labeled Amounts** — Each extracted amount is grouped by role (Monthly payment, Loan balance, Fee, Escrow amount, etc.) based on surrounding text
- **Summary Generation** — Creates bullet-point summaries with one line per labeled amount group
- **Batch Processing** — Process multiple transcripts sequentially or in parallel
- **Persistent Warm Pool** — Optional `PipelinePool` keeps worker processes alive between batches for sustained throughput

## Architecture

```
Transcript_triage_linter/
├── cli.py                    # Entry point
├── benchmark.py              # Sequential vs. parallel vs. warm-pool benchmark
├── Data_Classes/
│   ├── entities.py           # Extracted entities model (amounts + context)
│   ├── reasonCode.py         # Reason code model
│   ├── transcript.py         # Parsed transcript model
│   └── triageResult.py       # Final result model
├── engines/
│   ├── transcriptParser.py   # Text normalization & speaker extraction
│   ├── entityExtractor.py    # Regex-based entity extraction with context capture
│   ├── ruleEngine.py         # Keyword-based rule matching
│   ├── intentClassifier.py   # Intent classification from reason codes
│   ├── escalationEngine.py   # Risk level calculation
│   ├── summaryGenerator.py   # Bullet point generation with per-label grouping
│   ├── batchReporter.py      # Batch metrics & CSV reporting
│   ├── triageResult.py       # Pipeline orchestration (sequential + parallel)
│   ├── pipelinePool.py       # Persistent warm worker pool
│   └── cli.py                # CLI implementation
├── transcripts/              # ~519 synthetic mortgage servicing transcripts
├── results/                  # Output directory
└── testing/
    ├── fixtures/             # Unit tests
    └── integration/          # Integration tests
```

## Installation

```bash
git clone https://github.com/HumayounKhan09/Transcript_triage_linter.git
cd Transcript_triage_linter
pip install pandas pytest
```

## Usage

### Single Transcript

```bash
# JSON output
python cli.py --single transcripts/synth_short_001.txt --format json

# CSV output
python cli.py --single transcripts/synth_short_001.txt --format csv

# Both formats
python cli.py --single transcripts/synth_short_001.txt --format both
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

### Programmatic API

`TriagePipeline` picks the right strategy automatically:

```python
from engines.triageResult import TriagePipeline
import glob

files = glob.glob("transcripts/*.txt")

with TriagePipeline() as pipeline:
    # < 8 files → runs sequentially
    result = pipeline.process_single("transcripts/synth_short_001.txt")

    # ≥ 8 files → spins up the warm pool on first call, keeps it alive
    results = pipeline.process_batch(files[:100])
    results2 = pipeline.process_batch(files[100:])  # pool already warm
# pool shut down automatically on context exit
```

### Run Benchmark

```bash
python benchmark.py
```

Sample output:

```
Sequential (34 files):           138.8ms  (4.08ms/transcript)
Cold parallel (34 files):         52.1ms  (1.54ms/transcript)
Warm pool call 1 (34 files):     47.9ms  (1.41ms/transcript, includes startup)
Warm pool call 2 (34 files):     40.3ms  (1.16ms/transcript)
```

## Output Example

### JSON Output
```json
{
  "intent": "payment",
  "escalate": false,
  "risk_level": "LOW",
  "reason_codes": ["PAYMENT_INTENT"],
  "entities": {
    "amounts": [2450, 185000],
    "dates": ["June 1, 2025"],
    "phones": [],
    "loan_numbers": ["LN-20250001"]
  },
  "summary_bullet": [
    "Borrower requested to make a payment.",
    "Monthly payment: $2,450.00.",
    "Loan balance: $185,000.00."
  ]
}
```

### Batch CSV Output
```
SUMMARY METRICS
Total Transcripts,519
Escalation Rate,42.3%
Top Intent,PAYMENT_INTENT (87)
Top Reason Code,HARDSHIP_LANGUAGE (94)

filename,intent,escalate,risk_level,reason_codes,summary
synth_short_001.txt,payment,False,LOW,PAYMENT_INTENT,"Borrower requested to make a payment. Monthly payment: $1,847.00."
```

## Amount Context Labels

When amounts are extracted, surrounding text (40 chars before and after the match) is used to assign a semantic label. One summary bullet is generated per label group.

| Label | Triggered by context containing… |
|-------|----------------------------------|
| Monthly payment | "monthly payment", "your payment is", "next payment" |
| Loan balance | "principal balance", "remaining balance", "current balance" |
| Loan amount | "loan amount", "mortgage amount", "borrow" |
| Property value | "purchase price", "home price", "appraised" |
| Escrow shortage | "escrow shortage", "escrow deficiency" |
| Escrow amount | "escrow", "impound", "property tax", "insurance premium" |
| Fee | "late fee", "convenience fee", "processing fee" |
| Down payment | "down payment", "money down" |
| Payoff amount | "payoff", "pay off", "total amount to pay" |
| Deferred amount | "forbearance", "deferral", "deferred" |
| Amount past due | "arrears", "past due", "missed payment" |
| Interest rate | "interest rate", "rate of" |
| Insurance premium | "pmi", "mortgage insurance premium" |
| Other amounts | (no context match — catch-all bucket) |

## Rule Categories

### Escalation Rules (trigger supervisor review)
| Code | Sample keywords |
|------|----------------|
| `HARDSHIP_LANGUAGE` | "lost my job", "can't afford", "financial hardship" |
| `LOAN_MOD_REQUEST` | "loan modification", "forbearance", "payment plan" |
| `BANKRUPTCY_OR_LAWYER` | "filed bankruptcy", "my attorney", "chapter 7" |
| `LEGAL_THREAT` | "sue you", "legal action", "attorney general" |
| `DISPUTE_FEE_OR_CHARGE` | "dispute this charge", "unauthorized charge" |
| `SUPERVISOR_REQUEST` | "speak to supervisor", "your manager" |
| `ABUSIVE_LANGUAGE` | "idiot", "stupid", "ridiculous" |
| `THIRD_PARTY_CALLER` | "calling for my husband", "power of attorney" |

### Normal Rules
| Code | Sample keywords |
|------|----------------|
| `PAYMENT_INTENT` | "make a payment", "pay my mortgage" |
| `ESCROW_QUESTION` | "escrow account", "property taxes" |
| `NEW_LOAN_INQUIRY` | "refinance", "current rates" |

## Synthetic Transcript Corpus

The `transcripts/` directory contains ~519 synthetic mortgage servicing call transcripts spanning 6 duration buckets:

| Bucket | Duration | Count | Topics |
|--------|----------|-------|--------|
| `synth_short_*` | ≤5 min | 75 | Simple payment, balance, escrow, account ops |
| `synth_medshort_*` | 5–8 min | 125 | ARM mechanics, PMI, forbearance, third-party auth |
| `synth_core_*` | 8–12 min | ~172 | Hardship intake, modification, loss mitigation |
| `synth_medlong_*` | 12–15 min | ~68 | Short sale, regulatory disputes, servicer errors |
| `synth_long_*` | 15–20 min | 30 | Complex multi-issue calls, estate, bankruptcy |
| `synth_xl_*` | 20+ min | 10 | Extended loss mitigation, multi-party disputes |

Every transcript uses `Agent:` / `Caller:` speaker labels only, includes identity verification, specific dollar amounts, loan numbers, and realistic resolutions.

## Performance

| Mode | Throughput | Notes |
|------|-----------|-------|
| Sequential | ~4.1ms/transcript | Single process |
| Cold parallel | ~1.5ms/transcript | `ProcessPoolExecutor`, fresh workers |
| Warm pool (steady state) | ~1.2ms/transcript | `PipelinePool`, workers pre-initialized |

Parallel processing and warm pool management are handled automatically by `TriagePipeline.process_batch()` — small batches run sequentially, large batches use the persistent warm pool with no extra setup required.

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

### Pre-push Hook (Local)

Run tests automatically before every `git push`:

```bash
git config core.hooksPath .githooks
```

To disable:

```bash
git config --unset core.hooksPath
```

### Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Unit Tests | ~150 | Entity extraction, rule matching, classification, summary generation |
| Integration Tests | ~91 | End-to-end pipeline, batch reporting, CLI |
| **Total** | **~241** | |

## Known Issues (Errata)

The following edge cases are documented with `@pytest.mark.xfail` tests:

| Issue | Description | Workaround |
|-------|-------------|------------|
| Magnitude suffix spacing | `$500k` not recognized | Use `$500 k` or `500 thousand` |
| CA$ prefix | `CA$100` not matched | Use `CAD 100` instead |
| Date pattern overlap | `"Jan 5, 2023"` may return `["Jan 5, 2023", "Jan 5"]` | First match is the complete date |
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
┌──────────┐ ┌─────────────────┐
│ruleEngine│ │ entityExtractor │  → Match keywords; extract entities
└────┬─────┘ │  + context      │     with 40-char context window
     │       └────────┬────────┘
     ▼                │
┌──────────────────┐  │
│ intentClassifier │  │  → Determine primary intent
└────────┬─────────┘  │
         │            │
         ▼            ▼
  ┌─────────────────────┐
  │  escalationEngine   │  → Calculate risk level
  └──────────┬──────────┘
             │
             ▼
   ┌──────────────────┐
   │ summaryGenerator │  → Generate per-label-group bullets
   └──────────┬───────┘
              │
              ▼
   ┌──────────────────┐
   │   TriageResult   │  → Final output (JSON / CSV)
   └──────────────────┘
```

## License

MIT License

## Author

Humayoun Khan
