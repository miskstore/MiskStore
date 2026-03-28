import urllib.request
import urllib.error
import urllib.parse
import json

def test_api():
    url = 'http://127.0.0.1:8000/api/cart/'
    
    # We will pass a fake device ID, and Accept-Language: ar
    headers = {
        'Accept-Language': 'ar',
        'X-Device-ID': 'test-device-123',
        'Content-Type': 'application/json'
    }
    
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        response = urllib.request.urlopen(req)
        print("Status Code:", response.status)
        print("Response Body:", response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Error Body:", e.read().decode('utf-8'))
    except Exception as e:
        print("Other Error:", str(e))

if __name__ == '__main__':
    test_api()
