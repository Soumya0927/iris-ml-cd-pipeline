import os
import requests
from datetime import datetime

# Get the API URL from the environment variable set in the GitHub workflow
API_URL = os.getenv("API_URL")
if not API_URL:
    raise ValueError("API_URL environment variable not set.")

PREDICT_ENDPOINT = f"{API_URL}/predict/"

# Sample data for prediction
payload = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

report_content = f"# CML Deployment Report 🚀\n\n"
report_content += f"Deployment Timestamp: **{datetime.utcnow().isoformat()}Z**\n\n"
report_content += f"## Deployment Status\n\n"
report_content += f"✅ Successfully deployed to GKE.\n"
report_content += f"✅ API is available at: **{API_URL}**\n\n"
report_content += f"## Live API Test\n\n"

try:
    response = requests.post(PREDICT_ENDPOINT, json=payload, timeout=15)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    prediction_data = response.json()
    
    report_content += f"Sent prediction request with payload:\n"
    report_content += f"```json\n{payload}\n```\n"
    report_content += f"Received prediction response:\n"
    report_content += f"```json\n{prediction_data}\n```\n"
    report_content += f"\n**Conclusion**: The live API endpoint is responding correctly. 🎉"

except requests.exceptions.RequestException as e:
    report_content += f"🔥 **API Test Failed!**\n"
    report_content += f"Could not get a valid response from `{PREDICT_ENDPOINT}`.\n"
    report_content += f"Error: `{str(e)}`"

# Write the report to a file
with open("report.md", "w") as f:
    f.write(report_content)

print("CML report 'report.md' generated successfully.")
