@echo off
chcp 65001 >nul
echo ========================================
echo ANG文件欧拉角处理工具 - 运行程序
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo [错误] 虚拟环境不存在！
    echo 请先运行 setup_env.bat 或 setup_and_run.bat 来设置环境
    pause
    exit /b 1
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo.
echo 启动程序...
echo ========================================
echo.
python ang_processor.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause

