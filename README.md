# HOJ Tool

## 项目介绍

HOJ Tool 是一个针对 HOJ 类在线评测系统(OJ)的辅助工具，提供自动刷题和账号管理功能，支持命令行和Web界面两种操作模式，适用于 Windows 平台。

## 主要功能

1. **自动刷题模块**：利用 AI 辅助自动解答 OJ 平台上的编程题目
   - 支持训练题目、指定题目和全部题目三种刷题模式
   - 自动分析题目要求并生成解答代码
   - 智能提交并验证结果

2. **账号管理模块**：提供账号相关的管理功能
   - 支持封禁指定账号
   - 支持批量封禁账号（可设置白名单）

3. **双模式操作界面**：
   - 命令行控制台模式：轻量级操作
   - Web GUI模式：基于FastAPI的现代化Web界面

4. **配置管理**：支持保存用户配置信息，方便后续使用

## 系统要求

- 操作系统：Windows 10/11
- 浏览器：Google Chrome（推荐）、Microsoft Edge 或 Firefox
- 网络连接：需要稳定的互联网连接

## 安装教程

### 方法一：源码部署

1. 克隆仓库至本地

   ```shell
   git clone https://gitee.com/wzokee/hoj-tool.git
   ```

2. 安装浏览器（推荐 Google Chrome）

3. 安装浏览器对应的爬虫驱动（有可能非最新、稳定，请自行辨别）
   - Chrome驱动下载地址：<https://googlechromelabs.github.io/chrome-for-testing/>
   - 或：<http://chromedriver.storage.googleapis.com/index.html>
   - Edge驱动下载地址：<https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
   - Firefox驱动下载地址：<https://github.com/mozilla/geckodriver/releases>

4. 安装 Python 第三方库
   - 运行 `tool/install_packages.bat` 或手动安装以下依赖包：

     ```packages
     selenium
     requests
     pyperclip
     colorama
     python-dotenv
     fastapi
     uvicorn
     ```

### 方法二：安装包安装（推荐）

1. 下载最新版本的 EXE 文件
2. 安装浏览器（推荐 Google Chrome），同上
3. 安装浏览器对应的爬虫驱动

## 使用说明

### 1. 启动程序

- 源码方式：运行 `python main.py`
- EXE方式：双击 `main.exe`

启动后默认进入Web GUI模式，也可以在启动时输入"console"进入命令行模式（已停更命令行模式）。

### 2. 配置信息

首次使用需要进行配置：

1. 在主菜单中选择 "配置信息"
2. 按照提示依次输入：
   - OJ 网址（保留 http:// 或 https://）
   - OJ API 网址（如不清楚，可填写与 OJ 网址相同）
   - OJ 用户名和密码
   - AI 对话地址（需注册登录 [360bot](https://bot.n.cn/)，创建聊天页面后复制网址）
   - 浏览器类型（Chrome/Edge/Firefox）
   - 浏览器驱动路径
3. 在弹出的页面登录 360bot 以获取 Cookies，登录后回车完成配置

### 3. 自动刷题

1. 在主菜单中选择 "自动刷题"
2. 根据提示选择刷题模式：
   - 刷训练题目
   - 刷指定题目
   - 刷全部题目
3. 程序会自动使用 AI 解答题目并提交

### 4. 账号管理

1. 在主菜单中选择 "封禁他人账号"
2. 选择操作模式：
   - 封禁所有账户（可设置白名单）
   - 封禁指定账户

## 技术实现

- **前端**：HTML/CSS/JavaScript，纯净<sub>因为我不会Vue</sub>，提供直观的Web操作界面
- **后端**：Python + FastAPI，提供RESTful API接口
- **自动化**：Selenium，实现浏览器自动化操作
- **AI集成**：360bot，提供代码生成能力
- **数据存储**：JSON文件，保存用户配置信息

## 开发者工具

项目包含以下开发者工具：

- `tool/install_packages.bat`：自动安装所需Python依赖
- `tool/minifier.py`：静态文件压缩工具
- `tool/packaging.py`：使用Nuitka打包程序

## 参与贡献

1. Fork 本仓库
2. 创建 Pull Request
3. Star 本项目：）

## 免责声明

本工具仅供学习和研究使用，请勿用于任何违反学术诚信或相关规定的行为。使用本工具产生的一切后果由使用者自行承担。

本工具使用爬虫获取360bot（纳米AI）信息，您在使用时如果**侵犯"北京奇虎科技有限公司"的权益**后果自负，与HOJtool开发者无关

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。
