# API配置文件示例
# 复制此文件为 config.py 并填入您的API密钥

# Hugging Face API Token
# 获取方式：https://huggingface.co/settings/tokens
# 注册账号后，在 Settings -> Access Tokens 中创建新token
HF_API_TOKEN = None  # 例如: "hf_xxxxxxxxxxxxxxxxxxxxx"

# 通义千问API配置（阿里云）
# 获取方式：https://dashscope.console.aliyun.com/
# 注册阿里云账号后，在通义千问控制台获取API Key
TONGYI_API_KEY = None  # 例如: "sk-xxxxxxxxxxxxxxxxxxxxx"

# 使用优先级（按顺序尝试）
# 可选值: "hf_token", "tongyi", "hf_free", "local"
API_PRIORITY = ["hf_token", "tongyi", "hf_free", "local"]
