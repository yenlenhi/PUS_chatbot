import requests
import json
import sys

url = "http://localhost:8000/api/v1/chat"
headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
data = {"message": "Xin chào, hãy giới thiệu về trường Đại học An ninh Nhân dân ngắn gọn.", "conversation_id": "verify_stream_001"}

print(f"Sending request to {url}...")
try:
    with requests.post(url, headers=headers, json=data, stream=True, timeout=60) as r:
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('content-type')}")
        
        if r.status_code != 200:
            print(f"Error: {r.text}")
            sys.exit(1)
            
        counter = 0
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Chunk {counter}: {decoded_line[:100]}...") # Print first 100 chars
                counter += 1
                if counter > 10 and "data: {" in decoded_line:
                     # Stop early if we see valid data to save time (or let it finish)
                     pass 
        print("Stream finished.")
except Exception as e:
    print(f"Exception: {e}")
