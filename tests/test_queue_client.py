import fakeredis
from rq import Queue, SimpleWorker

from src.queue import FakeQueueClient, QueueRetryPolicy, RQQueueClient


def sample_task(text: str) -> str:
    return text.upper()


_retry_attempts = 0


def retry_once_task() -> str:
    global _retry_attempts
    _retry_attempts += 1
    if _retry_attempts == 1:
        raise RuntimeError("transient test failure")
    return "ok"


def test_fake_queue_client_enqueue() -> None:
    client = FakeQueueClient()

    enqueued = client.enqueue(
        queue_name="default",
        function=sample_task,
        args=("hello",),
    )

    assert enqueued.queue_name == "default"
    assert enqueued.function_name == "sample_task"
    assert enqueued.args == ("hello",)
    assert enqueued.kwargs == {}
    assert len(client.enqueued_jobs) == 1


def test_rq_queue_client_enqueue_with_local_connection() -> None:
    connection = fakeredis.FakeRedis()
    client = RQQueueClient(connection=connection)

    enqueued = client.enqueue(
        queue_name="default",
        function=sample_task,
        args=("hello",),
        description="test job",
    )

    queue = Queue(name="default", connection=connection)
    fetched_job = queue.fetch_job(enqueued.job_id)

    assert fetched_job is not None
    assert fetched_job.description == "test job"
    assert fetched_job.func_name.endswith("sample_task")
    assert fetched_job.args == ("hello",)


def test_rq_queue_client_persists_bounded_retry_policy() -> None:
    connection = fakeredis.FakeRedis()
    client = RQQueueClient(connection=connection)

    enqueued = client.enqueue(
        queue_name="telegram",
        function=sample_task,
        args=("hello",),
        retry_policy=QueueRetryPolicy(max_retries=2, retry_intervals=(5, 30)),
    )

    fetched_job = Queue(name="telegram", connection=connection).fetch_job(
        enqueued.job_id
    )
    assert fetched_job is not None
    assert fetched_job.retries_left == 2
    assert client.is_available() is True


def test_rq_worker_retries_transient_job_after_worker_restart() -> None:
    global _retry_attempts
    _retry_attempts = 0
    connection = fakeredis.FakeRedis()
    client = RQQueueClient(connection=connection)
    enqueued = client.enqueue(
        queue_name="telegram",
        function=retry_once_task,
        retry_policy=QueueRetryPolicy(max_retries=1, retry_intervals=(0,)),
    )

    first_worker = SimpleWorker(
        [Queue(name="telegram", connection=connection)],
        connection=connection,
    )
    first_worker.work(burst=True)
    second_worker = SimpleWorker(
        [Queue(name="telegram", connection=connection)],
        connection=connection,
    )
    second_worker.work(burst=True)

    fetched_job = Queue(name="telegram", connection=connection).fetch_job(
        enqueued.job_id
    )
    assert _retry_attempts == 2
    assert fetched_job is not None
    assert fetched_job.is_finished
