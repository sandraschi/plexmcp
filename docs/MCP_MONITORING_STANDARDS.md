# MCP Server Monitoring Standards

## Overview

This document outlines the comprehensive monitoring standards and patterns used across heavyweight MCP (Model Context Protocol) servers. It provides reusable templates, configurations, and best practices for implementing observability in MCP servers.

## Repository Analysis Summary

Based on analysis of existing repositories, the following MCP servers have monitoring implementations:

### 🟢 **Production-Ready Monitoring Stack**
- **VeoGen** - Complete observability stack with Grafana, Prometheus, Loki, Alertmanager
- **Tailscale-MCP** - Full monitoring with 4 Grafana dashboards, structured logging
- **Ring-MCP** - Comprehensive monitoring with security camera dashboards
- **DockerMCP** - Complete monitoring stack with backup automation

### 🟡 **Partial Monitoring Implementation**
- **AvatarMCP** - Basic Prometheus/Loki setup
- **HandbrakeMCP** - Grafana + Prometheus configuration
- **MCP-Server-Template** - Template with monitoring components

### 🔴 **Basic/Incomplete Monitoring**
- **Advanced-Memory-MCP** - Health checks only
- **Basic-Memory** - Health checks only
- **Nest-Protect-MCP** - Enhanced logging mentioned
- **VirtualDJ-MCP** - Performance monitoring mentioned
- **VRChat-MCP** - Performance monitoring planned

## Standard Monitoring Stack Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│   Prometheus    │───▶│     Grafana     │
│     (MCP)       │    │   (Metrics)     │    │  (Dashboards)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       │                       │
┌─────────────────┐              │                       │
│   Structured    │              │                       │
│    Logging      │              │                       │
└─────────────────┘              │                       │
         │                       │                       │
         ▼                       │                       │
┌─────────────────┐              │                       │
│    Promtail     │──────────────┼───────────────────────┤
│ (Log Shipping)  │              │                       │
└─────────────────┘              │                       │
         │                       │                       │
         ▼                       │                       │
┌─────────────────┐              │                       │
│      Loki       │──────────────┘                       │
│ (Log Storage)   │                                      │
└─────────────────┘                                      │
         │                                              │
         ▼                                              │
┌─────────────────┐                                      │
│ Alertmanager    │◀─────────────────────────────────────┘
│   (Alerts)      │
└─────────────────┘
```

### Component Responsibilities

1. **Prometheus**: Metrics collection and storage
2. **Grafana**: Visualization and dashboards
3. **Loki**: Log aggregation and storage
4. **Promtail**: Log shipping agent
5. **Alertmanager**: Alert routing and notifications

## Standard Configuration Files

### Docker Compose Template

```yaml
version: '3.8'

services:
  # Main MCP Application
  mcp-server:
    build: .
    container_name: ${PROJECT_NAME}-mcp
    ports:
      - "${MCP_PORT:-8080}:8080"
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - PROMETHEUS_PORT=${PROMETHEUS_PORT:-9091}
    volumes:
      - ./logs:/app/logs
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki

  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: ${PROJECT_NAME}-prometheus
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
    networks:
      - monitoring
    restart: unless-stopped

  # Loki - Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: ${PROJECT_NAME}-loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki:/etc/loki
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - monitoring
    restart: unless-stopped

  # Promtail - Log shipping
  promtail:
    image: grafana/promtail:latest
    container_name: ${PROJECT_NAME}-promtail
    volumes:
      - ./monitoring/promtail:/etc/promtail
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - monitoring
    restart: unless-stopped

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: ${PROJECT_NAME}-grafana
    ports:
      - "${GRAFANA_PORT:-3000}:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring
    restart: unless-stopped
    depends_on:
      - prometheus
      - loki

volumes:
  prometheus_data:
  loki_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

### Prometheus Configuration Template

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:9091']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
```

### Loki Configuration Template

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_scheduler:
  max_outstanding_requests_per_tenant: 2048

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  max_cache_freshness_per_query: 10m
  split_queries_by_interval: 15m
  max_query_parallelism: 32
```

### Promtail Configuration Template

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: mcp-server-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: mcp-server
          service: ${PROJECT_NAME}
          __path__: /app/logs/*.log

    pipeline_stages:
      - match:
          selector: '{job="mcp-server"}'
          stages:
            - json:
                expressions:
                  timestamp: timestamp
                  level: level
                  logger: logger
                  message: event
                  operation: operation
                  device_id: device_id
                  status: status
                  duration: duration
            - timestamp:
                source: timestamp
                format: RFC3339
            - labels:
                level:
                logger:
                operation:
                device_id:
                status:
                duration:
            - output:
                source: message

  - job_name: system-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*log
```

## Standard Dashboard Templates

### 1. System Overview Dashboard

```json
{
  "dashboard": {
    "title": "${PROJECT_NAME} - System Overview",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"mcp-server\"}",
            "legendFormat": "MCP Server"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx Errors/sec"
          }
        ]
      }
    ]
  }
}
```

### 2. Application Performance Dashboard

```json
{
  "dashboard": {
    "title": "${PROJECT_NAME} - Performance",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes",
            "legendFormat": "Resident Memory"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m])",
            "legendFormat": "CPU Usage"
          }
        ]
      }
    ]
  }
}
```

### 3. Logs Dashboard

```json
{
  "dashboard": {
    "title": "${PROJECT_NAME} - Logs",
    "panels": [
      {
        "title": "Log Stream",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"mcp-server\"}",
            "refId": "A"
          }
        ]
      },
      {
        "title": "Error Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"mcp-server\", level=\"error\"}",
            "refId": "A"
          }
        ]
      }
    ]
  }
}
```

## Standard Alert Rules

```yaml
groups:
  - name: mcp-server-alerts
    rules:
      - alert: MCPServerDown
        expr: up{job="mcp-server"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MCP Server is down"
          description: "MCP Server has been down for more than 1 minute"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 0.1 requests per second"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 1000000000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 1GB"

      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80%"
```

## Environment Configuration Template

```bash
# .env.template
PROJECT_NAME=mcp-server
MCP_PORT=8080
GRAFANA_PORT=3000
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO
PROMETHEUS_METRICS_PORT=9091

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# Optional: Alertmanager Configuration
ALERTMANAGER_WEBHOOK_URL=http://localhost:9093/api/v1/alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

## Startup Script Template

```bash
#!/bin/bash
# start-monitoring.sh

set -e

echo "Starting ${PROJECT_NAME} monitoring stack..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Create necessary directories
mkdir -p logs
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

# Start the monitoring stack
docker-compose up -d

echo "Monitoring stack started successfully!"
echo "Access Grafana at: http://localhost:${GRAFANA_PORT:-3000} (${GRAFANA_USER:-admin}/${GRAFANA_PASSWORD:-admin})"
echo "Access Prometheus at: http://localhost:${PROMETHEUS_PORT:-9090}"
echo "Access Loki at: http://localhost:3100"
echo "Access MCP Server at: http://localhost:${MCP_PORT:-8080}"
```

## Best Practices

### 1. Logging Standards
- Use structured logging with JSON format
- Include correlation IDs for request tracing
- Log all significant operations and errors
- Use consistent field names across services

### 2. Metrics Standards
- Export Prometheus metrics on a dedicated port
- Use consistent metric naming conventions
- Include labels for dimensions (device_id, operation, status)
- Implement health check endpoints

### 3. Dashboard Standards
- Create focused dashboards for different audiences
- Use consistent color schemes and layouts
- Include time range selectors and refresh intervals
- Provide drill-down capabilities

### 4. Alert Standards
- Set appropriate thresholds for alerts
- Use severity levels (critical, warning, info)
- Include meaningful descriptions and runbooks
- Test alerting channels regularly

## Implementation Checklist

- [ ] Docker Compose configuration
- [ ] Prometheus configuration
- [ ] Loki configuration
- [ ] Promtail configuration
- [ ] Grafana dashboards
- [ ] Alert rules
- [ ] Environment configuration
- [ ] Startup scripts
- [ ] Health check endpoints
- [ ] Metrics export
- [ ] Structured logging
- [ ] Documentation

## Repository-Specific Customizations

### VeoGen
- Video generation specific metrics
- Movie project dashboards
- User management analytics
- API usage tracking

### Tailscale-MCP
- Network topology visualization
- Device activity monitoring
- Security event tracking
- File transfer analytics

### Ring-MCP
- Security camera monitoring
- Motion detection analytics
- Device status tracking
- Multi-server support

### DockerMCP
- Container health monitoring
- Resource usage tracking
- Image management metrics
- Backup automation logs

## Troubleshooting Guide

### Common Issues

1. **Prometheus not scraping metrics**
   - Check if metrics endpoint is accessible
   - Verify scrape configuration
   - Check network connectivity

2. **Loki not receiving logs**
   - Verify Promtail configuration
   - Check log file paths
   - Verify Loki connectivity

3. **Grafana dashboards not loading**
   - Check data source configuration
   - Verify Prometheus/Loki connectivity
   - Check dashboard JSON validity

4. **Alerts not firing**
   - Verify alert rules syntax
   - Check Alertmanager configuration
   - Verify notification channels

### Debug Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f prometheus
docker-compose logs -f loki
docker-compose logs -f grafana

# Test metrics endpoint
curl http://localhost:9091/metrics

# Test log ingestion
curl -X POST http://localhost:3100/loki/api/v1/push
```

## Conclusion

This monitoring standard provides a comprehensive foundation for implementing observability in heavyweight MCP servers. By following these patterns and templates, you can ensure consistent monitoring across all your MCP projects while allowing for project-specific customizations.

The key is to start with the standard stack and gradually add project-specific metrics, dashboards, and alerts as needed. This approach ensures consistency while maintaining flexibility for unique requirements.
