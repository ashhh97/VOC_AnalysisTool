#!/bin/bash

# 推送代码到GitHub的脚本
# 仓库地址: https://github.com/ashhh97/VOC_AnalysisTool.git

set -e

echo "🚀 开始推送代码到GitHub..."

# 检查Git是否可用
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装。请先安装Xcode命令行工具："
    echo "   xcode-select --install"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 初始化Git仓库（如果还没有）
if [ ! -d .git ]; then
    echo "📁 初始化Git仓库..."
    git init
fi

# 检查远程仓库配置
REMOTE_URL="https://github.com/ashhh97/VOC_AnalysisTool.git"
if git remote get-url origin &> /dev/null; then
    CURRENT_URL=$(git remote get-url origin)
    if [ "$CURRENT_URL" != "$REMOTE_URL" ]; then
        echo "🔄 更新远程仓库地址..."
        git remote set-url origin "$REMOTE_URL"
    else
        echo "✅ 远程仓库已配置: $REMOTE_URL"
    fi
else
    echo "🔗 添加远程仓库..."
    git remote add origin "$REMOTE_URL"
fi

# 添加所有文件
echo "📝 添加文件到Git..."
git add .

# 检查是否有未提交的更改
if git diff --staged --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️  没有需要提交的更改"
else
    # 创建提交
    echo "💾 创建提交..."
    git commit -m "Initial commit: VOC分析工具" || git commit -m "Update: VOC分析工具"
fi

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")

# 如果还没有分支，创建main分支
if [ -z "$CURRENT_BRANCH" ]; then
    echo "🌿 创建main分支..."
    git checkout -b main
    CURRENT_BRANCH="main"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
echo "   仓库: $REMOTE_URL"
echo "   分支: $CURRENT_BRANCH"

# 尝试推送到main分支，如果失败则尝试master
if git push -u origin "$CURRENT_BRANCH" 2>&1; then
    echo ""
    echo "✅ 成功！代码已推送到GitHub"
    echo "📋 查看仓库: https://github.com/ashhh97/VOC_AnalysisTool"
else
    echo ""
    echo "⚠️  推送到 $CURRENT_BRANCH 分支失败，尝试推送到 master 分支..."
    git checkout -b master 2>/dev/null || git checkout master 2>/dev/null || true
    git push -u origin master
    echo ""
    echo "✅ 成功！代码已推送到GitHub (master分支)"
    echo "📋 查看仓库: https://github.com/ashhh97/VOC_AnalysisTool"
fi


