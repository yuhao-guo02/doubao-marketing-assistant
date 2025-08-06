#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包AI本地部署应用
集成豆包大模型实现文生图和文生文功能
支持多种渠道类型：海报大图、banner、信息流
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
from datetime import datetime
import json
import pandas as pd
from io import BytesIO

from werkzeug.utils import secure_filename

app = Flask(__name__)

# 豆包API配置
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY', '32e8fa73-48b0-47d9-a593-f2920340862f')  # 从环境变量读取API Key
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 调试信息
print(f"API Key: {DOUBAO_API_KEY[:10]}...")
print(f"Base URL: {DOUBAO_BASE_URL}")

def generate_text(prompt, max_tokens=500):
    """
    使用豆包大模型生成文本
    """
    try:
        print(f"开始生成文本，提示词: {prompt[:50]}...")
        
        headers = {
            'Authorization': f'Bearer {DOUBAO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'doubao-seed-1-6-250615',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        }
        
        response = requests.post(
            f'{DOUBAO_BASE_URL}/chat/completions',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("文本生成成功")
            return {
                'success': True,
                'content': content
            }
        else:
            print(f"API返回错误状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return {
                'success': False,
                'error': f"API错误: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        print(f"文本生成失败: {e}")
        return {
            'success': False,
            'error': f"文本生成失败: {str(e)}"
        }

def generate_image(prompt, size="1024x1024"):
    """
    使用豆包文生图模型生成图片
    """
    try:
        print(f"开始生成图片，提示词: {prompt[:50]}...")
        
        headers = {
            'Authorization': f'Bearer {DOUBAO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'doubao-seedream-3-0-t2i-250415',
            'prompt': prompt,
            'response_format': 'url',
            'size': size
        }
        
        response = requests.post(
            f'{DOUBAO_BASE_URL}/images/generations',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                
                # 下载并保存图片
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"generated_image_{timestamp}.png"
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
                    return {
                        'success': False,
                        'error': f"图片下载失败: {img_response.status_code}"
                    }
            else:
                return {
                    'success': False,
                    'error': "API返回的数据格式不正确"
                }
        else:
            print(f"图片生成API返回错误状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return {
                'success': False,
                'error': f"图片生成API错误: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        print(f"图片生成失败: {e}")
        return {
            'success': False,
            'error': f"图片生成失败: {str(e)}"
        }

def get_channel_prompts(product_info, channel_type):
    """
    根据渠道类型获取对应的提示词
    """
    product_name = product_info.get('name', '产品')
    product_category = product_info.get('category', '商品')
    product_features = product_info.get('features', '')
    target_audience = product_info.get('target_audience', '')
    # 修复价格字段映射：前端传递的是 'price'，不是 'price_range'
    price_info = product_info.get('price', '')
    additional_info = product_info.get('additional_info', '')
    
    if channel_type == 'poster':
        # 海报大图提示词
        image_prompt = f"""请生成一张竖版海报图片，需完整呈现以下产品信息：{product_name}、（{product_features}）、价格（{price_info}）。图片风格需贴合 {product_category} 的行业特性，色彩搭配鲜明且主次分明，文字布局清晰易读，重点信息（价格）需用加粗/亮色突出，可适当添加场景化元素。"""
        
        return {
            'image_prompt': image_prompt,
            'size': '700x1200',
            'text_prompt': None  # 海报不需要单独生成文案
        }
    
    elif channel_type == 'banner':
        # Banner提示词
        image_prompt = f"""请生成一张横版图片，画面以 {product_name} 为视觉焦点。图片中的文案需极度精简，仅保留价格（{price_info}）、行动指令（如 "立即抢购"）。文字字体需醒目但不遮挡画面主体。整体风格色彩明快，避免信息堆砌感。"""
        
        return {
            'image_prompt': image_prompt,
            'size': '1200x400',
            'text_prompt': None  # Banner不需要单独生成文案
        }
    
    elif channel_type == 'feed':
        # 信息流提示词
        image_prompt = f"""请生成一张图片，图片中不包含任何文字，画面以 {product_name}为主，风格简约大气，背景可适当添加场景化元素，整体保证主体卖点{product_features}突出但又不单调。"""
        
        text_prompt = f"""请为 {product_name} 生成一段配套文案（不超过 30 字），需包含产品名称和 1 个核心卖点（如 "{product_name}，{product_features}"），语言口语化、无修饰，适合在美团信息流中自然展示，给人轻松种草的感觉。"""
        
        return {
            'image_prompt': image_prompt,
            'size': '600x600',  # 修改为正方形尺寸以满足最小512像素要求
            'text_prompt': text_prompt
        }
    
    else:
        # 默认提示词
        image_prompt = f"高质量产品展示图，{product_name}，{product_category}，{product_features}，专业摄影风格，明亮光线，白色背景，产品细节清晰，适合电商展示，4K超高清"
        
        return {
            'image_prompt': image_prompt,
            'size': '1024x1024',
            'text_prompt': None
        }

def analyze_user_behavior_data(df):
    """
    分析用户行为数据，计算每日指标
    """
    try:
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期分组计算指标
        daily_stats = df.groupby('date').agg({
            'user_id': 'nunique',  # 每日访问用户数（PV）
            'click': 'sum',        # 每日点击量
            'purchase': 'sum',     # 每日购买量
            'price': 'first',      # 每日价格（取第一个，因为日内价格相同）
            'is_promotion': 'first'  # 每日促销标识（取第一个，因为日内促销状态相同）
        }).reset_index()
        
        # 重命名列
        daily_stats.columns = ['date', 'pv', 'clicks', 'purchases', 'price', 'is_promotion']
        
        # 计算衍生指标
        daily_stats['click_rate'] = daily_stats['clicks'] / daily_stats['pv']  # 点击率
        daily_stats['conversion_rate'] = daily_stats['purchases'] / daily_stats['clicks']  # 转化率
        daily_stats['gmv'] = daily_stats['purchases'] * daily_stats['price']  # GMV
        
        # 处理除零情况
        daily_stats['click_rate'] = daily_stats['click_rate'].fillna(0)
        daily_stats['conversion_rate'] = daily_stats['conversion_rate'].fillna(0)
        
        return daily_stats
        
    except Exception as e:
        print(f"数据分析失败: {e}")
        return None




@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/generate_text', methods=['POST'])
def generate_text_route():
    """生成文本"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 500)
        
        if not prompt:
            return jsonify({'success': False, 'error': '提示词不能为空'})
        
        result = generate_text(prompt, max_tokens)
        return jsonify(result)
        
    except Exception as e:
        print(f"文本生成过程中发生错误: {e}")
        return jsonify({'success': False, 'error': f"服务器内部错误: {str(e)}"})

@app.route('/generate_marketing', methods=['POST'])
def generate_marketing_route():
    """生成商品营销内容"""
    try:
        data = request.get_json()
        product_info = data.get('product_info', {})
        channel_type = data.get('channel_type', 'default')
        
        if not product_info:
            return jsonify({'success': False, 'error': '商品信息不能为空'})
        
        # 获取对应渠道的提示词
        prompts = get_channel_prompts(product_info, channel_type)
        
        # 生成图片
        image_result = generate_image(prompts['image_prompt'], prompts['size'])
        
        # 如果是信息流，还需要生成配套文案
        text_result = None
        if prompts['text_prompt']:
            text_result = generate_text(prompts['text_prompt'], 100)
        
        return jsonify({
            'success': True,
            'text': text_result,
            'image': image_result,
            'channel_type': channel_type
        })
        
    except Exception as e:
        print(f"营销内容生成过程中发生错误: {e}")
        return jsonify({'success': False, 'error': f"服务器内部错误: {str(e)}"})



@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    """生成图片"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        size = data.get('size', '1024x1024')
        
        if not prompt:
            return jsonify({'success': False, 'error': '提示词不能为空'})
        
        result = generate_image(prompt, size)
        return jsonify(result)
        
    except Exception as e:
        print(f"图片生成过程中发生错误: {e}")
        return jsonify({'success': False, 'error': f"服务器内部错误: {str(e)}"})

@app.route('/download/<filename>')
def download_image(filename):
    """下载生成的图片"""
    try:
        filepath = os.path.join('static', 'generated', filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/analyze_data', methods=['POST'])
def analyze_data_route():
    """分析用户行为数据"""
    try:
        # 检查是否有文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': '请选择文件'})
            
            # 读取Excel文件
            df = pd.read_excel(file)
        else:
            # 使用样例数据
            sample_file = os.path.join(os.path.dirname(__file__), 'user_behavior_data.xlsx')
            if not os.path.exists(sample_file):
                return jsonify({'success': False, 'error': '样例数据文件不存在'})
            df = pd.read_excel(sample_file)
        
        # 验证数据格式
        required_columns = ['user_id', 'date', 'price', 'click', 'purchase']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'success': False, 'error': '数据格式不正确，需要包含：user_id, date, price, click, purchase'})
        
        # 检查是否有促销列，如果没有则添加默认值
        if 'is_promotion' not in df.columns:
            df['is_promotion'] = 0
        
        # 分析数据
        daily_stats = analyze_user_behavior_data(df)
        if daily_stats is None:
            return jsonify({'success': False, 'error': '数据分析失败'})
        
        # 计算总体统计
        total_stats = {
            'total_pv': int(daily_stats['pv'].sum()),
            'total_clicks': int(daily_stats['clicks'].sum()),
            'total_purchases': int(daily_stats['purchases'].sum()),
            'avg_click_rate': float(daily_stats['click_rate'].mean()),
            'avg_conversion_rate': float(daily_stats['conversion_rate'].mean()),
            'total_gmv': float(daily_stats['gmv'].sum()),
            'date_range': f"{daily_stats['date'].min().strftime('%Y-%m-%d')} 到 {daily_stats['date'].max().strftime('%Y-%m-%d')}"
        }
        
        # 转换daily_stats为可序列化的格式
        daily_stats_records = []
        for _, row in daily_stats.iterrows():
            daily_stats_records.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'pv': int(row['pv']),
                'clicks': int(row['clicks']),
                'purchases': int(row['purchases']),
                'price': float(row['price']),
                'click_rate': float(row['click_rate']),
                'conversion_rate': float(row['conversion_rate']),
                'gmv': float(row['gmv']),
                'is_promotion': int(row['is_promotion'])
            })
        
        return jsonify({
            'success': True,
            'daily_stats': daily_stats_records,
            'total_stats': total_stats
        })
        
    except Exception as e:
        print(f"数据分析过程中发生错误: {e}")
        return jsonify({'success': False, 'error': f"服务器内部错误: {str(e)}"})

@app.route('/download_sample')
def download_sample_data():
    """下载样例数据"""
    try:
        sample_file = os.path.join(os.path.dirname(__file__), 'user_behavior_data.xlsx')
        if not os.path.exists(sample_file):
            return jsonify({'success': False, 'error': '样例数据文件不存在'})
        return send_file(sample_file, as_attachment=True, download_name='sample_data.xlsx')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('static/generated', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 获取端口配置，Railway会自动设置PORT环境变量
    port = int(os.environ.get('PORT', 8080))
    
    print("豆包AI营销助手启动中...")
    print(f"访问地址: http://0.0.0.0:{port}")
    
    # Railway部署时使用0.0.0.0绑定所有网络接口
    app.run(debug=False, host='0.0.0.0', port=port) 