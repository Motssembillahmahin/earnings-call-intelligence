import logging

from common import Settings, aws_client, get_logger, get_settings, get_tracer


def test_settings_defaults():
    s = Settings()
    assert s.service_name == "eci"
    assert s.environment == "dev"
    assert s.aws_region == "us-east-1"
    assert s.kafka_bootstrap_servers == "localhost:9092"
    assert s.temporal_address == "localhost:7233"
    assert s.database_url.startswith("postgresql+psycopg://")


def test_settings_reads_env_with_prefix(monkeypatch):
    monkeypatch.setenv("ECI_SERVICE_NAME", "recorder")
    monkeypatch.setenv("ECI_AWS_REGION", "eu-west-1")
    s = Settings()
    assert s.service_name == "recorder"
    assert s.aws_region == "eu-west-1"


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_get_logger_returns_named_stdlib_logger():
    log = get_logger("svc.discovery")
    assert isinstance(log, logging.Logger)
    assert log.name == "svc.discovery"


def test_get_tracer_returns_usable_tracer():
    tracer = get_tracer("svc.discovery")
    # A span can be started and ended without raising.
    with tracer.start_as_current_span("unit") as span:
        assert span is not None


def test_aws_client_builds_client_for_service():
    client = aws_client("s3")
    assert client.meta.service_model.service_name == "s3"
