"""
File Name: triageResult.py
Description: This is the main driver of the entire linter
"""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from Data_Classes.triageResult import triageResult as TriageResult
from engines.transcriptParser import transcriptParser
from engines.ruleEngine import ruleEngine as RuleEngine
from engines.entityExtractor import entityExtractor as EntityExtractor
from engines.intentClassifier import intentClassifier as IntentClassifier
from engines.escalationEngine import escalationEngine as EscalationEngine
from engines.summaryGenerator import summaryGenerator as SummaryGenerator

# ---------------------------------------------------------------------------
# Module-level worker — must be at the top level so ProcessPoolExecutor can
# pickle it. Each worker process imports the module once and reuses the
# pre-compiled regex patterns on every call.
# ---------------------------------------------------------------------------
def _process_file(file_path: str) -> TriageResult:
    parser          = transcriptParser()
    entity_extractor = EntityExtractor()
    intent_clf      = IntentClassifier()
    escalate_eng    = EscalationEngine()
    summary_gen     = SummaryGenerator()

    try:
        with open(file_path, 'r') as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    transcript      = parser.parse_transcript(raw_text)
    reason_codes    = RuleEngine(transcript).apply_rules()
    entity          = entity_extractor.extract_all_entities(transcript)
    intents         = intent_clf.classify(reason_codes)
    esc_result      = escalate_eng.evaluate_escalation(reason_codes)
    summary         = summary_gen.generate_bullets(intents, entity, reason_codes)

    return TriageResult(intents, esc_result["escalation_needed"],
                        esc_result["risk_level"], reason_codes, entity, summary)


class TriagePipeline:
    # Threshold at which parallel processing pays off over its startup cost
    _PARALLEL_THRESHOLD = 8

    def __init__(self):
        self.parser           = transcriptParser()
        self.entity_extractor = EntityExtractor()
        self.intent           = IntentClassifier()
        self.escalate         = EscalationEngine()
        self.summary          = SummaryGenerator()

    def process_single(self, file_path: str) -> TriageResult:
        """Process a single transcript file and return TriageResult."""
        return _process_file(file_path)

    def process_batch(self, file_paths: list, workers: int = None) -> list[TriageResult]:
        """Process multiple transcripts.

        Uses parallel processes when the batch is large enough to offset the
        startup cost. `workers` defaults to the number of CPU cores.
        """
        if len(file_paths) < self._PARALLEL_THRESHOLD:
            return [_process_file(p) for p in file_paths]

        max_workers = workers or os.cpu_count() or 4
        results_map = {}
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_process_file, p): i for i, p in enumerate(file_paths)}
            for future in as_completed(futures):
                idx = futures[future]
                results_map[idx] = future.result()

        return [results_map[i] for i in range(len(file_paths))]
