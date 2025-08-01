# HOJ Tool

## Project Introduction

HOJ Tool is an auxiliary tool for HOJ-like online judging systems (OJ), with main functions including automatic problem solving and account management, suitable for Windows platform.

## Main Features

1. **Auto Problem Solver Module**: Uses AI assistance to automatically solve programming problems on OJ platforms
2. **Account Management Module**: Provides account-related management functions
3. **Configuration Management**: Supports saving user configuration information for convenient future use

## Installation Guide

### Method 1: Source Code Installation

1. Clone the repository to local

   ```shell
   git clone https://gitee.com/wzokee/oj-auto-problem-solver-bot.git
   ```

2. Install Google Chrome browser

3. Install the corresponding web crawler driver (chromedriver) for Google Chrome
   - Download link 1: <https://googlechromelabs.github.io/chrome-for-testing/>
   - Download link 2: <http://chromedriver.storage.googleapis.com/index.html>

4. Install Python third-party libraries
   - Run `install_packages.bat` or manually install dependencies

### Method 2: EXE Installation (Recommended)

1. Download the latest version of the EXE file
2. Install Google Chrome browser
3. Install the corresponding web crawler driver (chromedriver) for Google Chrome

## Usage Instructions

### 1. Configuration

Initial configuration is required for first use:

1. Run `main.py` or `main.exe`
2. Select "1.Configuration" in the main menu
3. Follow the prompts to enter the following information:
   - OJ URL (keep http:// or https://)
   - OJ API URL (if unsure, fill in the same as OJ URL)
   - OJ username and password
   - AI chat URL (need to register and login to [360bot](https://bot.n.cn/), create a chat page and copy the URL)
   - ChromeDriver path
4. Login to 360bot in the pop-up page to obtain Cookies, press Enter after login to complete configuration

### 2. Auto Problem Solving

1. Select "2.Auto Problem Solver" in the main menu
2. Choose the problem solving mode according to the prompts:
   - Solve training problems
   - Solve specified problems
   - Solve all problems
3. The program will automatically use AI to solve problems and submit

### 3. Account Management

1. Select "3.Ban Others' Accounts" in the main menu
2. Choose operation mode:
   - Ban all accounts (whitelist can be set)
   - Ban specified accounts

## Technical Implementation

- Uses Selenium for web automation
- Utilizes 360bot AI interface to generate code solutions
- Retrieves problems and submits code through OJ API
- Supports automated testing and error handling

## Contributing

1. Fork this repository
2. Create a new Pull Request
3. Submit issues
4. Star this repository

## Disclaimer

This tool is for learning and research purposes only. Please do not use it for any behavior that violates academic integrity or relevant regulations. All consequences arising from the use of this tool shall be borne by the user.
