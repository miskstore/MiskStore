import urllib.request
import urllib.error
import urllib.parse
import json

def test_login():
    url = 'http://127.0.0.1:8000/api/auth/login/' # Ensure correct path based on their URLs
    
    # Send bad credentials
    data = json.dumps({"email": "bad@email.com", "password": "bad"}).encode('utf-8')
    
    headers = {
        'Accept-Language': 'ar',
        'Content-Type': 'application/json'
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        response = urllib.request.urlopen(req)
        print("Status", response.status)
        print("Body", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Error Body:", e.read().decode('utf-8'))

if __name__ == '__main__':
    test_login()
