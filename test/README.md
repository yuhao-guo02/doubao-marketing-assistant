# 豆包AI营销助手

一个基于豆包大模型的智能营销文案和图片生成工具。

## 功能特点

- 🎯 **智能文案生成**：使用豆包大模型生成产品营销文案
- 🖼️ **AI图片生成**：使用豆包文生图模型生成产品展示图片
- 🌐 **Web界面**：现代化的响应式Web界面
- 📱 **移动端适配**：支持手机和平板访问

## 部署方法

### 方法1：使用 Render（推荐）

1. **注册Render账户**
   - 访问 https://render.com
   - 使用GitHub账户注册

2. **连接GitHub仓库**
   - 将代码推送到GitHub仓库
   - 在Render中连接该仓库

3. **创建Web Service**
   - 选择"New Web Service"
   - 选择你的GitHub仓库
   - 设置以下配置：
     - **Name**: doubao-marketing-assistant
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

4. **设置环境变量**
   - 在Render的Environment Variables中添加：
     - `DOUBAO_API_KEY`: 你的豆包API密钥

5. **部署**
   - 点击"Create Web Service"
   - 等待部署完成

### 方法2：使用 Railway

1. **注册Railway账户**
   - 访问 https://railway.app
   - 使用GitHub账户注册

2. **部署项目**
   - 点击"New Project"
   - 选择"Deploy from GitHub repo"
   - 选择你的仓库

3. **设置环境变量**
   - 在Variables标签页添加：
     - `DOUBAO_API_KEY`: 你的豆包API密钥

### 方法3：使用 Heroku

1. **注册Heroku账户**
   - 访问 https://heroku.com
   - 注册账户

2. **安装Heroku CLI**
   ```bash
   # Windows
   # 下载并安装 Heroku CLI
   ```

3. **部署**
   ```bash
   heroku login
   heroku create your-app-name
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

4. **设置环境变量**
   ```bash
   heroku config:set DOUBAO_API_KEY=your_api_key
   ```

## 本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **设置环境变量**
   ```bash
   # Windows
   set DOUBAO_API_KEY=your_api_key
   
   # Linux/Mac
   export DOUBAO_API_KEY=your_api_key
   ```

3. **运行应用**
   ```bash
   python app.py
   ```

4. **访问应用**
   - 打开浏览器访问 http://localhost:5000

## 项目结构

```
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖
├── Procfile              # 部署配置文件
├── runtime.txt           # Python版本配置
├── templates/
│   └── index.html        # 主页模板
└── static/
    └── generated/        # 生成的图片存储目录
```

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5, CSS3, JavaScript, Bootstrap
- **AI模型**: 豆包大模型 (doubao-seed-1-6-250615)
- **图像生成**: 豆包文生图 (doubao-seedream-3-0-t2i-250415)

## 注意事项

1. **API密钥安全**: 请妥善保管你的豆包API密钥，不要泄露
2. **使用限制**: 注意豆包API的使用限制和计费规则
3. **图片存储**: 生成的图片会保存在服务器上，定期清理
4. **性能优化**: 生产环境建议使用CDN和缓存

## 许可证

MIT License 