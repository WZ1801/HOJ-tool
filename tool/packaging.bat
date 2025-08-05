@echo off
echo 正在打包HOJ Tool，请稍候...

REM 使用Nuitka打包Python程序
python -m nuitka --standalone ^
    --enable-plugin=numpy ^
    --include-data-dir=static=static ^
    --lto=yes ^
    --main="main.py" ^
    --product-name="HOJ tool" ^
    --product-version="4.0" ^
    --copyright="EchoSearch-MIT" ^
    --windows-icon-from-ico="favicon.ico"

echo 打包完成！
pause