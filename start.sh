#!/bin/bash

# 启动脚本

echo "正在启动VOC分析工具..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 创建上传目录
mkdir -p backend/uploads

# 启动后端服务器（后台运行）
echo "启动后端服务器..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 启动前端服务器
echo "启动前端服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "VOC分析工具已启动！"
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="

# 等待用户中断
wait

