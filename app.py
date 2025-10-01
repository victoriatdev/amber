
from flask import Flask, jsonify, request, g
import time
import os

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# --- Metrics ---
REQUEST_COUNT = Counter(
    "amber_http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "amber_request_latency_seconds", "Request latency", ["endpoint"]
)

ERROR_COUNT = Counter(
    "amber_http_errors_total", "Total HTTP errors", ["endpoint", "exception_type"]
)

UP = Gauge("amber_app_up", "1 if the app is up")
UP.set(1)

START_TIME = time.time()
UPTIME = Gauge("amber_uptime_seconds", "App uptime in seconds")

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def record_metrics(response):
    # update uptime
    UPTIME.set(time.time() - START_TIME)

    if request.endpoint != "metrics":
        resp_code = response.status_code
        REQUEST_COUNT.labels(request.method, f"/{request.endpoint or 'unknown'}", resp_code).inc()
        if hasattr(g, "start_time"):
            latency = time.time() - g.start_time
            REQUEST_LATENCY.labels(f"/{request.endpoint or 'unknown'}").observe(latency)
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    endpoint = f"/{request.endpoint or 'unknown'}"
    ERROR_COUNT.labels(endpoint, e.__class__.__name__).inc()
    return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return jsonify(
        {
            "app": "Amber",
            "message": "Hello from Amber 💎",
            "docs": "/readme",
            "health": "/health",
            "metrics": "/metrics"
        }
    )

@app.route("/health")
def health():
    # simple liveness; extend with deeper checks as needed
    return jsonify({"status": "ok"}), 200

@app.route("/readme")
def readme():
    return jsonify({
        "about": "Amber is a tiny SRE-friendly demo app for learning monitoring, alerting, and reliability practices.",
        "endpoints": ["/", "/health", "/metrics"],
        "metrics_prefix": "amber_* (Prometheus format)"
    })

@app.route("/error")
def error():
    # intentionally raise an error to test alerts
    raise RuntimeError("Intentional error for testing")

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
