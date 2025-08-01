import time
import base64
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Optional: Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# ========== 🧠 Configuration ==========
GRAFANA_INSTANCE_ID = "1277332"  # Your Grafana.com user/org ID
GRAFANA_API_TOKEN = "glc_eyJvIjoiMTQ4OTg0OSIsIm4iOiJzdGFjay0xMzI1MjI3LWh0LXdyaXRlLXByb21ldGhldXMtYXBpcngiLCJrIjoieWg3OW95cjcwOFpscjd4NDQwajF4RUluIiwibSI6eyJyIjoicHJvZC1hcC1zb3V0aC0xIn19"  # Your write token

# Prepare base64 encoded Authorization header
auth_string = f"{GRAFANA_INSTANCE_ID}:{GRAFANA_API_TOKEN}"
auth_header = base64.b64encode(auth_string.encode()).decode()

# ========== 🚀 Exporter Setup ==========
otlp_exporter = OTLPSpanExporter(
    endpoint="https://tempo-prod-19-prod-ap-south-1.grafana.net/otlp/v1/traces",
    headers={
        "Authorization": f"Basic {auth_header}"
    }
)

# Set up Tracer
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({
            "service.name": "tempo-dummy-service"
        })
    )
)

tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(otlp_exporter)
)

# ========== 📦 Dummy Trace Generator ==========
print("🚀 Starting dummy trace generator...")
try:
    while True:
        with tracer.start_as_current_span("dummy-operation"):
            print("✅ Sent dummy trace to Tempo Cloud")
            time.sleep(5)

except KeyboardInterrupt:
    print("🛑 Trace sending interrupted by user.")
