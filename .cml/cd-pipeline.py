#!/usr/bin/env python3
"""
CML Continuous Deployment Pipeline Script
Generates deployment report and validates the deployed model
"""

import os
import json
import requests
import time
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def get_service_url():
    """Get the external IP of the Kubernetes service"""
    print("Getting service URL...")
    
    # Wait for external IP to be assigned
    for i in range(30):  # Wait up to 5 minutes
        result = run_command("kubectl get service iris-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'")
        if result and result != "":
            return f"http://{result}"
        print(f"Waiting for external IP... ({i+1}/30)")
        time.sleep(10)
    
    return None

def test_api_endpoints(base_url):
    """Test API endpoints and return results"""
    results = {}
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        results['root'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        results['root'] = {'success': False, 'error': str(e)}
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        results['health'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        results['health'] = {'success': False, 'error': str(e)}
    
    # Test prediction endpoint
    test_data = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    
    try:
        response = requests.post(f"{base_url}/predict/", json=test_data, timeout=10)
        results['predict'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response': response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        results['predict'] = {'success': False, 'error': str(e)}
    
    return results

def get_deployment_info():
    """Get Kubernetes deployment information"""
    info = {}
    
    # Get deployment status
    deployment_status = run_command("kubectl get deployment iris-api-deployment -o json")
    if deployment_status:
        deployment_data = json.loads(deployment_status)
        info['replicas'] = {
            'desired': deployment_data['spec']['replicas'],
            'ready': deployment_data['status'].get('readyReplicas', 0),
            'available': deployment_data['status'].get('availableReplicas', 0)
        }
    
    # Get pods status
    pods_status = run_command("kubectl get pods -l app=iris-api -o json")
    if pods_status:
        pods_data = json.loads(pods_status)
        info['pods'] = []
        for pod in pods_data['items']:
            info['pods'].append({
                'name': pod['metadata']['name'],
                'status': pod['status']['phase'],
                'ready': all(condition['status'] == 'True' 
                           for condition in pod['status'].get('conditions', [])
                           if condition['type'] == 'Ready')
            })
    
    return info

def generate_cml_report():
    """Generate CML deployment report"""
    print("Generating CML deployment report...")
    
    # Get deployment timestamp
    deployment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_sha = os.getenv('GITHUB_SHA', 'unknown')
    
    # Get service URL
    service_url = get_service_url()
    
    report = f"""# 🚀 Iris API Deployment Report

## Deployment Summary
- **Timestamp**: {deployment_time}
- **Commit SHA**: `{commit_sha}`
- **Environment**: Production (GKE)
- **Service URL**: {service_url if service_url else 'Pending...'}

"""
    
    # Get deployment info
    deployment_info = get_deployment_info()
    
    if deployment_info:
        report += f"""## Kubernetes Deployment Status

### Replicas
- **Desired**: {deployment_info.get('replicas', {}).get('desired', 'N/A')}
- **Ready**: {deployment_info.get('replicas', {}).get('ready', 'N/A')}
- **Available**: {deployment_info.get('replicas', {}).get('available', 'N/A')}

### Pods Status
"""
        for pod in deployment_info.get('pods', []):
            status_emoji = "✅" if pod['ready'] else "❌"
            report += f"- {status_emoji} `{pod['name']}` - {pod['status']}\n"
    
    # Test API if service URL is available
    if service_url:
        print(f"Testing API at {service_url}")
        api_results = test_api_endpoints(service_url)
        
        report += f"""
## API Testing Results

### Endpoint Tests
"""
        
        for endpoint, result in api_results.items():
            emoji = "✅" if result.get('success') else "❌"
            report += f"- {emoji} **{endpoint.upper()}** endpoint\n"
            
            if result.get('success'):
                if endpoint == 'predict' and 'response' in result:
                    pred_response = result['response']
                    report += f"  - Predicted class: `{pred_response.get('predicted_class', 'N/A')}`\n"
                    if 'probabilities' in pred_response:
                        report += f"  - Confidence scores: {pred_response['probabilities']}\n"
            else:
                error = result.get('error', result.get('response', 'Unknown error'))
                report += f"  - Error: {error}\n"
    
    # Performance metrics (if available)
    report += f"""
## Performance Metrics

### Resource Usage
"""
    
    # Get resource usage
    resource_usage = run_command("kubectl top pods -l app=iris-api --no-headers 2>/dev/null || echo 'Metrics not available'")
    if resource_usage and "not available" not in resource_usage:
        report += f"```\n{resource_usage}\n```\n"
    else:
        report += "- Metrics server not available\n"
    
    # Deployment success indicator
    all_tests_passed = service_url and all(
        result.get('success', False) for result in 
        (test_api_endpoints(service_url).values() if service_url else [])
    )
    
    status_emoji = "✅" if all_tests_passed else "⚠️"
    report += f"""
## Overall Status: {status_emoji}

"""
    
    if all_tests_passed:
        report += "🎉 **Deployment successful!** All tests passed and the API is responding correctly.\n"
    else:
        report += "⚠️ **Deployment issues detected.** Please check the logs and test results above.\n"
    
    # Write report to file
    with open('deployment_report.md', 'w') as f:
        f.write(report)
    
    print("CML report generated successfully!")
    return all_tests_passed

def main():
    """Main pipeline execution"""
    print("Starting CML CD Pipeline...")
    
    # Generate and publish report
    success = generate_cml_report()
    
    # Use CML to publish the report
    run_command("cml comment create deployment_report.md")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
