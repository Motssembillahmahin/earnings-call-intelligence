"""OpenTelemetry tracing setup. One trace per event_id flows across all services."""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Tracer

_PROVIDER: TracerProvider | None = None


def setup_tracing(service_name: str | None = None) -> TracerProvider:
    """Install a global ``TracerProvider`` (idempotent).

    Spans are exported to the OTLP endpoint when one is configured in settings;
    otherwise the provider records spans (so trace context still propagates) but
    attaches no exporter. Safe to call multiple times; the first call wins.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        return _PROVIDER

    from .settings import get_settings

    settings = get_settings()
    resource = Resource.create({"service.name": service_name or settings.service_name})
    provider = TracerProvider(resource=resource)

    if settings.otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otlp_endpoint))
        )

    trace.set_tracer_provider(provider)
    _PROVIDER = provider
    return provider


def get_tracer(name: str) -> Tracer:
    """Return a tracer for ``name`` (works with or without ``setup_tracing``)."""
    return trace.get_tracer(name)
