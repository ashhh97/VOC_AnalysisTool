import requests
import json
import traceback

POSSIBLE_KEYS = [
    "sk-9c8cf1737d414de689770a971dcebfac"
]
MODEL_NAME = "qwen-flash-2025-07-28"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

def test_api():
    print(f"Testing model: {MODEL_NAME}")
    
    for key in POSSIBLE_KEYS:
        print(f"Testing with key: {key[:8]}...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        
        payload = {
            "model": MODEL_NAME,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, are you working?"
                    }
                ]
            },
            "parameters": {
                "max_tokens": 50,
                "temperature": 0.3
            }
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            except:
                print(f"Response Text: {response.text}")
                
            if response.status_code == 200:
                print("SUCCESS: API call worked!")
                return True
            else:
                print("FAILURE: API call failed.")
                
        except Exception as e:
            print(f"Exception: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    test_api()
