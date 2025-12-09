# GitHub上传说明

## 方法1：网页上传（推荐，无需Git）

### 步骤：

1. **创建GitHub仓库**
   - 访问：https://github.com/new
   - 仓库名称：`voc-analysis-tool`（或您喜欢的名字）
   - 选择 Public 或 Private
   - ⚠️ **不要勾选** "Initialize this repository with a README"
   - 点击 "Create repository"

2. **上传文件**
   - 在新建的仓库页面，点击 "uploading an existing file" 按钮
   - 将以下文件逐个上传（或拖拽上传）：

### 需要上传的文件清单：

```
voc-analysis-tool/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── voc_analyzer.py
├── src/
│   ├── App.css
│   ├── App.jsx
│   ├── components/
│   │   ├── FileUpload.css
│   │   ├── FileUpload.jsx
│   │   ├── SpreadsheetEditor.css
│   │   └── SpreadsheetEditor.jsx
│   ├── index.css
│   └── main.jsx
├── .gitignore
├── index.html
├── package.json
├── README.md
├── vite.config.js
├── start.sh
└── 使用说明.md
```

3. **提交更改**
   - 上传完成后，在页面底部输入提交信息：`Initial commit`
   - 点击 "Commit changes"

## 方法2：使用Git命令行（需要先安装Git）

如果您想使用Git命令行，需要先安装Xcode命令行工具：

```bash
xcode-select --install
```

安装完成后，运行：

```bash
cd /Users/SL/Desktop/voc-analysis-tool
./setup-github.sh
```

## 注意事项

- `.gitignore` 文件已经配置好了，会忽略 `node_modules/`、`dist/` 等不需要上传的文件
- 如果使用网页上传，建议先创建文件夹结构，然后逐个上传文件
- GitHub网页上传支持拖拽多个文件，但需要保持文件夹结构


