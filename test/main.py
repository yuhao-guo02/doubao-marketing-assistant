#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包大模型API调用示例
"""

import os
from openai import OpenAI

def main():
    """
    主函数 - 调用豆包大模型API
    """
    try:
        # 初始化豆包客户端
        client = OpenAI(
            # 豆包API的基础URL
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            # API密钥 - 建议使用环境变量存储
            api_key='32e8fa73-48b0-47d9-a593-f2920340862f',
        )

        # 调用豆包大模型
        response = client.chat.completions.create(
            # 豆包模型名称
            model="doubao-seed-1-6-250615",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                            },
                        },
                        {"type": "text", "text": "这是哪里？"},
                    ],
                }
            ],
        )

        # 打印响应结果
        print("豆包大模型响应:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"调用豆包API时发生错误: {e}")

if __name__ == "__main__":
    main()