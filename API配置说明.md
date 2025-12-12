# Qwen API 配置说明

本工具支持多种Qwen API配置方式，按优先级自动尝试。

## 配置方式

### 方式1：使用配置文件（推荐）

1. 编辑 `backend/config.py` 文件
2. 填入您的API密钥
3. 设置API优先级

### 方式2：使用环境变量

```bash
export HF_API_TOKEN="your_huggingface_token"
export TONGYI_API_KEY="your_tongyi_key"
```

## API选项

### 1. Hugging Face API Token（推荐）

**优点：**
- 免费额度充足
- 支持多个Qwen模型
- 响应速度快

**获取步骤：**
1. 访问 https://huggingface.co/ 注册账号
2. 登录后访问 https://huggingface.co/settings/tokens
3. 点击 "New token"
4. 选择权限：**Read**（读取权限即可）
5. 复制生成的token（格式：`hf_xxxxxxxxxxxxxxxxxxxxx`）

**配置方法：**
在 `backend/config.py` 中设置：
```python
HF_API_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxx"
```

**支持的模型：**
- Qwen2.5-7B-Instruct
- Qwen2-7B-Instruct
- Qwen2-1.5B-Instruct
- Qwen2.5-14B-Instruct

### 2. 通义千问API（阿里云）

**优点：**
- 官方Qwen API
- 免费额度：每月100万tokens
- 响应稳定

**获取步骤：**
1. 访问 https://www.aliyun.com/ 注册阿里云账号
2. 访问 https://dashscope.console.aliyun.com/
3. 开通通义千问服务
4. 在API-KEY管理页面创建API Key
5. 复制API Key（格式：`sk-xxxxxxxxxxxxxxxxxxxxx`）

**配置方法：**
在 `backend/config.py` 中设置：
```python
TONGYI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxx"
```

**支持的模型：**
- qwen-turbo（快速，推荐）
- qwen-plus（平衡）
- qwen-max（最强）

### 3. Hugging Face 免费API（无需Token）

**状态：** 目前大部分模型返回410错误，不可用

**说明：** 如果配置了Token，会自动尝试免费API作为备用

### 4. 本地分析（备用）

**说明：** 如果所有API都不可用，自动使用基于关键词的本地分析

## API优先级配置

在 `backend/config.py` 中可以设置API优先级：

```python
API_PRIORITY = ["hf_token", "tongyi", "hf_free", "local"]
```

优先级说明：
- `hf_token`: Hugging Face API Token（如果已配置）
- `tongyi`: 通义千问API（如果已配置）
- `hf_free`: Hugging Face免费API
- `local`: 本地关键词分析

系统会按顺序尝试，直到找到可用的API。

## 测试API配置

运行测试脚本检查API是否可用：

```bash
python3 test_hf_api.py  # 测试Hugging Face API
```

## 常见问题

### Q: 如何知道当前使用的是哪个API？

A: 查看后端日志，会显示：
- `[HF Token API]` - 使用Hugging Face Token
- `[通义千问API]` - 使用通义千问
- `[HF Free API]` - 使用Hugging Face免费API
- `[本地分析]` - 使用本地关键词分析

### Q: API调用失败怎么办？

A: 系统会自动尝试下一个API，如果都失败，会使用本地分析。

### Q: 如何只使用某个特定的API？

A: 在 `config.py` 中设置 `API_PRIORITY`，只包含您想要的API类型。

例如，只使用通义千问：
```python
API_PRIORITY = ["tongyi", "local"]
```

### Q: Hugging Face Token需要什么权限？

A: 只需要 **Read** 权限即可，不需要Write权限。

## 推荐配置

**最佳配置（推荐）：**
```python
HF_API_TOKEN = "your_token"  # 主要使用
TONGYI_API_KEY = "your_key"  # 备用
API_PRIORITY = ["hf_token", "tongyi", "local"]
```

**仅使用通义千问：**
```python
TONGYI_API_KEY = "your_key"
API_PRIORITY = ["tongyi", "local"]
```

**仅使用Hugging Face：**
```python
HF_API_TOKEN = "your_token"
API_PRIORITY = ["hf_token", "local"]
```
