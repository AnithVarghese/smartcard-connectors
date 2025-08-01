from prometheus_client import start_http_server, Gauge
import random, time

# Fake metrics
cpu_usage = Gauge('dummy_cpu_usage', 'Random CPU usage %')
memory_usage = Gauge('dummy_memory_usage', 'Random Memory usage MB')
network_io = Gauge('dummy_network_io', 'Random Network I/O KBps')

# Start HTTP server at port 8000
start_http_server(8000)
print("Dummy exporter running at http://localhost:8000/metrics")

while True:
    cpu_usage.set(random.uniform(10, 90))
    memory_usage.set(random.uniform(1000, 16000))
    network_io.set(random.uniform(100, 1000))
    time.sleep(1)
