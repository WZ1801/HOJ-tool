# HOJ Tool  

## Project Introduction  

HOJ Tool is an auxiliary tool designed for HOJ-style online judge systems (OJ), providing automated problem-solving and account management features. It supports both command-line and web interface operation modes and is compatible with Windows platforms.  

## Key Features  

1. **Automated Problem-Solving Module**: Uses AI to automatically solve programming problems on OJ platforms.  
   - Supports three modes: practice problems, specified problems, and all problems.  
   - Automatically analyzes problem requirements and generates solution code.  
   - Intelligently submits and verifies results.  

2. **Account Management Module**: Provides account-related management functions.  
   - Supports banning specified accounts.  
   - Supports batch banning (with optional whitelist settings).  

3. **Dual-Mode Interface**:  
   - Command-line console mode: Lightweight operation.  
   - Web GUI mode: Modern web interface based on FastAPI.  

4. **Configuration Management**: Saves user settings for future use.  

## System Requirements  

- Operating System: Windows 7/8/10/11  
- Browser: Google Chrome (recommended), Microsoft Edge, or Firefox  
- Internet Connection: Stable connection required  

## Installation Guide  

### Method 1: Source Code Deployment  

1. Clone the repository locally:  

   ```shell  
   git clone https://gitee.com/wzokee/hoj-tool.git  
   ```  

2. Install a browser (Google Chrome recommended).  

3. Install the corresponding web driver for the browser (versions may not be the latest or stable; verify as needed):  
   - Chrome Driver: <https://googlechromelabs.github.io/chrome-for-testing/>  
   - Alternative: <http://chromedriver.storage.googleapis.com/index.html>  
   - Edge Driver: <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>  
   - Firefox Driver: <https://github.com/mozilla/geckodriver/releases>  

4. Install Python dependencies:  
   - Run `tool/install_packages.bat` or manually install the following packages:  

     ```packages
     selenium  
     requests  
     pyperclip  
     colorama  
     python-dotenv  
     fastapi  
     uvicorn  
     ```  

### Method 2: Installer Setup (Recommended)  

1. Download the latest EXE file.  
2. Install a browser (Google Chrome recommended), as above.  
3. Install the corresponding web driver.  

## Usage Instructions  

### 1. Launch the Program  

- Source code method: Run `python main.py`.  
- EXE method: Double-click `main.exe`.  

By default, the program starts in Web GUI mode. You can also enter "console" at launch to use the command-line mode (command-line mode is no longer maintained).  

### 2. Configuration  

First-time setup requires configuration:  

1. Select "Configuration" from the main menu.  
2. Enter the following as prompted:  
   - OJ URL (include `http://` or `https://`).  
   - OJ API URL (if unsure, use the same as the OJ URL).  
   - OJ username and password.  
   - AI chat URL (register/login at [360bot](https://bot.n.cn/), create a chat page, and copy the URL).  
   - Browser type (Chrome/Edge/Firefox).  
   - Browser driver path.  
3. Log in to 360bot on the pop-up page to obtain cookies. Press Enter after logging in to complete setup.  

### 3. Automated Problem-Solving  

1. Select "Automated Problem-Solving" from the main menu.  
2. Choose a mode:  
   - Practice problems.  
   - Specified problems.  
   - All problems.  
3. The tool will use AI to solve and submit the problems automatically.  

### 4. Account Management  

1. Select "Ban Accounts" from the main menu.  
2. Choose an operation mode:  
   - Ban all accounts (with optional whitelist).  
   - Ban specified accounts.  

## Technical Implementation  

- **Frontend**: HTML/CSS/JavaScript (pure, *because I don’t know Vue*), providing an intuitive web interface.  
- **Backend**: Python + FastAPI, offering RESTful API services.  
- **Automation**: Selenium for browser automation.  
- **AI Integration**: 360bot for code generation.  
- **Data Storage**: JSON files for saving user configurations.  

## Developer Tools  

The project includes the following developer tools:  

- `tool/install_packages.bat`: Installs required Python dependencies automatically.  
- `tool/minifier.py`: Static file compression tool.  
- `tool/packaging.py`: Uses Nuitka for packaging.  

## Contributing  

1. Fork the repository.  
2. Create a Pull Request.  
3. Star the project :)  

## Disclaimer  

This tool is for learning and research purposes only. Do not use it for any activities that violate academic integrity or relevant regulations. Users bear full responsibility for any consequences arising from its use.  

This tool employs web scraping to retrieve information from 360bot (Nano AI). If your use of this tool infringes upon the rights of *Beijing Qihu Technology Co., Ltd.*, you are solely responsible, and the HOJ Tool developer bears no liability.  

## License  

This project is licensed under the MIT License. See the LICENSE file for details.
