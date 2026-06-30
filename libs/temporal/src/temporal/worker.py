"""Helpers for building Temporal workers and logging from activities."""

import logging
from collections.abc import Sequence
from typing import Any

from temporalio.worker import Worker

from common import get_logger


def build_worker(
    client: Any,
    task_queue: str,
    workflows: Sequence[type] | None = None,
    activities: Sequence[Any] | None = None,
) -> Worker:
    """Construct a Temporal ``Worker`` bound to a task queue.

    ``workflows`` and ``activities`` default to empty so a worker can be built
    incrementally as a service grows.
    """
    return Worker(
        client,
        task_queue=task_queue,
        workflows=list(workflows or []),
        activities=list(activities or []),
    )


def activity_logger() -> logging.Logger:
    """Return the shared logger for activity code."""
    return get_logger("eci.activity")
