@echo off
title HOJ Tool - 安装依赖

echo 正在安装HOJ Tool所需依赖包...
echo.

pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

echo 正在升级pip...
echo.
python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo 错误：pip升级失败
    pause
    exit /b 1
)

echo.
echo 正在安装所需Python包...
echo.

REM 安装项目所需的所有依赖包
pip install selenium
pip install requests
pip install pyperclip
pip install colorama
pip install python-dotenv
pip install fastapi
pip install uvicorn

if %errorlevel% neq 0 (
    echo 错误：依赖包安装失败
    pause
    exit /b 1
)

echo.
echo 所有依赖包已成功安装！
echo.

REM 检查是否安装了所有必需的包
echo 正在验证安装...
python -c "import selenium, requests, pyperclip, colorama, dotenv, fastapi, uvicorn; print('所有依赖包验证通过')"

if %errorlevel% neq 0 (
    echo 警告：某些依赖包可能未正确安装，请检查上面的错误信息
) else (
    echo 依赖包验证成功
)

echo.
echo 安装完成！现在可以运行HOJ Tool了。
pause