# 快速配置Qwen API

## 最简单的方法：使用Hugging Face Token（推荐）

### 步骤1：获取Token（2分钟）

1. 访问：https://huggingface.co/
2. 注册/登录账号
3. 访问：https://huggingface.co/settings/tokens
4. 点击 "New token"
5. 输入名称（如：voc-analysis）
6. 选择权限：**Read**
7. 点击 "Generate token"
8. 复制token（格式：`hf_xxxxxxxxxxxxxxxxxxxxx`）

### 步骤2：配置Token（30秒）

编辑文件：`backend/config.py`

```python
HF_API_TOKEN = "hf_你的token在这里"
```

保存文件，重启后端即可！

## 或者：使用通义千问API

### 步骤1：获取API Key（5分钟）

1. 访问：https://www.aliyun.com/ 注册账号
2. 访问：https://dashscope.console.aliyun.com/
3. 开通通义千问服务
4. 在API-KEY管理页面创建API Key
5. 复制API Key

### 步骤2：配置API Key

编辑文件：`backend/config.py`

```python
TONGYI_API_KEY = "sk-你的key在这里"
```

保存文件，重启后端即可！

## 验证配置

重启后端后，查看日志应该显示：
- `[VOC Analyzer] Hugging Face Token已配置` 或
- `[VOC Analyzer] 通义千问API Key已配置`

## 测试

运行测试脚本：
```bash
python3 test_hf_api.py
```

如果看到 `✓ API可用！` 说明配置成功！
