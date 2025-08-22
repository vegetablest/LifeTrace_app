@echo off
echo 启动 LifeTrace 开发模�?..

echo 安装依赖（如果需要）...
call npm install

echo 启动开发服务器�?Electron...
call npm run electron-dev
