import requests
import json

try:
    response = requests.post('http://localhost:5000/submit', json={'entry': 'Verification entry from script'})
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
