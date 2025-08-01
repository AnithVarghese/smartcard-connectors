import time
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Setup trace provider with resource info
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "local-tempo-test"})
    )
)

# Configure OTLP HTTP exporter (local Tempo default port 4318)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces"
)

# Add span processor
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Get tracer
tracer = trace.get_tracer(__name__)

# Send dummy traces in a loop
print("🚀 Sending dummy traces to local Tempo (http://localhost:4318)...")

while True:
    with tracer.start_as_current_span("dummy-span") as span:
        span.set_attribute("example.key", "example.value")
        print("✅ Trace sent")
        time.sleep(5)
