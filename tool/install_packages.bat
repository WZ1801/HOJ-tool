echo install packages
pause 
cls

pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

echo Upgrading pip...
 
python -m pip install --upgrade pip 
 
echo Installing required Python packages...
 
pip install selenium
pip install requests
pip install pyperclip
pip install hashlib
pip install colorama
pip install dotenv

cls
echo All packages installed successfully.
pause 