# Graph Report - .  (2026-06-30)

## Corpus Check
- Large corpus: 563 files · ~677,649 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 592 nodes · 1032 edges · 42 communities (25 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Transcript Data Model|Transcript Data Model]]
- [[_COMMUNITY_Reason Code Data Model|Reason Code Data Model]]
- [[_COMMUNITY_Transcript Parser Engine|Transcript Parser Engine]]
- [[_COMMUNITY_Domain Concepts & Escalation Rules|Domain Concepts & Escalation Rules]]
- [[_COMMUNITY_Entity Extractor Test Rationale|Entity Extractor Test Rationale]]
- [[_COMMUNITY_Intent Classifier & Triage Pipeline|Intent Classifier & Triage Pipeline]]
- [[_COMMUNITY_README Documentation|README Documentation]]
- [[_COMMUNITY_Summary Generator Tests|Summary Generator Tests]]
- [[_COMMUNITY_Triage Result Data Model|Triage Result Data Model]]
- [[_COMMUNITY_Entities Class & Summary Generator|Entities Class & Summary Generator]]
- [[_COMMUNITY_Batch Reporter Integration Tests|Batch Reporter Integration Tests]]
- [[_COMMUNITY_Benchmark Script|Benchmark Script]]
- [[_COMMUNITY_CLI Engine|CLI Engine]]
- [[_COMMUNITY_Entity Extractor Engine|Entity Extractor Engine]]
- [[_COMMUNITY_Triage Pipeline Integration Tests|Triage Pipeline Integration Tests]]
- [[_COMMUNITY_CLI Init & Triage Result Internals|CLI Init & Triage Result Internals]]
- [[_COMMUNITY_Entities Data Class API|Entities Data Class API]]
- [[_COMMUNITY_Loan Number Extraction Tests|Loan Number Extraction Tests]]
- [[_COMMUNITY_Date Extraction Tests|Date Extraction Tests]]
- [[_COMMUNITY_Pipeline Pool (Concurrent Processing)|Pipeline Pool (Concurrent Processing)]]
- [[_COMMUNITY_Summary Bullet Extraction Tests|Summary Bullet Extraction Tests]]
- [[_COMMUNITY_Single Transcript Processing Tests|Single Transcript Processing Tests]]
- [[_COMMUNITY_Entity Extractor Test Setup|Entity Extractor Test Setup]]
- [[_COMMUNITY_Phone Number Extraction Tests|Phone Number Extraction Tests]]
- [[_COMMUNITY_CSV Generation Tests|CSV Generation Tests]]
- [[_COMMUNITY_CLI Integration Tests|CLI Integration Tests]]
- [[_COMMUNITY_Batch Processing Tests|Batch Processing Tests]]
- [[_COMMUNITY_Escalation Bullet Tests|Escalation Bullet Tests]]
- [[_COMMUNITY_Bullet Format Tests|Bullet Format Tests]]
- [[_COMMUNITY_CLI Batch Mode Tests|CLI Batch Mode Tests]]
- [[_COMMUNITY_CLI Single Mode Tests|CLI Single Mode Tests]]
- [[_COMMUNITY_CLI Batch Output & Stats|CLI Batch Output & Stats]]
- [[_COMMUNITY_Payment Bullet Extraction|Payment Bullet Extraction]]
- [[_COMMUNITY_Top Intents Analysis Tests|Top Intents Analysis Tests]]
- [[_COMMUNITY_Reason Code Count Tests|Reason Code Count Tests]]
- [[_COMMUNITY_CLI Argument Validation Tests|CLI Argument Validation Tests]]
- [[_COMMUNITY_Common Pattern Analysis Tests|Common Pattern Analysis Tests]]
- [[_COMMUNITY_CLI Print Methods Tests|CLI Print Methods Tests]]
- [[_COMMUNITY_CSV Save Function|CSV Save Function]]
- [[_COMMUNITY_JSON Save Function|JSON Save Function]]
- [[_COMMUNITY_README Known Issues|README Known Issues]]

## God Nodes (most connected - your core abstractions)
1. `reasonCode` - 42 edges
2. `transcript` - 38 edges
3. `run_rules()` - 30 edges
4. `triageResult` - 29 edges
5. `Entities` - 27 edges
6. `entityExtractor` - 26 edges
7. `TriagePipeline` - 25 edges
8. `to_code_map()` - 25 edges
9. `parse()` - 25 edges
10. `CLI` - 24 edges

## Surprising Connections (you probably didn't know these)
- `CFPB Complaint (Consumer Financial Protection Bureau)` --semantically_similar_to--> `LEGAL_THREAT Escalation Rule`  [INFERRED] [semantically similar]
  testing/fixtures/transcripts/test_dispute_escalates_slowly.txt → README.md
- `entityExtractor` --uses--> `Entities`  [INFERRED]
  engines/entityExtractor.py → Data_Classes/entities.py
- `summaryGenerator` --uses--> `Entities`  [INFERRED]
  engines/summaryGenerator.py → Data_Classes/entities.py
- `TestExtractEscalationBullet` --uses--> `Entities`  [INFERRED]
  testing/fixtures/test_summary_generator.py → Data_Classes/entities.py
- `TestExtractPaymentBullet` --uses--> `Entities`  [INFERRED]
  testing/fixtures/test_summary_generator.py → Data_Classes/entities.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Escalation-Triggering Fixture Transcripts** — fixture_abusive_language_escalating, fixture_legal_threat_angry_escalation, fixture_dispute_escalates_slowly, fixture_complex_multi_issue_chaos, fixture_bankruptcy_confused_caller [INFERRED 0.95]
- **Hardship and Loss Mitigation Call Flow (Forbearance / Loan Mod / Loss Mitigation)** — concept_forbearance, concept_loan_modification, concept_loss_mitigation, concept_hardship_language, concept_loan_mod_request [INFERRED 0.85]
- **Core NLP Pipeline Processing Stages** — readme_transcript_parser, readme_rule_engine, readme_entity_extractor, readme_intent_classifier, readme_escalation_engine, readme_summary_generator [EXTRACTED 1.00]

## Communities (42 total, 17 thin omitted)

### Community 0 - "Transcript Data Model"
Cohesion: 0.05
Nodes (35): File Name: transcript.py Description: Data Class for transcript, transcript, File Name: ruleEngine.py Description: Rule Engine for processing transcripts, Score a rule against normalised text using fast string containment checks., ruleEngine, _score(), make_transcript(), Unit tests for ruleEngine. (+27 more)

### Community 1 - "Reason Code Data Model"
Cohesion: 0.08
Nodes (12): File Name: reasonCode.py Description: Data Class for Reason Code, reasonCode, escalationEngine, File Name: escalationEngine.py Description: Engine to handle escalation logic, File Name: intentClassifier.py Description: Intent Classifier Engine, engine(), make_reason(), Unit tests for escalationEngine. (+4 more)

### Community 2 - "Transcript Parser Engine"
Cohesion: 0.08
Nodes (15): File Name: transcriptParser.py Description: Parser for transcript data, transcriptParser, assert_timestamp_recent(), parse(), Unit tests for transcriptParser., Tests for raw text preservation., Tests for timestamp generation., Tests for basic parser behavior. (+7 more)

### Community 3 - "Domain Concepts & Escalation Rules"
Cohesion: 0.12
Nodes (34): ABUSIVE_LANGUAGE Escalation Rule, Automatic Stay (Bankruptcy Provision), BANKRUPTCY_OR_LAWYER Escalation Rule, Cash-Out Refinance, CFPB Complaint (Consumer Financial Protection Bureau), DISPUTE_FEE_OR_CHARGE Escalation Rule, Escrow Analysis (Annual Shortage/Surplus Calculation), ESCROW_QUESTION Normal Rule (+26 more)

### Community 4 - "Entity Extractor Test Rationale"
Cohesion: 0.07
Nodes (9): Tests for monetary amount extraction., Bare values 100-9999 in mortgage context scale to thousands., Equivalent values should be deduped., $500k should work but currently requires space., $1.5m should work but currently requires space., $500 k works with space., $1.5 m works with space., CA$ format should work but doesn't. (+1 more)

### Community 5 - "Intent Classifier & Triage Pipeline"
Cohesion: 0.14
Nodes (12): intentClassifier, classifier(), classify(), make_reason(), Unit tests for intentClassifier., Tests for basic intent classification., Tests for recognized intent codes., DISPUTE_FEE_OR_CHARGE from ruleEngine should be recognized. (+4 more)

### Community 6 - "README Documentation"
Cohesion: 0.15
Nodes (19): Amount Context Labels (40-char Window Semantic Labeling), Batch Processing, batchReporter — Batch Metrics & CSV Reporting, Context-Labeled Amount Extraction, Entity Extraction, entityExtractor — Regex-based Entity Extraction, Escalation Detection, escalationEngine — Risk Level Calculation (+11 more)

### Community 7 - "Summary Generator Tests"
Cohesion: 0.17
Nodes (5): make_entities(), Tests for combined bullet generation., Tests for payment bullet generation., TestExtractPaymentBullet, TestGenerateBullets

### Community 8 - "Triage Result Data Model"
Cohesion: 0.20
Nodes (6): triageResult, DataFrame, batchReporter, File Name: batchReporter.py Description: Engine to generate batch reports, Identify common failure patterns in the batch of results, File Name: cli.py Description: Command Line Interface

### Community 9 - "Entities Class & Summary Generator"
Cohesion: 0.16
Nodes (9): File Name: entities.py Description: Data Class for Entities, File Name: summaryGenerator.py Description: Engine to generate summary bullets f, Generate bullet explaining why call was escalated, Format a bullet point nicely, Generate summary bullets for the call, Generate bullet about what customer requested based on intent, summaryGenerator, gen() (+1 more)

### Community 10 - "Batch Reporter Integration Tests"
Cohesion: 0.12
Nodes (7): batch_results(), Integration tests for batchReporter.  Tests batch reporting with real processed, Tests for DataFrame generation., Tests for escalation rate calculation., reporter(), TestBuildReportDataframe, TestCalculateEscalationRate

### Community 11 - "Benchmark Script"
Cohesion: 0.18
Nodes (12): _get_transcripts(), main(), benchmark.py — Compare sequential, cold parallel, and warm-pool throughput.  Res, Return (result, elapsed_ms)., _row(), _time_call(), File Name: triageResult.py Description: Data Class for triageResult, _process_file_warm() (+4 more)

### Community 12 - "CLI Engine"
Cohesion: 0.21
Nodes (5): CLI, Run single mode with error handling, Print single result summary to terminal, Format duration in ms or s depending on length., No-op pause for CLI completion (kept for compatibility).

### Community 13 - "Entity Extractor Engine"
Cohesion: 0.22
Nodes (5): entityExtractor, Return flat list of numeric amounts (backward-compatible)., Return list of (amount, context_snippet) pairs., _init_worker(), Initializer run once in each worker process at pool startup.

### Community 14 - "Triage Pipeline Integration Tests"
Cohesion: 0.14
Nodes (4): pipeline(), Integration tests for TriagePipeline.  Tests end-to-end transcript processing us, Tests for cross-field consistency., TestResultConsistency

### Community 15 - "CLI Init & Triage Result Internals"
Cohesion: 0.21
Nodes (5): Release the warm pool if one was created., Scale worker count with batch size using a square-root curve.          workers =, Process a single transcript file and return a TriageResult., Process multiple transcripts.          Small batches run sequentially. Larger ba, TriagePipeline

### Community 17 - "Loan Number Extraction Tests"
Cohesion: 0.17
Nodes (3): Tests for loan number extraction., Misspelled method name should still work., TestExtractLoanNumbers

### Community 18 - "Date Extraction Tests"
Cohesion: 0.20
Nodes (3): Tests for date extraction., Should not return both 'Jan 5, 2023' and 'Jan 5'., TestExtractDates

### Community 19 - "Pipeline Pool (Concurrent Processing)"
Cohesion: 0.25
Nodes (4): PipelinePool, Shut down the underlying ProcessPoolExecutor., Persistent warm worker pool for transcript triage processing.      Usage::, Process a list of transcript file paths and return TriageResult objects.

### Community 22 - "Entity Extractor Test Setup"
Cohesion: 0.29
Nodes (5): extractor(), make_transcript(), Unit tests for entityExtractor., Tests for combined entity extraction., TestExtractAllEntities

### Community 25 - "CLI Integration Tests"
Cohesion: 0.25
Nodes (4): cli(), Integration tests for CLI.  Tests command-line interface functionality., Temp directory with symlink to transcripts., temp_dir()

### Community 27 - "Escalation Bullet Tests"
Cohesion: 0.43
Nodes (3): make_reason(), Tests for escalation bullet generation., TestExtractEscalationBullet

### Community 31 - "CLI Batch Output & Stats"
Cohesion: 0.33
Nodes (3): Run batch mode with error handling, Print aggregate batch statistics to terminal, Process all transcripts in batch

### Community 32 - "Payment Bullet Extraction"
Cohesion: 0.33
Nodes (3): Map a raw context snippet to a human-readable label., Generate one bullet per labeled amount group, plus one catch-all for unlabeled., Single-string summary of amounts (used by tests; delegates to extract_payment_bu

## Knowledge Gaps
- **6 isolated node(s):** `Transcript Triage Linter`, `transcriptParser — Text Normalization & Speaker Extraction`, `batchReporter — Batch Metrics & CSV Reporting`, `Known Issues (xfail Edge Cases)`, `Automatic Stay (Bankruptcy Provision)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TriagePipeline` connect `CLI Init & Triage Result Internals` to `Transcript Data Model`, `Reason Code Data Model`, `Transcript Parser Engine`, `Intent Classifier & Triage Pipeline`, `Triage Result Data Model`, `Entities Class & Summary Generator`, `Batch Reporter Integration Tests`, `Benchmark Script`, `Entity Extractor Engine`, `Triage Pipeline Integration Tests`, `Pipeline Pool (Concurrent Processing)`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `entityExtractor` connect `Entity Extractor Engine` to `Transcript Data Model`, `Entity Extractor Test Rationale`, `Intent Classifier & Triage Pipeline`, `Benchmark Script`, `CLI Init & Triage Result Internals`, `Entities Data Class API`, `Loan Number Extraction Tests`, `Date Extraction Tests`, `Pipeline Pool (Concurrent Processing)`, `Entity Extractor Test Setup`, `Phone Number Extraction Tests`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `reasonCode` connect `Reason Code Data Model` to `Transcript Data Model`, `Intent Classifier & Triage Pipeline`, `Summary Generator Tests`, `Triage Result Data Model`, `Entities Class & Summary Generator`, `Benchmark Script`, `Entities Data Class API`, `Summary Bullet Extraction Tests`, `Escalation Bullet Tests`, `Bullet Format Tests`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `reasonCode` (e.g. with `triageResult` and `escalationEngine`) actually correct?**
  _`reasonCode` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `transcript` (e.g. with `entityExtractor` and `ruleEngine`) actually correct?**
  _`transcript` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `triageResult` (e.g. with `Entities` and `reasonCode`) actually correct?**
  _`triageResult` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Entities` (e.g. with `triageResult` and `entityExtractor`) actually correct?**
  _`Entities` has 8 INFERRED edges - model-reasoned connections that need verification._