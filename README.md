# VOC分析工具 - AI用户研究分析

一个基于AI的用户反馈（VOC - Voice of Customer）分析工具，可以自动分类和分析用户反馈，并将结果展示在在线表格编辑器中。

## 功能特点

- 📊 **Excel文件上传**：支持上传.xlsx和.xls格式的Excel文件
- 🤖 **AI智能分析**：自动识别用户反馈的情感（正面/负面）和分类
- 📝 **在线编辑**：集成Luckysheet在线表格编辑器，支持实时编辑
- 🔄 **智能分类**：将同类问题的用户声音归为一类
- 📋 **多Sheet支持**：保留原始数据，在新建Sheet中展示分析结果
- 🎨 **合并单元格**：自动为同类问题添加分类标题和情感标签

## 技术栈

### 前端
- React 18
- Vite
- Luckysheet（在线表格编辑器）

### 后端
- Python Flask
- openpyxl（Excel处理）
- Hugging Face API（AI分析，免费）

## 本地部署（从零起步）

以下步骤面向第一次接触开源项目的小白，从注册 GitHub 到跑通前后端。

### 0. 准备环境
- 操作系统：macOS / Windows / Linux 均可
- 需要安装：
  - Git：https://git-scm.com/downloads
  - Node.js（含 npm）：建议 LTS 版本，https://nodejs.org/
  - Python 3.9+：https://www.python.org/downloads/
  - 可选：VS Code / Cursor 作为编辑器

### 1. 注册并获取代码
1) 注册/登录 GitHub：https://github.com  
2) 打开项目地址，复制仓库 HTTPS URL（形如 `https://github.com/xxx/voc-analysis-tool.git`）。  
3) 打开终端，选择一个存放代码的目录并克隆：
```bash
cd /path/to/your/workspace
git clone https://github.com/xxx/voc-analysis-tool.git
cd voc-analysis-tool
```

### 2. 前端依赖安装
在仓库根目录执行：
```bash
npm install
```

### 3. 后端依赖安装
建议使用虚拟环境，避免污染系统 Python。
```bash
cd backend
python -m venv .venv          # 创建虚拟环境（可选但推荐）
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
```

### 4.（可选）配置 AI Key
工具默认会优先尝试免费的 Hugging Face 接口，无 Key 也能跑。若你有 Key，可在 `backend/config.example.py` 复制为 `config.py` 并填入：
```python
HF_API_TOKEN = "your_hf_token"
TONGYI_API_KEY = "your_tongyi_key"  # 可选
```
环境变量方式也支持：`export HF_API_TOKEN=xxx`。

### 5. 启动后端
```bash
cd backend
source .venv/bin/activate  # 若使用虚拟环境
python app.py
```
默认监听 http://localhost:5000

### 6. 启动前端
另开一个终端窗口，回到项目根目录：
```bash
npm run dev
```
按提示在浏览器打开（通常是 http://localhost:5173 或 3000）。

### 7. 使用
1) 打开前端地址  
2) 上传 Excel（.xlsx/.xls）  
3) 点击「开始AI分析」  
4) 结果会在「分析结果」sheet 中按分类/情绪分组显示，并支持手动编辑  

### 8. 常见问题
- 端口被占用：修改前端 `vite.config.js` 或后端 `app.py` 的端口，或关闭占用进程。  
- 依赖安装慢：使用国内镜像（如 `npm config set registry https://registry.npmmirror.com`；`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`）。  
- AI 调用失败：未配置 Key 时会自动回落到规则分析；如需更高质量，请配置有效的 HF/Tongyi Key。  

### 9. 目录结构速览
```
voc-analysis-tool/
├── src/                    # 前端代码（Vite + React）
├── backend/                # 后端 Flask 与分析逻辑
├── public/                 # 前端静态资源
├── package.json            # 前端依赖
├── backend/requirements.txt# 后端依赖
└── README.md               # 文档
```

## 使用方法

1. 打开浏览器访问 http://localhost:3000
2. 点击上传区域或拖拽Excel文件上传
3. 上传成功后，表格将在在线编辑器中显示
4. 点击"开始AI分析"按钮，系统将：
   - 分析用户反馈内容
   - 识别情感（正面/负面）
   - 按问题类型分类
   - 在新建的Sheet中展示分析结果，同类问题归为一类，并添加分类标题和情感标签

## Excel文件格式要求

Excel文件应包含用户反馈数据，建议格式：
- 第一行为表头
- 包含用户反馈内容的列（系统会自动识别包含"反馈"、"意见"、"评论"等关键词的列）
- 支持多个Sheet

## AI分析说明

系统支持多种 AI API，按配置的优先级依次尝试：

1. **通义千问 API**（阿里云 DashScope）
   - 默认模型：`qwen-flash-2025-07-28`
   - 需要在 `backend/config.py` 中配置 `TONGYI_API_KEY`
   - 使用阿里云免费额度，用完即停
   - 获取方式：https://dashscope.console.aliyun.com/

2. **Hugging Face API**
   - 模型：`Qwen2.5-7B-Instruct`、`Qwen2-7B-Instruct` 等
   - 支持 Token 认证（配置 `HF_API_TOKEN`）或免费接口（无需 Token，但可能不稳定）
   - 免费接口有速率限制，用完即停
   - Token 获取方式：https://huggingface.co/settings/tokens

3. **本地规则分析**（备用方案）
   - 当所有 API 都不可用或额度耗尽时，自动切换到基于关键词规则的本地分析
   - 准确度较低，但无需网络和 API 配置

**支持的功能：**
- 情感识别：正面、负面、中性
- 问题分类：功能问题、性能问题、界面问题、体验问题、服务问题、价格问题、其他问题

## 项目结构

```
voc-analysis-tool/
├── src/                    # 前端源代码
│   ├── components/         # React组件
│   ├── App.jsx            # 主应用组件
│   └── main.jsx           # 入口文件
├── backend/               # 后端源代码
│   ├── app.py             # Flask应用
│   ├── voc_analyzer.py    # VOC分析器
│   └── requirements.txt   # Python依赖
├── uploads/              # 上传文件存储目录（自动创建）
├── package.json          # 前端依赖配置
└── vite.config.js        # Vite配置
```

## 注意事项

- 上传的文件会保存在`backend/uploads/`目录中
- 如果Hugging Face API不可用，系统会自动使用本地规则分析
- 建议使用Chrome或Edge浏览器以获得最佳体验

## 许可证

MIT License

