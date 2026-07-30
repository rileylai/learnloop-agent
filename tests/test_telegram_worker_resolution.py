from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap

import fakeredis
from rq import Queue
from rq.utils import import_attribute

from src.queue import RQQueueClient, get_callable_import_path
from src.worker.telegram import (
    TELEGRAM_WEBHOOK_JOB_PATH,
    process_telegram_webhook_job,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_SCRIPT = REPO_ROOT / "scripts" / "run_worker.py"


def _subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return environment


def test_fresh_subprocess_imports_module_level_worker_callable() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from src.worker.telegram import "
                "TELEGRAM_WEBHOOK_JOB_PATH, process_telegram_webhook_job; "
                "assert callable(process_telegram_webhook_job); "
                "assert process_telegram_webhook_job.__module__ == "
                "'src.worker.telegram'; "
                "assert TELEGRAM_WEBHOOK_JOB_PATH == "
                "'src.worker.telegram.process_telegram_webhook_job'"
            ),
        ],
        cwd=REPO_ROOT,
        env=_subprocess_environment(),
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_non_repo_cwd_worker_bootstrap_resolves_job_function(tmp_path: Path) -> None:
    probe = textwrap.dedent(
        """
        import runpy
        import sys

        namespace = runpy.run_path(sys.argv[1], run_name="worker_import_probe")
        namespace["validate_telegram_job_import"]()
        assert namespace["ensure_repo_root_on_sys_path"]().__str__() in sys.path
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", probe, str(WORKER_SCRIPT)],
        cwd=tmp_path,
        env=_subprocess_environment(),
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_worker_startup_validates_import_before_redis_requirement(
    tmp_path: Path,
) -> None:
    environment = _subprocess_environment()
    environment.pop("REDIS_URL", None)
    result = subprocess.run(
        [sys.executable, str(WORKER_SCRIPT)],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "REDIS_URL is required" in result.stderr
    assert "Invalid attribute name" not in result.stderr


def test_rq_import_attribute_resolves_canonical_worker_path() -> None:
    resolved = import_attribute(TELEGRAM_WEBHOOK_JOB_PATH)

    assert resolved is process_telegram_webhook_job
    assert get_callable_import_path(process_telegram_webhook_job) == (
        TELEGRAM_WEBHOOK_JOB_PATH
    )


def test_enqueue_path_matches_actual_worker_callable() -> None:
    connection = fakeredis.FakeRedis()
    enqueued = RQQueueClient(connection=connection).enqueue(
        queue_name="telegram",
        function=process_telegram_webhook_job,
        args=(None, "555", "/help", None, None, [], "worker-test"),
    )
    job = Queue(name="telegram", connection=connection).fetch_job(enqueued.job_id)

    assert job is not None
    assert job.func_name == TELEGRAM_WEBHOOK_JOB_PATH
    assert enqueued.function_name == TELEGRAM_WEBHOOK_JOB_PATH
    assert import_attribute(job.func_name) is process_telegram_webhook_job
