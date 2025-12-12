# 配置通义千问API详细步骤

## 步骤1：注册阿里云账号并开通服务（约5分钟）

1. **访问阿里云官网**
   - 打开：https://www.aliyun.com/
   - 如果没有账号，点击"免费注册"
   - 如果有账号，直接登录

2. **进入通义千问控制台**
   - 访问：https://dashscope.console.aliyun.com/
   - 首次使用需要开通服务（通常是免费的）

3. **创建API Key**
   - 在控制台左侧菜单找到"API-KEY管理"
   - 点击"创建新的API Key"
   - 输入名称（如：voc-analysis）
   - 点击"确定"
   - **重要**：复制生成的API Key（格式类似：`sk-xxxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ API Key只显示一次，请立即保存！

## 步骤2：配置API Key（30秒）

1. **打开配置文件**
   ```bash
   # 在项目根目录
   code backend/config.py
   # 或者用任何文本编辑器打开
   ```

2. **填入API Key**
   ```python
   # 通义千问API配置（阿里云）
   TONGYI_API_KEY = "sk-你的API_Key_粘贴在这里"
   ```

3. **设置优先级（可选）**
   如果想优先使用通义千问，可以修改：
   ```python
   API_PRIORITY = ["tongyi", "hf_token", "hf_free", "local"]
   ```

4. **保存文件**

## 步骤3：重启后端服务器

1. **停止当前后端**（如果正在运行）
   - 在终端按 `Ctrl+C`

2. **重新启动后端**
   ```bash
   cd backend
   python3 app.py
   ```

3. **查看日志确认**
   启动后应该看到：
   ```
   [VOC Analyzer] 初始化完成
   [VOC Analyzer] 通义千问API Key已配置
   [VOC Analyzer] API优先级: tongyi, hf_token, hf_free, local
   ```

## 步骤4：测试API是否可用

运行测试脚本：
```bash
python3 test_hf_api.py
```

如果看到：
```
测试: 通义千问API
  ✓ API可用！
```

说明配置成功！

## 常见问题

### Q: 找不到API Key管理页面？
A: 确保已经开通了通义千问服务，可能需要实名认证。

### Q: API Key格式是什么？
A: 通常以 `sk-` 开头，后面是一串字符，例如：`sk-1234567890abcdef`

### Q: 如何查看API使用情况？
A: 在通义千问控制台的"用量统计"页面可以查看。

### Q: 免费额度是多少？
A: 通义千问通常提供每月100万tokens的免费额度，足够日常使用。

### Q: 配置后还是使用本地分析？
A: 检查：
1. API Key是否正确（没有多余空格）
2. 后端是否已重启
3. 查看后端日志是否有错误信息

## 验证配置是否生效

上传文件进行分析时，查看后端日志：
- ✅ 如果看到 `[通义千问API] 调用成功` → 配置成功
- ❌ 如果看到 `[通义千问API] 调用失败` → 检查API Key是否正确
- ❌ 如果看到 `[Qwen API] 使用本地分析` → 检查API Key是否已配置
