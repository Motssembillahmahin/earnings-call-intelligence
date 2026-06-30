"""Standard Temporal retry-policy presets used across workflows and activities."""

from datetime import timedelta

from temporalio.common import RetryPolicy

# Default: durable, patient retries for normal activities.
DEFAULT_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=60),
    maximum_attempts=5,
)

# Short: tight retries for fast, idempotent operations that should fail fast.
SHORT_RETRY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=10),
    maximum_attempts=3,
)
