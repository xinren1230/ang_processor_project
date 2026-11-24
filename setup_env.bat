@echo off
chcp 65001 >nul
echo ========================================
echo ANG文件欧拉角处理工具 - 环境设置
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo [1/4] 检查Python版本...
python --version

echo.
echo [2/4] 创建虚拟环境（如果不存在）...
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
echo [3/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo.
echo [4/4] 升级pip并安装依赖包...
python -m pip install --upgrade pip --quiet
echo 正在安装依赖包（PyQt5, numpy）...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 要运行程序，请执行: run.bat
echo 或者运行: setup_and_run.bat（自动设置并运行）
echo.
pause

