"""Background worker: executes queued runs (QUEUE_MODE=worker).

    uv run python -m app.worker            # loop forever
    uv run python -m app.worker --once     # drain the queue, then exit

Start as many workers as you like; each run is claimed atomically.
"""

from __future__ import annotations

import argparse
import logging
import signal
import time
from datetime import timedelta

from .config import settings
from .db import init_db
from .services.pipeline import execute_run
from .services.queue import next_queued_run_id, recover_interrupted_runs

log = logging.getLogger("topiome.worker")
_stopping = False


def _stop(signum, frame) -> None:  # noqa: ANN001, ARG001
    global _stopping
    _stopping = True
    log.info("signal %s received; finishing the current run, then exiting", signum)


def run_once() -> int:
    """Execute queued runs until none are left. Returns how many were processed."""
    processed = 0
    while not _stopping:
        run_id = next_queued_run_id()
        if run_id is None:
            break
        log.info("executing run %s", run_id)
        execute_run(run_id)  # no-op if another worker claimed it first
        processed += 1
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Topiome run worker")
    parser.add_argument("--once", action="store_true", help="drain the queue and exit")
    parser.add_argument("--poll", type=float, default=2.0, help="seconds between queue checks")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    init_db()
    stale = recover_interrupted_runs(stale_after=timedelta(hours=settings.run_timeout_hours))
    if stale:
        log.warning("marked %d stale running runs as interrupted", stale)
    log.info("worker started (queue_mode=%s)", settings.queue_mode)
    if args.once:
        log.info("processed %d runs", run_once())
        return
    while not _stopping:
        if run_once() == 0:
            time.sleep(args.poll)


if __name__ == "__main__":
    main()
