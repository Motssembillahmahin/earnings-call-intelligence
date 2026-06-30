import logging
from datetime import timedelta

import temporal.worker as worker_mod
from temporal import DEFAULT_RETRY, SHORT_RETRY, activity_logger, build_worker


def test_default_retry_policy():
    assert DEFAULT_RETRY.maximum_attempts == 5
    assert DEFAULT_RETRY.backoff_coefficient == 2.0
    assert DEFAULT_RETRY.initial_interval == timedelta(seconds=1)


def test_short_retry_is_tighter_than_default():
    assert SHORT_RETRY.maximum_attempts < DEFAULT_RETRY.maximum_attempts
    assert SHORT_RETRY.maximum_interval <= DEFAULT_RETRY.maximum_interval


def test_activity_logger_is_named_logger():
    log = activity_logger()
    assert isinstance(log, logging.Logger)
    assert log.name == "eci.activity"


class FakeWorker:
    def __init__(self, client, **kwargs):
        self.client = client
        self.kwargs = kwargs


def test_build_worker_wires_task_queue_workflows_activities(monkeypatch):
    monkeypatch.setattr(worker_mod, "Worker", FakeWorker)

    async def sample_activity():
        return "ok"

    class SampleWorkflow:
        pass

    client = object()
    w = build_worker(
        client,
        task_queue="eci-tq",
        workflows=[SampleWorkflow],
        activities=[sample_activity],
    )
    assert isinstance(w, FakeWorker)
    assert w.client is client
    assert w.kwargs["task_queue"] == "eci-tq"
    assert w.kwargs["workflows"] == [SampleWorkflow]
    assert w.kwargs["activities"] == [sample_activity]


def test_build_worker_defaults_empty_collections(monkeypatch):
    monkeypatch.setattr(worker_mod, "Worker", FakeWorker)
    w = build_worker(object(), task_queue="tq")
    assert w.kwargs["workflows"] == []
    assert w.kwargs["activities"] == []
