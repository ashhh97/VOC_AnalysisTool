# 上传代码到 GitHub 仓库步骤

## 您的仓库地址
https://github.com/ashhh97/VOC_AnalysisTool.git

## 方法：通过 GitHub 网页界面上传

### 步骤1：访问您的仓库
打开浏览器，访问：https://github.com/ashhh97/VOC_AnalysisTool

### 步骤2：上传文件
1. 在仓库页面，点击 **"uploading an existing file"** 按钮（如果仓库是空的，这个按钮会很明显）

2. **创建文件夹结构并上传文件**：
   
   **首先创建 backend 文件夹：**
   - 点击 "Add file" → "Create new file"
   - 在文件名输入框中输入：`backend/app.py`
   - 复制 `backend/app.py` 的内容粘贴进去
   - 点击 "Commit new file"
   
   **然后继续添加其他文件：**
   - `backend/requirements.txt`
   - `backend/voc_analyzer.py`
   - `src/App.css`
   - `src/App.jsx`
   - `src/index.css`
   - `src/main.jsx`
   - `src/components/FileUpload.css`
   - `src/components/FileUpload.jsx`
   - `src/components/SpreadsheetEditor.css`
   - `src/components/SpreadsheetEditor.jsx`
   - `.gitignore`
   - `index.html`
   - `package.json`
   - `README.md`
   - `vite.config.js`
   - `start.sh`
   - `使用说明.md`

### 步骤3：批量上传（更简单的方法）

**推荐方法：使用 GitHub Desktop 或直接拖拽**

1. 访问仓库页面
2. 点击 "uploading an existing file"
3. 将整个项目文件夹拖拽到上传区域
4. GitHub 会自动识别文件夹结构

**注意：** 如果拖拽整个文件夹不行，可以：
- 先创建文件夹结构（通过创建新文件时输入路径）
- 然后逐个上传文件

### 快速操作提示

**最简单的方式：**
1. 打开 https://github.com/ashhh97/VOC_AnalysisTool
2. 点击 "uploading an existing file"
3. 打开 Finder，进入 `/Users/SL/Desktop/voc-analysis-tool`
4. 选择所有文件（Command+A），拖拽到浏览器上传区域
5. 输入提交信息："Initial commit"
6. 点击 "Commit changes"

## 需要上传的文件清单

```
✅ backend/app.py
✅ backend/requirements.txt
✅ backend/voc_analyzer.py
✅ src/App.css
✅ src/App.jsx
✅ src/index.css
✅ src/main.jsx
✅ src/components/FileUpload.css
✅ src/components/FileUpload.jsx
✅ src/components/SpreadsheetEditor.css
✅ src/components/SpreadsheetEditor.jsx
✅ .gitignore
✅ index.html
✅ package.json
✅ README.md
✅ vite.config.js
✅ start.sh
✅ 使用说明.md
```

**不需要上传的文件（已在 .gitignore 中）：**
- node_modules/
- dist/
- backend/uploads/
- backend/__pycache__/
- *.pyc
- .env
- .DS_Store


