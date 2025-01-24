import requests
import json

# api key 450e9c2c0a859bccd215724a8741b2309ee3f208
# Define the API endpoint and data
url = 'https://nooklz.com/api/accounts/check'
data = {
    "account_ids":[
        17565483
    ]
}

# Replace {{token}} with your actual token
headers = {
    "Authorization": "Token 450e9c2c0a859bccd215724a8741b2309ee3f208"
}

try:
    # Send POST request
    response = requests.post(url, json=data, headers=headers)
    
    # Print raw response details
    print("Status Code:", response.status_code)
    #print("Response Text:", response.text)
    
    # Handle non-200 status codes
    if response.status_code != 200:
        print("Error: Non-200 status code received.")
        #exit()
    
    # Try to parse the JSON response
    try:
        json_response = response.json()
        print("JSON Response:", json_response)
        print("Raw Response Text:", response.text)
    except ValueError:
        print("Error: Response is not valid JSON.")
        print("Raw Response Text:", response.text)

except requests.RequestException as e:
    print(f"An error occurred: {e}")

#print(response)