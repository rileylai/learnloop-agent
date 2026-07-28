#!/usr/bin/env python3
"""Run the LearnLoop RQ worker for Telegram background jobs."""

from __future__ import annotations

import argparse
import os

from redis import Redis
from rq import Queue, Worker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue",
        default="telegram",
        help="RQ queue name to consume (default: telegram)",
    )
    args = parser.parse_args()

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
