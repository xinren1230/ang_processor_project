@echo off
chcp 65001 >nul
echo ========================================
echo ANG文件欧拉角处理工具 - 环境设置和运行
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo [1/5] 检查Python版本...
python --version

echo.
echo [2/5] 创建虚拟环境（如果不存在）...
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
) else (
    echo 虚拟环境已存在，跳过创建步骤
)

echo.
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo.
echo [4/5] 升级pip并安装依赖包...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [警告] pip升级失败，继续安装依赖...
)

echo 正在安装依赖包（PyQt5, numpy）...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo [5/5] 启动程序...
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

