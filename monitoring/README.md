# Monitoring & Observability

This directory is an observability placeholder to illustrate DevOps principles for monitoring the "Multi-Environment Deployment Manager".

## Monitoring Goals

In a production environment, DevOps principles require visibility into the state and health of our running applications. Implementing a monitoring solution like **Prometheus** (coupled with Grafana) or **Nagios** can help us achieve this.

### Metrics to Monitor:

1. **Container Health:**
   - **How?** Check the `/health` endpoint of our Flask app or verify the pod status via Kubernetes metrics (like `kube-state-metrics`).
   - **Why?** It automatically detects if our application process crashes or becomes unresponsive so we can trigger self-healing (like Kubernetes restarting the pod) or send alerts.

2. **CPU and Memory Usage:**
   - **How?** Expose cAdvisor or node-exporter metrics to Prometheus.
   - **Why?** Allows us to establish baseline resource limits, perform capacity planning, and detect potential memory leaks or unexpected CPU spikes before they cause outages.

3. **Request Latency and HTTP error rates:**
   - **How?** Instrument the Flask application with a library (like `prometheus-flask-exporter`) to track the time it takes to serve a request and HTTP response codes.
   - **Why?** Tracking the golden signals (Latency, Traffic, Errors, and Saturation) allows us to measure the user experience and ensure we meet our Service Level Objectives (SLOs).
