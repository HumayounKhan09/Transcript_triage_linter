"""
File Name: pipelinePool.py
Description: Persistent warm worker pool for the Transcript Triage Linter pipeline.
             Workers are initialized once with all engine objects pre-loaded so
             the ~80ms startup cost is paid once at pool creation, not per batch.
"""

import os
from concurrent.futures import ProcessPoolExecutor

from Data_Classes.triageResult import triageResult as TriageResult

# ---------------------------------------------------------------------------
# Per-process module-level state — populated once by _init_worker()
# ---------------------------------------------------------------------------
_parser = None
_extractor = None
_intent_clf = None
_escalate = None
_summary = None


def _init_worker():
    """Initializer run once in each worker process at pool startup."""
    global _parser, _extractor, _intent_clf, _escalate, _summary
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from engines.transcriptParser import transcriptParser
    from engines.entityExtractor import entityExtractor
    from engines.intentClassifier import intentClassifier
    from engines.escalationEngine import escalationEngine
    from engines.summaryGenerator import summaryGenerator
    _parser = transcriptParser()
    _extractor = entityExtractor()
    _intent_clf = intentClassifier()
    _escalate = escalationEngine()
    _summary = summaryGenerator()


def _process_file_warm(file_path: str) -> TriageResult:
    """Process a single transcript file using pre-warmed module-level engines."""
    from engines.ruleEngine import ruleEngine as RuleEngine

    try:
        with open(file_path, 'r') as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    transcript   = _parser.parse_transcript(raw_text)
    reason_codes = RuleEngine(transcript).apply_rules()
    entity       = _extractor.extract_all_entities(transcript)
    intents      = _intent_clf.classify(reason_codes)
    esc_result   = _escalate.evaluate_escalation(reason_codes)
    summary      = _summary.generate_bullets(intents, entity, reason_codes)

    return TriageResult(
        intents,
        esc_result["escalation_needed"],
        esc_result["risk_level"],
        reason_codes,
        entity,
        summary,
    )


class PipelinePool:
    """Persistent warm worker pool for transcript triage processing.

    Usage::

        with PipelinePool(workers=4) as pool:
            results = pool.process_batch(file_paths)

    Or manage lifecycle manually::

        pool = PipelinePool()
        results = pool.process_batch(file_paths)
        pool.shutdown()
    """

    def __init__(self, workers: int = None):
        self._workers = workers or os.cpu_count() or 4
        self._executor = ProcessPoolExecutor(
            max_workers=self._workers,
            initializer=_init_worker,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_batch(self, file_paths: list) -> list[TriageResult]:
        """Process a list of transcript file paths and return TriageResult objects.

        Results are returned in the same order as *file_paths*.
        """
        # executor.map preserves order
        return list(self._executor.map(_process_file_warm, file_paths))

    def shutdown(self, wait: bool = True):
        """Shut down the underlying ProcessPoolExecutor."""
        self._executor.shutdown(wait=wait)

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False
