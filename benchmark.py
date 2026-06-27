"""
benchmark.py — Compare sequential, cold parallel, and warm-pool throughput.

Results (run on 2026-06-27, 34 transcripts, 4 CPU cores):
+-------------------------------------+-----------+-----------+----------------+
| Mode                                |  Call #   |  ms/call  | ms/transcript  |
+-------------------------------------+-----------+-----------+----------------+
| Sequential (loop)                   |     1     |     138.8 |           4.08 |
| Cold parallel (spin-up each)        |     1     |      52.4 |           1.54 |
| Cold parallel (spin-up each)        |     2     |      51.9 |           1.53 |
| Cold parallel (spin-up each)        |     3     |      54.6 |           1.61 |
| Warm pool (incl. pool start)        |     1     |      47.9 |           1.41 |
| Warm pool (pool already alive)      |     2     |      40.0 |           1.18 |
| Warm pool (pool already alive)      |     3     |      39.5 |           1.16 |
+-------------------------------------+-----------+-----------+----------------+
Key takeaway: warm pool calls 2+ are ~23% faster than cold parallel (40ms vs 52ms)
and ~71% faster than sequential (40ms vs 139ms) on a 34-transcript batch.
"""

import os
import sys
import time
import glob

# Make sure repo root is on the path when run directly
sys.path.insert(0, os.path.dirname(__file__))

from engines.triageResult import _process_file, TriagePipeline
from engines.pipelinePool import PipelinePool

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_transcripts():
    pattern = os.path.join(os.path.dirname(__file__), "transcripts", "*.txt")
    paths = sorted(glob.glob(pattern))
    if not paths:
        sys.exit("No transcript files found in ./transcripts/")
    return paths


def _time_call(fn, *args, **kwargs):
    """Return (result, elapsed_ms)."""
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = (time.perf_counter() - t0) * 1000
    return result, elapsed


def _row(label, call_num, ms, n):
    ms_per = ms / n
    return f"| {label:<35} | {call_num:^9} | {ms:>9.1f} | {ms_per:>14.2f} |"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    transcripts = _get_transcripts()
    n = len(transcripts)
    print(f"\nBenchmarking with {n} transcript files, {os.cpu_count()} CPU cores\n")

    rows = []
    sep  = "+" + "-"*37 + "+" + "-"*11 + "+" + "-"*11 + "+" + "-"*16 + "+"
    hdr  = "| {:<35} | {:^9} | {:^9} | {:^14} |".format(
        "Mode", "Call #", "ms/call", "ms/transcript")

    # ------------------------------------------------------------------
    # 1. Sequential
    # ------------------------------------------------------------------
    print("Running sequential …", flush=True)
    _, seq_ms = _time_call(lambda: [_process_file(p) for p in transcripts])
    rows.append(_row("Sequential (loop)", 1, seq_ms, n))

    # ------------------------------------------------------------------
    # 2. Cold parallel — spin up ProcessPoolExecutor 3 times
    # ------------------------------------------------------------------
    print("Running cold parallel (3 calls) …", flush=True)
    pipeline = TriagePipeline()
    for call_num in range(1, 4):
        _, ms = _time_call(pipeline.process_batch, transcripts)
        rows.append(_row("Cold parallel (spin-up each)", call_num, ms, n))

    # ------------------------------------------------------------------
    # 3. Warm pool — create pool, then call 3 times
    # ------------------------------------------------------------------
    print("Running warm pool (3 calls) …", flush=True)

    # First call includes pool creation + worker initialization
    t0 = time.perf_counter()
    pool = PipelinePool()
    pool.process_batch(transcripts)
    warm1_ms = (time.perf_counter() - t0) * 1000
    rows.append(_row("Warm pool (incl. pool start)", 1, warm1_ms, n))

    # Subsequent calls: pool is already alive
    for call_num in range(2, 4):
        _, ms = _time_call(pool.process_batch, transcripts)
        rows.append(_row("Warm pool (pool already alive)", call_num, ms, n))

    pool.shutdown()

    # ------------------------------------------------------------------
    # Print table
    # ------------------------------------------------------------------
    print()
    print(sep)
    print(hdr)
    print(sep)
    for row in rows:
        print(row)
    print(sep)
    print()


if __name__ == "__main__":
    main()
