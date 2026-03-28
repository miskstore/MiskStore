import json
import urllib.request
import urllib.error
import time

f = open('final_results.txt', 'w', encoding='utf-8')

def my_print(text):
    f.write(str(text) + '\n')
import urllib.error
import time

BASE_URL = 'http://127.0.0.1:8000/api'
HEADERS = {
    'Accept-Language': 'ar',
    'Content-Type': 'application/json',
    'X-Device-ID': 'translation-test-device'
}

def make_request(method, endpoint, payload=None):
    url = BASE_URL + endpoint
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    
    my_print(f"\n--- Testing {method} {endpoint} ---")
    try:
        response = urllib.request.urlopen(req)
        my_print(f"Status: {response.status}")
        try:
            my_print(f"Success Body: {json.loads(response.read().decode('utf-8'))}")
        except:
             my_print(f"Success Body: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        my_print(f"Status: {e.code}")
        try:
            my_print(f"Error Body: {json.loads(e.read().decode('utf-8'))}")
        except:
            my_print(f"Error Body: {e.read().decode('utf-8')}")
    except Exception as e:
        my_print(f"Other Error: {e}")

def run_tests():
    # 1. Login (Trigger SimpleJWT error)
    make_request('POST', '/auth/login/', {"email": "bad@email.com", "password": "bad"})
    
    # 2. Product Detail 404 (Trigger our custom "Product not found")
    make_request('GET', '/products/99999/')
    
    # 3. Add to Cart (Trigger Django's get_object_or_404 "No ProductVariant matches...")
    make_request('POST', '/cart/add/', {"variant_id": 99999, "quantity": 1})
    
    # 4. Auth required endpoints (Trigger DRF Authentication error)
    make_request('POST', '/orders/place/', {})
    
    # 5. Signup (Trigger custom "passwords doesn't match" error)
    make_request('POST', '/auth/signup/', {
        "email": "test@test.com", 
        "password1": "pass1", 
        "password2": "pass2",
        "full_name": "Test User"
    })
    
    # 6. Invalid Review Data (Trigger Serializer Validation error from DRF)
    # Actually reviews/add requires auth, so it will hit auth error. Let's send a bad request payload anyway.
    make_request('POST', '/reviews/add/', {"rating": 10}) # rating > 5 or missing product
    f.close()

if __name__ == '__main__':
    run_tests()
