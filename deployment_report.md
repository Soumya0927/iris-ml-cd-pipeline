# 🚀 Iris API Deployment Report

## Deployment Summary
- **Timestamp**: 2025-07-26 15:25:29 UTC
- **Commit SHA**: `unknown`
- **Environment**: Production (GKE)
- **Service URL**: http://34.42.47.121

## Kubernetes Deployment Status

### Replicas
- **Desired**: 3
- **Ready**: 0
- **Available**: 0

### Pods Status
- ❌ `iris-api-deployment-659646694-h4nds` - Pending
- ❌ `iris-api-deployment-659646694-qt8x6` - Pending
- ❌ `iris-api-deployment-659646694-tzbgt` - Pending

## API Testing Results

### Endpoint Tests
- ❌ **ROOT** endpoint
  - Error: HTTPConnectionPool(host='34.42.47.121', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f7e8a469720>: Failed to establish a new connection: [Errno 111] Connection refused'))
- ❌ **HEALTH** endpoint
  - Error: HTTPConnectionPool(host='34.42.47.121', port=80): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f7e8a46a170>: Failed to establish a new connection: [Errno 111] Connection refused'))
- ❌ **PREDICT** endpoint
  - Error: HTTPConnectionPool(host='34.42.47.121', port=80): Max retries exceeded with url: /predict/ (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f7e8a46aad0>: Failed to establish a new connection: [Errno 111] Connection refused'))

## Performance Metrics

### Resource Usage
- Metrics server not available

## Overall Status: ⚠️

⚠️ **Deployment issues detected.** Please check the logs and test results above.
