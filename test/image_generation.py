#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包文生图模型调用示例
使用 Doubao-Seedream-3.0-t2i 模型生成图片
基于官方文档：https://www.volcengine.com/docs/82379/1541523
"""

import os
from openai import OpenAI
from datetime import datetime
import requests

def generate_image_with_doubao():
    """
    使用豆包文生图模型生成图片
    """
    try:
        # 初始化OpenAI客户端，使用官方推荐的方式
        client = OpenAI(
            # 此为默认路径，您可根据业务所在地域进行配置
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            # 直接使用API Key
            api_key='32e8fa73-48b0-47d9-a593-f2920340862f',
        )
        
        print("正在调用豆包文生图模型...")
        print("提示词: 一只可爱的小猫坐在花园里，阳光明媚，背景是美丽的花朵")
        
        # 使用官方推荐的方式调用图像生成API
        resp = client.images.generate(
            prompt="一只可爱的小猫坐在花园里，阳光明媚，背景是美丽的花朵",
            model="doubao-seedream-3-0-t2i-250415",  # 使用官方模型名称
            response_format="url",
            size="1024x1024",
        )
        
        print("✅ 图片生成成功!")
        print(f"响应: {resp}")
        
        # 保存图片
        if hasattr(resp, 'data') and len(resp.data) > 0:
            image_url = resp.data[0].url
            save_image_from_url(image_url)
        else:
            print("❌ 响应中没有找到图片数据")
            
    except Exception as e:
        print(f"❌ 调用豆包文生图API时发生错误: {e}")

def save_image_from_url(image_url):
    """
    从URL下载并保存图片
    """
    try:
        print(f"正在下载图片: {image_url}")
        response = requests.get(image_url, timeout=30)
        
        if response.status_code == 200:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"doubao_generated_{timestamp}.png"
            
            # 保存图片
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 图片已保存为: {filename}")
            print(f"文件大小: {len(response.content)} 字节")
        else:
            print(f"❌ 下载图片失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 保存图片时发生错误: {e}")

def save_base64_image(base64_data):
    """
    保存base64编码的图片
    """
    try:
        # 解码base64数据
        image_data = base64.b64decode(base64_data)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"doubao_generated_{timestamp}.png"
        
        # 保存图片
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ 图片已保存为: {filename}")
        print(f"文件大小: {len(image_data)} 字节")
        
    except Exception as e:
        print(f"❌ 保存base64图片时发生错误: {e}")

def main():
    """
    主函数
    """
    print("🚀 开始调用豆包文生图模型...")
    print("=" * 50)
    
    generate_image_with_doubao()
    
    print("=" * 50)
    print("程序执行完成!")

if __name__ == "__main__":
    main() 