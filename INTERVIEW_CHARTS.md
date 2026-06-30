# Interview Design Charts — Transcript Triage Linter

A reference for discussing the **why**, **engineering trade-offs**, **design decisions**, and **user experience** of this system.

---

## 1. System Overview — The Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                   │
│   CLI / Python API   →   single file  OR  batch of N files         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  TriagePipeline │  ← orchestrator; picks strategy
                    │  (triageResult) │    based on batch size
                    └────────┬────────┘
                             │
           ┌─────────────────▼──────────────────┐
           │                                    │
           │           STAGE 1                  │
           │      transcriptParser              │
           │  • normalize whitespace/case       │
           │  • extract Agent / Caller turns    │
           │  • produce Transcript data class   │
           └────────────────┬───────────────────┘
                            │ Transcript
          ┌─────────────────┴──────────────────┐
          │                                    │
          ▼                                    ▼
┌─────────────────────┐             ┌───────────────────────┐
│     STAGE 2a        │             │      STAGE 2b         │
│     ruleEngine      │             │   entityExtractor     │
│  • keyword scoring  │             │  • regex for amounts  │
│  • THRESHOLD = 2    │             │  • 40-char context    │
│  • → ReasonCode[]   │             │    window for labels  │
│    (8 escalation    │             │  • dates, phones,     │
│     + 3 normal)     │             │    loan numbers       │
└─────────┬───────────┘             └──────────┬────────────┘
          │ ReasonCode[]                        │ Entities
          │             ┌───────────────────────┘
          ▼             ▼
┌─────────────────────────────────────────────────────┐
│                    STAGE 3                          │
│               intentClassifier                      │
│  • maps ReasonCodes → primary intent string         │
│  • escalation codes win over normal codes           │
└─────────────────────────┬───────────────────────────┘
                          │ intents[]
                          ▼
┌─────────────────────────────────────────────────────┐
│                    STAGE 4                          │
│               escalationEngine                      │
│  • any escalation code → escalate = True            │
│  • score → LOW / MEDIUM / HIGH risk                 │
└─────────────────────────┬───────────────────────────┘
                          │ escalation_needed, risk_level
                          ▼
┌─────────────────────────────────────────────────────┐
│                    STAGE 5                          │
│               summaryGenerator                      │
│  • one bullet per intent                            │
│  • one bullet per labeled amount GROUP              │
│    (e.g. all "Monthly payment" amounts → 1 bullet)  │
└─────────────────────────┬───────────────────────────┘
                          │ summary_bullets[]
                          ▼
                ┌─────────────────────┐
                │    TriageResult     │
                │  intent             │
                │  escalate: bool     │
                │  risk_level         │
                │  reason_codes[]     │
                │  entities           │
                │  summary_bullets[]  │
                └─────────────────────┘
```

**Key talking point:** Each stage has one responsibility. The pipeline is stateless per transcript — all shared state lives in worker processes, not in the classes themselves.

---

## 2. Processing Strategy — The Three-Mode Architecture

```
process_batch(file_paths)
         │
         ▼
┌────────────────────────┐
│  len(file_paths) < 8?  │
└────────┬───────────────┘
         │ YES                        NO
         ▼                            ▼
┌─────────────────┐        ┌──────────────────────┐
│   SEQUENTIAL    │        │  _get_pool(n) called  │
│   Simple loop   │        │                       │
│   No overhead   │        │  Pool exists?  NO ──► │─► Create PipelinePool
│   ~4.1ms/file   │        │       │               │   workers=√n (capped)
└─────────────────┘        │  YES  ▼               │   _init_worker() once
                           │  optimal_workers(n)   │   per worker process
                           │  > pool.workers?      │
                           │       │               │
                           │  NO   │  YES          │
                           │  ▼    ▼               │
                           │  Reuse existing pool  │
                           │  (never scale down —  │
                           │   warm workers kept)  │
                           └──────────┬────────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │  executor.map(       │
                           │    _process_file_    │
                           │    warm, paths)      │
                           │  (preserves order)   │
                           └──────────────────────┘
```

**Key trade-off:** Why not always use the pool?
- `ProcessPoolExecutor` startup costs ~40ms per batch for cold workers
- For 2–3 files, sequential is faster *and* simpler
- Threshold of 8 is the crossover point where parallel overhead is worthwhile

---

## 3. Worker Scaling Formula — sqrt(batch_size)

```
Workers vs Batch Size
────────────────────────────────────────────────

workers = min(cpu_count, ceil(√batch_size))

  Batch size │  √n  │ ceil │ Cap (4 CPUs) │ Workers
  ───────────┼──────┼──────┼──────────────┼────────
      1–3    │  1.7 │   2  │      4       │   2
      4–8    │  2.8 │   3  │      4       │   3
      9–15   │  3.9 │   4  │      4       │   4   ← CPU ceiling
     16–25   │  5.0 │   5  │      4       │   4
     36–48   │  6.9 │   7  │      4       │   4
    100+     │ 10+  │  10+ │      4       │   4

  WHY square root?
  ┌────────────────────────────────────────────────┐
  │ Linear scaling: waste workers on small batches │
  │                                                │
  │    4 workers │░░░░░░░░░░░░░░░░░ (batch=5)      │
  │              │  2 workers busy, 2 idle         │
  │                                                │
  │ sqrt scaling: proportional to work             │
  │                                                │
  │    2 workers │░░░░░░░░░░░░░░░░░ (batch=5)      │
  │              │  both fully utilized            │
  └────────────────────────────────────────────────┘

  CPU cap prevents context-switching overhead
  on disk-bound I/O (more processes ≠ faster reads)
```

---

## 4. Warm Pool — How Worker Startup Cost Is Eliminated

```
                WITHOUT warm pool (cold parallel)
                ─────────────────────────────────
  Batch 1  ──► [spawn][init][init][init][init] ──► process ──► [kill]
  Batch 2  ──► [spawn][init][init][init][init] ──► process ──► [kill]
  Batch 3  ──► [spawn][init][init][init][init] ──► process ──► [kill]

              startup cost paid EVERY batch (~8ms overhead)

                WITH warm pool (PipelinePool)
                ─────────────────────────────
  Create   ──► [spawn][init][init][init][init]  ← paid ONCE
  Batch 1  ──────────────────────────────────► process
  Batch 2  ──────────────────────────────────► process  ← workers
  Batch 3  ──────────────────────────────────► process     stay alive

  Per-worker init: instantiate all 5 engine objects in global module state
    _parser, _extractor, _intent_clf, _escalate, _summary
    ↑ stored as module globals (picklable, shared within worker)

  Workers scale UP but never DOWN:
    If batch 1 = 10 files  →  3 workers created
    If batch 2 = 100 files →  4 workers created (scaled up)
    If batch 3 = 10 files  →  still 4 workers (not torn down — warm is valuable)
```

---

## 5. Performance Benchmarks (34 transcripts, 4 CPU cores)

```
Throughput by Processing Mode
──────────────────────────────────────────────────────────────────

Sequential (single process)
  Call 1:  138.8ms  ████████████████████████████████████  4.08ms/file

Cold parallel (new pool each call)
  Call 1:   52.4ms  ██████████████  1.54ms/file
  Call 2:   51.9ms  █████████████  1.53ms/file
  Call 3:   54.6ms  ██████████████  1.61ms/file

Warm pool (persistent workers)
  Call 1:   47.9ms  ████████████  1.41ms/file  ← includes pool startup
  Call 2:   40.0ms  ██████████  1.18ms/file  ← steady state
  Call 3:   39.5ms  ██████████  1.16ms/file

─────────────────────────────────────────────────────────────────
Improvement:   Sequential → Warm (steady)  =  71% faster
               Cold parallel → Warm        =  23% faster per batch
               Warm call 1  → call 2       =  16% (startup amortized)

At 519 transcripts (full corpus):
  Sequential estimated:  ≈ 2,100ms  (~2.1s)
  Warm pool estimated:   ≈   600ms  (~0.6s)
```

---

## 6. Rule Engine Design — Keyword Scoring (Not ML)

```
WHY keyword rules instead of an ML classifier?
──────────────────────────────────────────────

  ML model                           Rule engine (chosen)
  ────────────────────────           ────────────────────────────────
  ✗ Requires labeled data            ✓ Auditable — compliance teams
  ✗ Black-box decisions                can read exactly why a call
  ✗ Needs retraining                   was escalated
  ✗ Higher latency (inference)       ✓ Zero training data needed
  ✓ Handles novel phrasing           ✓ Sub-millisecond per transcript
                                     ✓ Deterministic — same input
                                       always produces same output

Scoring mechanism (THRESHOLD = 2):

  Rule: HARDSHIP_LANGUAGE
  ┌─────────────────────────────────────────────────────────┐
  │ Keywords (2pts each):   "can't afford", "lost my job"…  │
  │ Single words (1pt each): "hardship", "struggling"…      │
  │                                                          │
  │ Text: "I've been struggling and can't afford my payment" │
  │                                                          │
  │   "struggling"   →  +1  (single word)                   │
  │   "can't afford" →  +2  (keyword)                       │
  │   total = 3  ≥  THRESHOLD (2)  →  RULE FIRES ✓          │
  └─────────────────────────────────────────────────────────┘

  WHY THRESHOLD = 2?
    Single-word matches (score=1) are too ambiguous:
      "I want to dispute my balance"  →  "dispute" = 1pt  → NO fire
      "I dispute this charge, don't owe this"  →  3pts  → fires
    Prevents common-word false positives ("payment", "balance")
    appearing in non-relevant context from triggering escalation.
```

---

## 7. Entity Extraction — The 40-Character Context Window

```
Problem: "$2,450" appears in a transcript — what does it mean?

   "...your monthly payment is $2,450 starting June..."
         ◄────── 40 chars ──────►│◄─── 40 chars ───►

Context window: capture text 40 chars before AND after the match

  Before: "your monthly payment is "
  After:  " starting June"

  Label matching table (checked in priority order):
  ┌──────────────────────┬──────────────────────────────────────────┐
  │ Label                │ Context trigger phrases                  │
  ├──────────────────────┼──────────────────────────────────────────┤
  │ Monthly payment      │ "monthly payment", "your payment is"     │
  │ Loan balance         │ "principal balance", "remaining balance"  │
  │ Escrow shortage      │ "escrow shortage", "escrow deficiency"   │
  │ Fee                  │ "late fee", "convenience fee"            │
  │ Payoff amount        │ "payoff", "pay off"                      │
  │ Deferred amount      │ "forbearance", "deferral"                │
  │ …13 labels total…    │                                          │
  │ Other amounts        │ (catch-all — no context match)           │
  └──────────────────────┴──────────────────────────────────────────┘

  Result: amounts are GROUPED by label in summaryGenerator
    → one bullet per label group (not per dollar figure)

  WHY 40 chars?
    Too narrow (10): misses multi-word context ("your monthly payment is")
    Too wide (100):  context bleeds into adjacent sentences, wrong label
    40 chars: empirically covers most natural speech patterns for
              mortgage servicing conversations
```

---

## 8. Data Model — How Information Flows

```
┌────────────────────────────────────────────────────────────────┐
│  Transcript (Data Class)                                       │
│  ──────────────────────                                        │
│  _raw_text: str          get_raw_text() → original            │
│  _normalized: str        get_normalized_text() → lowercase,   │
│  _speakers: list           whitespace-cleaned                  │
└─────────────────────────────┬──────────────────────────────────┘
                              │  fed into
              ┌───────────────┴───────────┐
              ▼                           ▼
┌──────────────────────┐    ┌─────────────────────────────────────┐
│  ReasonCode          │    │  Entities (Data Class)              │
│  ─────────────────── │    │  ─────────────────────              │
│  code: str           │    │  amounts: list[float]               │
│  is_escalation: bool │    │  amount_contexts: list[             │
│  score: int          │    │    (float, str_label)]              │
│                      │    │  dates: list[str]                   │
│  get_code()          │    │  phones: list[str]                  │
│  get_is_escalation() │    │  loan_numbers: list[str]            │
│  to_code_map()       │    │                                     │
└──────────┬───────────┘    │  get_amount_contexts()              │
           │                │  get_amounts()                      │
           │                └──────────────────┬──────────────────┘
           │                                   │
           └────────────────┬──────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│  TriageResult (Final Output)                                  │
│  ───────────────────────────                                  │
│  intent: str                    (primary classification)      │
│  escalate: bool                 (supervisor needed?)          │
│  risk_level: str                (LOW / MEDIUM / HIGH)         │
│  reason_codes: list[ReasonCode]                               │
│  entities: Entities                                           │
│  summary: list[str]             (bullet points)               │
│                                                               │
│  to_json() → dict   __str__() → pretty print                  │
└───────────────────────────────────────────────────────────────┘
```

---

## 9. User Experience — Two Interfaces, One Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│  CLI (human-facing)                                              │
│  ──────────────────                                              │
│  python cli.py --single file.txt --format json                  │
│  python cli.py --batch --format csv                             │
│  python cli.py --list                                           │
│                                                                  │
│  Design decisions:                                               │
│  • --batch automatically uses warm pool when N ≥ 8              │
│    (user never manages pool lifecycle)                           │
│  • --format both  →  writes .json AND .csv in one command        │
│  • --list  →  shows available transcripts before processing      │
│  • human-readable stats printed to stdout, files to ./results/   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Python API (developer-facing)                                   │
│  ─────────────────────────────                                   │
│  with TriagePipeline() as pipeline:                             │
│      result  = pipeline.process_single("file.txt")              │
│      results = pipeline.process_batch(file_paths)               │
│  # pool automatically shut down on __exit__                      │
│                                                                  │
│  Design decisions:                                               │
│  • Context manager → no manual pool cleanup                      │
│  • Single API handles both small + large batches transparently   │
│  • workers param is optional; sqrt formula auto-sizes            │
│  • Lazy pool creation → no startup cost if batch is small        │
└──────────────────────────────────────────────────────────────────┘

Output formats:
  JSON  →  machine-readable, one result per file
  CSV   →  two-section format:
           SECTION 1: aggregate SUMMARY METRICS
             Total Transcripts, Escalation Rate, Top Intent,
             Top Reason Code, Average Risk Score
           SECTION 2: per-transcript rows
             filename, intent, escalate, risk_level, reason_codes, summary
```

---

## 10. Key Engineering Trade-offs Summary

```
Decision                  │ Chosen approach         │ Alternative considered
──────────────────────────┼─────────────────────────┼────────────────────────
Classification method     │ Keyword rule engine      │ ML classifier (BERT)
                          │ ✓ auditable, fast        │ ✓ generalization
                          │ ✗ brittle phrasing       │ ✗ black box, slow

Parallelism mechanism     │ ProcessPoolExecutor      │ ThreadPoolExecutor
                          │ ✓ true parallelism       │ ✓ lower overhead
                          │   (GIL bypass via fork)  │ ✗ GIL blocks CPU work
                          │ ✗ fork overhead          │

Worker scaling            │ ceil(√batch_size)        │ fixed N workers
                          │ ✓ proportional to work   │ ✓ simple
                          │ ✓ saves resources        │ ✗ idle workers on
                          │                          │   small batches

Pool lifecycle            │ lazy init, scale up only │ create/destroy per batch
                          │ ✓ warm workers kept      │ ✓ simple cleanup
                          │ ✗ memory held longer     │ ✗ startup cost/batch

Amount context window     │ 40 chars before+after    │ full sentence / regex
                          │ ✓ catches multi-word ctx │ ✗ sentence boundary
                          │ ✓ simple, fast           │   detection is error-prone

Rule threshold            │ THRESHOLD = 2            │ 1 (any match fires)
                          │ ✓ fewer false positives  │ ✗ common words cause
                          │ ✗ may miss weak signals  │   spurious escalations

Data classes (output)     │ typed Python dataclasses │ plain dicts
                          │ ✓ IDE autocomplete       │ ✓ less boilerplate
                          │ ✓ enforced shape         │ ✗ no validation
```

---

## 11. What I Would Build Next

```
Known issues to address:
┌──────────────────────────────────────────────────────────────────┐
│  1. Magnitude suffix spacing                                     │
│     "$500k" not recognized — parser expects "$500 k"            │
│     Fix: broaden _MAG pattern to allow zero-width spacing        │
│                                                                  │
│  2. Date pattern overlap                                         │
│     "Jan 5, 2023" may return ["Jan 5, 2023", "Jan 5"]           │
│     Fix: deduplicate by checking if one match is a substring     │
│          of a longer match, keep the longer                      │
│                                                                  │
│  3. Rule phrasing brittleness                                    │
│     "I need to speak with your manager" misses if phrasing       │
│     shifts ("I'd like to escalate this issue")                   │
│     Next step: add embedding similarity layer (sentence-         │
│     transformers) as a fallback when keyword score = 0–1         │
└──────────────────────────────────────────────────────────────────┘

Scaling path:
  Current: file-based CLI → streaming API → async ingestion
  Current: local process pool → distributed workers (Celery/Ray)
  Current: flat CSV output → structured database (SQLite → Postgres)
```
