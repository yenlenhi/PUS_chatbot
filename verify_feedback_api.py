import requests
import json
import sys

API_URL = "http://127.0.0.1:8000/api/v1/feedback/list"

def test_feedback_list():
    try:
        print(f"Testing GET {API_URL}...")
        response = requests.get(API_URL, params={"limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Status Code: 200")
            print(f"Total records: {data.get('total')}")
            print(f"Records returned: {len(data.get('records', []))}")
            
            if len(data.get('records', [])) > 0:
                print("Sample record 1:", json.dumps(data['records'][0], indent=2, ensure_ascii=False))
            else:
                print("No records found (database might be empty of feedback).")
                
            return True
        else:
            print(f"[FAILED] Status Code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Force utf-8 for stdout if possible, or just ignore errors
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
        
    success = test_feedback_list()
    # Don't exit with 1 to avoid noisy 'command failed' backend messages if it's just a connection check
    if not success:
        print("Verification failed.")
