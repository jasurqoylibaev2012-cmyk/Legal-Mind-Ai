import requests
import json

BASE_URL = "https://unautographed-cornelia-nonbibulously.ngrok-free.dev"

def test_index():
    try:
        # We can add a header to skip the warning for programmatic access checks
        headers = {"ngrok-skip-browser-warning": "true"}
        resp = requests.get(f"{BASE_URL}/", headers=headers)
        print(f"GET /: {resp.status_code}")
        if resp.status_code == 200:
            if "<title>LegalMind AI</title>" in resp.text:
                print("  Index Loaded OK (Correct Title Found)")
            else:
                print("  Index Loaded BUT Title Mismatch (Possible Ngrok Warning)")
                print(f"  First 100 chars: {resp.text[:100]}")
        else:
            print("  Index Failed")
    except Exception as e:
        print(f"GET / Error: {e}")

def test_quick_chat():
    try:
        resp = requests.post(f"{BASE_URL}/api/quick-chat", json={"key": "unknown"})
        print(f"POST /api/quick-chat: {resp.status_code}")
        print(f"  Response: {resp.json()}")
    except Exception as e:
        print(f"POST /api/quick-chat Error: {e}")

def test_notary():
    try:
        resp = requests.post(f"{BASE_URL}/api/notary", json={"location": "tash"})
        print(f"POST /api/notary: {resp.status_code}")
        print(f"  Response: {resp.json()}")
    except Exception as e:
        print(f"POST /api/notary Error: {e}")

if __name__ == "__main__":
    print("Starting Tests...")
    test_index()
    test_quick_chat()
    test_notary()
    print("Tests Completed.")
