#!/usr/bin/env python3
"""Run the LearnLoop RQ worker for Telegram background jobs."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


def ensure_repo_root_on_sys_path() -> Path:
    """Make imports independent of the worker's cwd or script launch path."""

    repo_root = Path(__file__).resolve().parents[1]
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)
    return repo_root


ensure_repo_root_on_sys_path()

from redis import Redis
from rq import Queue, Worker
from rq.utils import import_attribute


def validate_telegram_job_import() -> None:
    """Fail fast if RQ cannot resolve the queued Telegram callable."""

    from src.worker.telegram import (
        TELEGRAM_WEBHOOK_JOB_PATH,
        process_telegram_webhook_job,
    )

    resolved = import_attribute(TELEGRAM_WEBHOOK_JOB_PATH)
    if resolved is not process_telegram_webhook_job:
        raise RuntimeError(
            "RQ resolved a different Telegram worker callable"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue",
        default="telegram",
        help="RQ queue name to consume (default: telegram)",
    )
    args = parser.parse_args()

    validate_telegram_job_import()

    redis_url = os.getenv("REDIS_URL", "").strip()
    if not redis_url:
        parser.error("REDIS_URL is required to start the worker")

    connection = Redis.from_url(redis_url)
    connection.ping()
    worker = Worker([Queue(name=args.queue, connection=connection)], connection=connection)
    worker.work()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
