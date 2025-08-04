#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包AI营销助手 - Flask应用
集成豆包大模型生成产品宣传文案和图片
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import base64
import requests
from datetime import datetime
import json

app = Flask(__name__)

# 豆包API配置
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY', '32e8fa73-48b0-47d9-a593-f2920340862f')
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 调试信息
print(f"API Key: {DOUBAO_API_KEY[:10]}...")
print(f"Base URL: {DOUBAO_BASE_URL}")

# 初始化豆包客户端（简化版本）
client = True  # 使用简单的标志，因为我们现在直接使用requests
print("豆包客户端初始化成功")

def generate_marketing_copy(product_info):
    """
    使用豆包大模型生成营销文案
    """
    if client is None:
        return {
            'success': False,
            'error': '豆包客户端未初始化'
        }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试生成文案，第 {attempt + 1} 次...")
            
            # 构建提示词
            prompt = f"""
            请为以下产品生成吸引人的营销文案，包括：
            1. 产品标题（简洁有力）
            2. 产品描述（突出卖点）
            3. 营销口号（朗朗上口）
            4. 购买理由（3-5个要点）
            
            产品信息：
            - 产品名称：{product_info.get('name', '')}
            - 产品类型：{product_info.get('type', '')}
            - 主要功能：{product_info.get('features', '')}
            - 目标用户：{product_info.get('target_audience', '')}
            - 价格区间：{product_info.get('price_range', '')}
            
            请用中文回答，格式要清晰易读。
            """
            
            # 使用更稳定的请求方式
            import requests
            import json
            
            headers = {
                'Authorization': f'Bearer {DOUBAO_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'doubao-seed-1-6-250615',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                f'{DOUBAO_BASE_URL}/chat/completions',
                headers=headers,
                json=data,
                timeout=60,
                verify=True  # 确保SSL验证
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print("文案生成成功")
                return {
                    'success': True,
                    'content': content
                }
            else:
                print(f"API返回错误状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                raise Exception(f"API错误: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt == max_retries - 1:  # 最后一次尝试
                return {
                    'success': False,
                    'error': f"重试{max_retries}次后仍然失败: {str(e)}"
                }
            import time
            time.sleep(3)  # 增加等待时间到3秒

def generate_product_image(product_info):
    """
    使用豆包文生图模型生成产品图片
    """
    if client is None:
        return {
            'success': False,
            'error': '豆包客户端未初始化'
        }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试生成图片，第 {attempt + 1} 次...")
            
            # 构建图片生成提示词
            image_prompt = f"""
            高质量产品展示图，{product_info.get('name', '产品')}，
            {product_info.get('type', '')}，{product_info.get('features', '')}，
            专业摄影风格，明亮光线，白色背景，产品细节清晰，
            适合电商展示，4K超高清
            """
            
            # 使用更稳定的请求方式
            import requests
            import json
            
            headers = {
                'Authorization': f'Bearer {DOUBAO_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'doubao-seedream-3-0-t2i-250415',
                'prompt': image_prompt,
                'response_format': 'url',
                'size': '1024x1024'
            }
            
            response = requests.post(
                f'{DOUBAO_BASE_URL}/images/generations',
                headers=headers,
                json=data,
                timeout=60,
                verify=True
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and len(result['data']) > 0:
                    image_url = result['data'][0]['url']
                    
                    # 下载并保存图片
                    img_response = requests.get(image_url, timeout=60)
                    if img_response.status_code == 200:
                        # 生成文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"product_image_{timestamp}.png"
                        filepath = os.path.join('static', 'generated', filename)
                        
                        # 确保目录存在
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        
                        # 保存图片
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        print("图片生成成功")
                        return {
                            'success': True,
                            'image_path': f'/static/generated/{filename}',
                            'filename': filename
                        }
                else:
                    raise Exception("API返回的数据格式不正确")
            else:
                print(f"图片生成API返回错误状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                raise Exception(f"图片生成API错误: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt == max_retries - 1:  # 最后一次尝试
                return {
                    'success': False,
                    'error': f"重试{max_retries}次后仍然失败: {str(e)}"
                }
            import time
            time.sleep(3)  # 增加等待时间到3秒

@app.route('/')
def index():
    """主页"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"主页错误: {e}")
        return f"Error: {str(e)}", 500

@app.route('/generate', methods=['POST'])
def generate():
    """生成营销文案和图片"""
    try:
        print("收到生成请求...")
        
        # 获取产品信息
        product_info = {
            'name': request.form.get('product_name', ''),
            'type': request.form.get('product_type', ''),
            'features': request.form.get('product_features', ''),
            'target_audience': request.form.get('target_audience', ''),
            'price_range': request.form.get('price_range', '')
        }
        
        print(f"产品信息: {product_info}")
        
        # 检查必填字段
        if not product_info['name']:
            return jsonify({'success': False, 'error': '产品名称不能为空'})
        
        # 检查客户端是否可用
        if client is None:
            return jsonify({'success': False, 'error': '豆包客户端未初始化，请检查API配置'})
        
        # 生成营销文案
        print("开始生成营销文案...")
        copy_result = generate_marketing_copy(product_info)
        print(f"文案生成结果: {copy_result}")
        
        # 生成产品图片
        print("开始生成产品图片...")
        image_result = generate_product_image(product_info)
        print(f"图片生成结果: {image_result}")
        
        # 检查是否有成功的结果
        if not copy_result.get('success') and not image_result.get('success'):
            return jsonify({
                'success': False, 
                'error': f"文案生成失败: {copy_result.get('error', '未知错误')}, 图片生成失败: {image_result.get('error', '未知错误')}"
            })
        
        result = {
            'success': True,
            'copy': copy_result,
            'image': image_result
        }
        
        print(f"返回结果: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"生成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify({'success': False, 'error': f"服务器内部错误: {str(e)}"})

@app.route('/download/<filename>')
def download_image(filename):
    """下载生成的图片"""
    try:
        filepath = os.path.join('static', 'generated', filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('static/generated', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 获取端口（生产环境会提供PORT环境变量）
    port = int(os.environ.get('PORT', 5000))
    
    # 生产环境关闭调试模式
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 