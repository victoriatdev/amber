# Amber - SRE-Focused Demo Application

Amber is a minimal Flask service instrumented with Prometheus metrics to practice monitoring, alerting, autoscaling, chaos testing, and incident response.

## ./quickstart
```bash
docker compose up --build
```

- App: http://localhost:8000
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

In Grafana, add a Prometheus data source with URL `http://prometheus:9090`. Then create a dashboard with these queries:

- Requests by status:
  ```promql
  sum by (endpoint, http_status) (rate(amber_http_requests_total[1m]))
  ```

- Request latency (95th percentile):
  ```promql
  histogram_quantile(0.95, sum by (le, endpoint) (rate(amber_request_latency_seconds_bucket[5m])))
  ```

- Error rate:
  ```promql
  sum by (endpoint) (rate(amber_http_errors_total[1m]))
  ```

- Uptime:
  ```promql
  amber_uptime_seconds
  ```

## ./dev --local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## ./endpoints
- `/` — JSON hello with links
- `/health` — Liveness check (HTTP 200)
- `/metrics` — Prometheus exposition format
- `/error` — Intentionally raises an exception for testing

## ./load-testing --optional true
Example with [`hey`](https://github.com/rakyll/hey):
```bash
hey -z 30s -q 20 http://localhost:8000/
```

## ./todo
- Add readiness checks (DB ping, cache check)
- Define SLIs/SLOs; add burn-rate alerts in Prometheus
- Deploy to Kubernetes; add HPA
- Run chaos tests (kill container, inject latency)
- Write a postmortem after triggering `/error` during load
