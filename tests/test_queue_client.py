import fakeredis
from rq import Queue

from src.queue import FakeQueueClient, RQQueueClient


def sample_task(text: str) -> str:
    return text.upper()


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
