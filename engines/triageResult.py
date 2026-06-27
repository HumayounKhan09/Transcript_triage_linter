"""
File Name: triageResult.py
Description: This is the main driver of the entire linter
"""

import math
import os

from Data_Classes.triageResult import triageResult as TriageResult
from engines.transcriptParser import transcriptParser
from engines.ruleEngine import ruleEngine as RuleEngine
from engines.entityExtractor import entityExtractor as EntityExtractor
from engines.intentClassifier import intentClassifier as IntentClassifier
from engines.escalationEngine import escalationEngine as EscalationEngine
from engines.summaryGenerator import summaryGenerator as SummaryGenerator
from engines.pipelinePool import PipelinePool

# ---------------------------------------------------------------------------
# Module-level worker — must be at top level so ProcessPoolExecutor can pickle
# it (used by the sequential fallback path only).
# ---------------------------------------------------------------------------
def _process_file(file_path: str) -> TriageResult:
    parser           = transcriptParser()
    entity_extractor = EntityExtractor()
    intent_clf       = IntentClassifier()
    escalate_eng     = EscalationEngine()
    summary_gen      = SummaryGenerator()

    try:
        with open(file_path, 'r') as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    transcript   = parser.parse_transcript(raw_text)
    reason_codes = RuleEngine(transcript).apply_rules()
    entity       = entity_extractor.extract_all_entities(transcript)
    intents      = intent_clf.classify(reason_codes)
    esc_result   = escalate_eng.evaluate_escalation(reason_codes)
    summary      = summary_gen.generate_bullets(intents, entity, reason_codes)

    return TriageResult(intents, esc_result["escalation_needed"],
                        esc_result["risk_level"], reason_codes, entity, summary)


class TriagePipeline:
    # Batches smaller than this run sequentially (parallel startup cost not worth it)
    _PARALLEL_THRESHOLD = 8

    def __init__(self, workers: int = None):
        self.parser           = transcriptParser()
        self.entity_extractor = EntityExtractor()
        self.intent           = IntentClassifier()
        self.escalate         = EscalationEngine()
        self.summary          = SummaryGenerator()
        # Warm pool is created lazily on first parallel batch and kept alive
        self._pool: PipelinePool | None = None
        self._workers = workers

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _optimal_workers(batch_size: int) -> int:
        """Scale worker count with batch size using a square-root curve.

        workers = min(cpu_count, ceil(sqrt(batch_size)))

        This grows quickly for small batches (where adding a worker helps a
        lot) and flattens out for large ones (where we hit the CPU ceiling).
        """
        # Cap at logical core count — spawning more processes than cores causes
        # context-switching overhead and can starve I/O on disk-bound reads.
        return min(os.cpu_count() or 4, math.ceil(math.sqrt(batch_size)))

    def _get_pool(self, batch_size: int) -> PipelinePool:
        optimal = self._optimal_workers(batch_size)
        # Scale up if a larger batch needs more workers; never scale down
        # (shrinking would throw away warm workers for no gain).
        if self._pool is None or optimal > self._pool.workers:
            if self._pool is not None:
                self._pool.shutdown(wait=False)
            self._pool = PipelinePool(workers=optimal)
        return self._pool

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_single(self, file_path: str) -> TriageResult:
        """Process a single transcript file and return a TriageResult."""
        return _process_file(file_path)

    def process_batch(self, file_paths: list) -> list[TriageResult]:
        """Process multiple transcripts.

        Small batches run sequentially. Larger batches use the persistent warm
        pool automatically — no manual pool management needed.
        """
        if len(file_paths) < self._PARALLEL_THRESHOLD:
            return [_process_file(p) for p in file_paths]
        return self._get_pool(len(file_paths)).process_batch(file_paths)

    def shutdown(self):
        """Release the warm pool if one was created."""
        if self._pool is not None:
            self._pool.shutdown()
            self._pool = None

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False
