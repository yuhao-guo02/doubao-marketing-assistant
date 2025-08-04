#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出可用的豆包模型
"""

import requests

def list_models():
    """
    列出可用的模型
    """
    try:
        # API配置
        base_url = "https://ark.cn-beijing.volces.com/api/v1"
        api_key = '32e8fa73-48b0-47d9-a593-f2920340862f'
        
        # 请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print("正在获取可用模型列表...")
        
        # 发送请求
        response = requests.get(
            f"{base_url}/models",
            headers=headers,
            timeout=30
        )
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("✅ 成功获取模型列表!")
            print("=" * 50)
            
            if 'data' in result:
                for model in result['data']:
                    model_id = model.get('id', 'Unknown')
                    model_type = model.get('object', 'Unknown')
                    print(f"模型ID: {model_id}")
                    print(f"类型: {model_type}")
                    print("-" * 30)
            else:
                print("响应内容:")
                print(result)
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 获取模型列表时发生错误: {e}")

if __name__ == "__main__":
    list_models() 