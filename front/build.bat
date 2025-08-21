@echo off
echo 开始构建 LifeTrace Electron 应用...

echo 1. 安装依赖...
call npm install

echo 2. 构建 React 应用...
call npm run build

echo 3. 打包 Electron 应用...
call npm run build-electron

echo 构建完成！应用程序位于 dist-electron 目录中。
pause