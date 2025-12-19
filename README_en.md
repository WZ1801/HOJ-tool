# HOJ Tool

## Project Introduction

HOJ Tool is an auxiliary tool for [HOJ](https://gitee.com/himitzh0730/hoj)-like online judge (OJ) systems, providing automated problem-solving and account management functions. It supports both command-line and web interfaces and is suitable for the Windows platform.

## Main Features

1. **Automated Problem-Solving Module**: Utilizes AI to assist in automatically solving programming problems on the OJ platform.
   - Supports three problem-solving modes: training problems, specified problems, and all problems.
   - Generates solution code using web crawlers.
   - Ensures foolproof submission through callback mechanisms.

2. **Account Management Module**: Provides account-related management functions
   - Supports banning specified accounts
   - Supports batch banning of accounts (with whitelist settings available)

## System Requirements

- Operating System: Windows 10/11
- Browser: Google Chrome, Microsoft Edge, or Firefox
- Network Connection: A stable internet connection is required
- Python Environment: See `pyproject.toml` for details

## Installation Tutorial

### Method One: Source Code Deployment

1. Clone the repository to your local machine

   ```shell
   git clone <https://gitee.com/wzokee/hoj-tool.git>
   ```

2. Install a browser
   - <https://www.google.cn/chrome/>
   - <https://www.firefox.com/>
   - <https://www.microsoft.com/edge/download>

3. Install the corresponding crawler driver for your browser (it may not be the latest or most stable, please use your own discretion)
   - Chrome driver download address: <https://googlechromelabs.github.io/chrome-for-testing/>
   - Or: <http://chromedriver.storage.googleapis.com/index.html>

- Edge Driver Download Link: <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
- Firefox Driver Download Link: <https://github.com/mozilla/geckodriver/releases>

4. Install Python Third-Party Libraries

- Run `tool/install_packages.bat`

### Method Two: Installer Package Installation (Recommended)

1. Download the latest version of the installer package file
2. Follow the prompts to install
3. Install the browser, same as above
4. Install the crawler driver corresponding to the browser, same as above

## Instructions for Use

### 1. Start the Program

- Source code method: Run `python main.py`
- Installer method: Double-click `main.exe`

After startup, it defaults to Web GUI mode. Alternatively, if deploying from source code, you can add the parameter `python main.py -console` at startup to enter command-line mode (command-line mode is no longer updated).

### 2. Configuration Information

Initial setup is required for first-time use:

1. Select "Configuration" from the main menu
2. Follow the prompts to enter the following:
   - OJ URL (retain http:// or https://)

- OJ API URL (if unsure, you can fill in the same as the OJ URL)
  - OJ username and password
  - AI chat address (you need to register and log in to [360bot](https://bot.n.cn/), then create a chat page and copy the URL)
  - Browser type (Chrome/Edge/Firefox)
- Browser driver path

### 3. Automated Problem Solving

1. Select "Automated Problem Solving" from the main menu
2. Choose the problem-solving mode as prompted:

- Solve training problems
  - Solve specified problems
  - Solve all problems

3. Log in to 360bot and click the "Logged in to 360bot button"

4. The program will automatically use AI to solve problems and submit solutions.

### 4. Account Management

1. Select "Ban Other Accounts" from the main menu.
2. Enter the username to be banned as prompted.
3. The program will automatically perform the ban operation.

## Important Notes

1. This tool is for learning and exchange purposes only. Please comply with the terms of use of all OJ platforms and Nano AI.
2. The user is solely responsible for any consequences resulting from the use of this tool.
3. Please use AI-assisted features responsibly to avoid overburdening AI services.
4. It is recommended to back up important data before use.
5. If you encounter problems, please check the console output or log files.

## FAQ

### 1. Unable to Start Web Interface

Possible Causes:

- WebView2 runtime environment is not installed (Windows 10/11 usually comes with it)
- Port is occupied (default uses port 1146)
- Firewall blocking the program from running

Solution:

- Install Microsoft Edge WebView2 Runtime
- Check port occupancy
- Add the program to the firewall whitelist

### 2. Browser Driver Issues

Possible causes:

- Driver version does not match browser version
- Incompatible system
- Incorrect driver path configuration
- Corrupted driver file

Solution:

- Download the driver that matches your browser version
- Check frameworks like X86, and ensure they match the system
- Check and correctly configure the driver path
- Re-download the driver file

<sub>Can you give it a star? 🌟</sub>