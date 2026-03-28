import urllib.request
import urllib.error
import urllib.parse
import json

def test_api():
    url = 'http://127.0.0.1:8000/api/cart/add/'
    
    # Send a bad variant_id to trigger get_object_or_404 or bad stock error
    data = json.dumps({"variant_id": 99999, "quantity": 1000}).encode('utf-8')
    
    headers = {
        'Accept-Language': 'ar',
        'X-Device-ID': 'test-device-123',
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
    test_api()
