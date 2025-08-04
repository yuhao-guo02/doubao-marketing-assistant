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
from openai import OpenAI
import json

app = Flask(__name__)

# 豆包API配置
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY', '32e8fa73-48b0-47d9-a593-f2920340862f')
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 初始化豆包客户端
client = OpenAI(
    base_url=DOUBAO_BASE_URL,
    api_key=DOUBAO_API_KEY,
)

def generate_marketing_copy(product_info):
    """
    使用豆包大模型生成营销文案
    """
    try:
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
        
        response = client.chat.completions.create(
            model="doubao-seed-1-6-250615",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return {
            'success': True,
            'content': response.choices[0].message.content
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_product_image(product_info):
    """
    使用豆包文生图模型生成产品图片
    """
    try:
        # 构建图片生成提示词
        image_prompt = f"""
        高质量产品展示图，{product_info.get('name', '产品')}，
        {product_info.get('type', '')}，{product_info.get('features', '')}，
        专业摄影风格，明亮光线，白色背景，产品细节清晰，
        适合电商展示，4K超高清
        """
        
        # 调用文生图API
        resp = client.images.generate(
            prompt=image_prompt,
            model="doubao-seedream-3-0-t2i-250415",
            response_format="url",
            size="1024x1024",
        )
        
        if hasattr(resp, 'data') and len(resp.data) > 0:
            image_url = resp.data[0].url
            
            # 下载并保存图片
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"product_image_{timestamp}.png"
                filepath = os.path.join('static', 'generated', filename)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # 保存图片
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return {
                    'success': True,
                    'image_path': f'/static/generated/{filename}',
                    'filename': filename
                }
        
        return {
            'success': False,
            'error': '图片生成失败'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

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
        
        # 生成营销文案
        print("开始生成营销文案...")
        copy_result = generate_marketing_copy(product_info)
        print(f"文案生成结果: {copy_result}")
        
        # 生成产品图片
        print("开始生成产品图片...")
        image_result = generate_product_image(product_info)
        print(f"图片生成结果: {image_result}")
        
        result = {
            'success': True,
            'copy': copy_result,
            'image': image_result
        }
        
        print(f"返回结果: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"生成过程中发生错误: {e}")
        return jsonify({'success': False, 'error': str(e)})

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