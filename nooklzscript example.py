# https://www.postman.com/technical-cosmonaut-73167223/workspace/nooklz-api/collection/26823261-96628c08-2d41-4434-ab88-c6cc7ed40aff
import requests
import json

# Define the API endpoint and data
url = 'https://nooklz.com/api/proxies/check'
data = {
    "proxy_ids": [
        47141,
        47084
    ]
}

# Make the POST request
response = requests.post(url, json=data)

# Check the response
if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)