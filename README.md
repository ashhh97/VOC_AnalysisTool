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

## 安装和运行

### 1. 安装前端依赖

```bash
cd voc-analysis-tool
npm install
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动后端服务器

```bash
cd backend
python app.py
```

后端服务器将在 http://localhost:5000 运行

### 4. 启动前端开发服务器

```bash
npm run dev
```

前端应用将在 http://localhost:3000 运行

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

系统使用以下方式进行AI分析：
1. 优先使用Hugging Face免费API（无需API key）
2. 如果API不可用，自动切换到基于关键词规则的本地分析
3. 支持的情感识别：正面、负面、中性
4. 支持的问题分类：功能问题、性能问题、界面问题、体验问题、服务问题、价格问题、其他问题

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

