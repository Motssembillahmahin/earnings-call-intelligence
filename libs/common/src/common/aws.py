"""Lazy boto3 client factory using the shared region setting."""

from typing import Any

import boto3


def aws_client(service: str, region: str | None = None) -> Any:
    """Return a boto3 client for ``service`` in the configured region."""
    from .settings import get_settings

    return boto3.client(service, region_name=region or get_settings().aws_region)
