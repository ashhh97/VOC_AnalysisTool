#!/usr/bin/env python3
"""测试Hugging Face API是否可用"""
import requests
import json

API_URLS = [
    "https://api-inference.huggingface.co/models/Qwen/Qwen2-7B-Instruct",
    "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct",
    "https://api-inference.huggingface.co/models/Qwen/Qwen2-1.5B-Instruct",
    "https://api-inference.huggingface.co/models/THUDM/chatglm3-6b"
]

def test_api(api_url):
    """测试单个API端点"""
    print(f"\n测试: {api_url}")
    try:
        prompt = "请分析以下用户反馈，返回JSON格式结果：{\"sentiment\": \"正面/负面/中性\", \"category\": \"功能问题/性能问题/界面问题/体验问题/服务问题/价格问题/其他问题\"}\n\n用户反馈：测试反馈\n\n请只返回JSON，不要其他内容："
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ API可用！")
            print(f"  响应预览: {str(result)[:200]}")
            return True
        elif response.status_code == 503:
            error_info = response.json() if response.content else {}
            estimated_time = error_info.get('estimated_time', 0)
            print(f"  ⚠ 模型正在加载，预计等待时间: {estimated_time}秒")
            return None
        elif response.status_code == 410:
            print(f"  ✗ 模型不可用 (410 - Gone)")
            return False
        elif response.status_code == 429:
            print(f"  ⚠ 请求过多 (429)，需要等待")
            return None
        else:
            try:
                error_detail = response.json()
                print(f"  ✗ 错误: {error_detail}")
            except:
                print(f"  ✗ 错误: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"  ✗ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 未知错误: {e}")
        return False

def main():
    print("=" * 80)
    print("Hugging Face API 可用性测试")
    print("=" * 80)
    
    available_count = 0
    unavailable_count = 0
    loading_count = 0
    
    for api_url in API_URLS:
        result = test_api(api_url)
        if result is True:
            available_count += 1
        elif result is False:
            unavailable_count += 1
        else:
            loading_count += 1
    
    print("\n" + "=" * 80)
    print("测试总结:")
    print(f"  ✓ 可用: {available_count}")
    print(f"  ✗ 不可用: {unavailable_count}")
    print(f"  ⚠ 加载中: {loading_count}")
    print("=" * 80)
    
    if available_count == 0:
        print("\n⚠ 警告: 所有Hugging Face API都不可用，将使用本地分析")
    else:
        print(f"\n✓ 有 {available_count} 个API可用")

if __name__ == '__main__':
    main()
