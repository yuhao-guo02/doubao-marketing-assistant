# 豆包AI营销内容生成器

基于豆包大模型的智能营销内容生成工具，支持文生图、文生文功能，适用于多种营销渠道。

## 功能特性

- **文生图**: 支持多种尺寸的图片生成
- **文生文**: 智能文案生成
- **营销内容生成**: 针对不同渠道（海报、banner、信息流）的定制化内容
- **数据分析**: 用户行为数据分析功能

## 部署到Railway

### 1. 环境变量配置

在Railway项目设置中添加以下环境变量：

```
DOUBAO_API_KEY=你的豆包API密钥
```

### 2. 部署步骤

1. 将代码推送到GitHub仓库
2. 在Railway中连接GitHub仓库
3. 选择web文件夹作为部署目录
4. 配置环境变量
5. 部署应用

### 3. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DOUBAO_API_KEY=你的豆包API密钥

# 运行应用
python app.py
```

## API接口

### 文本生成
- **POST** `/generate_text`
- 参数: `prompt`, `max_tokens`

### 图片生成
- **POST** `/generate_image`
- 参数: `prompt`, `size`

### 营销内容生成
- **POST** `/generate_marketing`
- 参数: `product_info`, `channel_type`

### 数据分析
- **POST** `/analyze_data`
- 支持文件上传或使用样例数据

## 渠道类型

- `poster`: 海报大图 (700x1200)
- `banner`: Banner横幅 (1200x400)
- `feed`: 信息流 (600x600)

## 技术栈

- Flask: Web框架
- 豆包API: AI模型服务
- Pandas: 数据处理
- Gunicorn: WSGI服务器

## 注意事项

1. 确保豆包API密钥有效且有足够配额
2. 图片生成需要一定时间，请耐心等待
3. 生成的图片会保存在static/generated目录下 