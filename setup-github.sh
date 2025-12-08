#!/bin/bash

# VOC分析工具 - GitHub仓库设置脚本
# 使用方法：在终端运行 ./setup-github.sh

set -e

echo "🚀 开始设置GitHub仓库..."

# 检查Git是否可用
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装。请先完成Xcode命令行工具的安装。"
    echo "   如果安装对话框已关闭，请运行: xcode-select --install"
    exit 1
fi

# 检查GitHub CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "📦 GitHub CLI未安装，正在安装..."
    
    # 检查是否有Homebrew
    if ! command -v brew &> /dev/null; then
        echo "📦 正在安装Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # 添加Homebrew到PATH（Apple Silicon Mac）
        if [ -f /opt/homebrew/bin/brew ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi
    
    echo "📦 使用Homebrew安装GitHub CLI..."
    brew install gh
fi

# 检查GitHub CLI是否已登录
if ! gh auth status &> /dev/null; then
    echo "🔐 需要登录GitHub，请按照提示操作..."
    gh auth login
fi

# 初始化Git仓库（如果还没有）
if [ ! -d .git ]; then
    echo "📁 初始化Git仓库..."
    git init
fi

# 添加所有文件
echo "📝 添加文件到Git..."
git add .

# 检查是否有未提交的更改
if git diff --staged --quiet; then
    echo "ℹ️  没有需要提交的更改"
else
    # 创建初始提交
    echo "💾 创建初始提交..."
    git commit -m "Initial commit: VOC分析工具"
fi

# 获取仓库名称（使用当前目录名）
REPO_NAME=$(basename "$(pwd)")

# 检查是否已有远程仓库
if git remote get-url origin &> /dev/null; then
    echo "ℹ️  已存在远程仓库配置"
    REMOTE_URL=$(git remote get-url origin)
    echo "   当前远程仓库: $REMOTE_URL"
    read -p "是否要推送到现有仓库? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 推送到GitHub..."
        git push -u origin main || git push -u origin master
        echo "✅ 完成！代码已推送到GitHub"
        exit 0
    fi
fi

# 创建GitHub仓库
echo "🌐 在GitHub上创建仓库: $REPO_NAME"
read -p "仓库描述 (可选，直接回车跳过): " REPO_DESCRIPTION
read -p "是否设为私有仓库? (y/n，默认公开): " -n 1 -r
echo

PRIVATE_FLAG=""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PRIVATE_FLAG="--private"
else
    PRIVATE_FLAG="--public"
fi

# 创建仓库
if [ -z "$REPO_DESCRIPTION" ]; then
    gh repo create "$REPO_NAME" $PRIVATE_FLAG --source=. --remote=origin --push
else
    gh repo create "$REPO_NAME" $PRIVATE_FLAG --description "$REPO_DESCRIPTION" --source=. --remote=origin --push
fi

echo "✅ 完成！"
echo "📋 仓库地址: $(gh repo view --web)"
echo ""
echo "🎉 您的代码已成功推送到GitHub！"

