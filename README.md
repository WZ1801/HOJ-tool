

# HOJ Tool

## 项目介绍

HOJ Tool 是一个针对 [HOJ](https://gitee.com/himitzh0730/hoj) 类在线评测系统（OJ）的辅助工具，提供自动刷题和账号管理功能。它支持命令行和Web界面两种操作模式，适用于 Windows 平台。

## 主要功能

1. **自动刷题模块**：利用 AI 辅助自动解答 OJ 平台上的编程题目
   - 支持训练题目、指定题目和全部题目三种刷题模式
   - 使用爬虫生成解答代码
   - 回调提交确保万无一失

2. **账号管理模块**：提供账号相关的管理功能
   - 支持封禁指定账号
   - 支持批量封禁账号（可设置白名单）

## 系统要求

- 操作系统：Windows 10/11
- 浏览器：Google Chrome、Microsoft Edge 或 Firefox
- 网络连接：需要稳定的互联网连接
- Python 环境：详见 `pyproject.toml`

## 安装教程

### 方法一：源码部署

1. 克隆仓库至本地

   ```shell
   git clone https://gitee.com/wzokee/hoj-tool.git
   ```

2. 安装浏览器
   - [Google Chrome](https://www.google.cn/chrome/)
   - [Firefox](https://www.firefox.com/)
   - [Microsoft Edge](https://www.microsoft.com/edge/download)

3. 安装浏览器对应的爬虫驱动（有可能非最新、稳定，请自行辨别）
   - Chrome驱动下载地址：<https://googlechromelabs.github.io/chrome-for-testing/>
   - 或：<http://chromedriver.storage.googleapis.com/index.html>
   - Edge驱动下载地址：<https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
   - Firefox驱动下载地址：<https://github.com/mozilla/geckodriver/releases>

4. 安装 Python 第三方库
   - 运行 `tool/install_packages.bat`

### 方法二：安装包安装（推荐）

1. 下载最新版本的安装包文件
2. 按照提示安装
3. 安装浏览器，同上
4. 安装浏览器对应的爬虫驱动，同上

## 使用说明

### 1. 启动程序

- 源码方式：运行 `python main.py`
- 安装包方式：双击 `main.exe`

启动后默认进入 Web GUI 模式，也可以使用源码部署方式并在启动时加参数 `python main.py -console` 进入命令行模式（已停更命令行模式）。

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

### 3. 自动刷题

1. 在主菜单中选择 "自动刷题"
2. 根据提示选择刷题模式：
   - 刷训练题目
   - 刷指定题目
   - 刷全部题目
3. 登录 360bot 并点击 "已登录360bot按钮"
4. 程序会自动使用 AI 解答题目并提交

### 4. 账号管理

1. 在主菜单中选择 "封禁他人账号"
2. 根据提示输入要封禁的用户名
3. 程序会自动执行封禁操作

## 注意事项

1. 本工具仅供学习交流使用，请遵守各 OJ 平台和纳米 AI 的使用条款
2. 使用本工具造成的任何后果由使用者自行承担
3. 请合理使用 AI 辅助功能，避免对 AI 服务造成过大负担
4. 建议在使用前备份重要数据
5. 如遇到问题，请查看控制台输出或日志文件

## 常见问题

### 1. 无法启动 Web 界面

可能原因：

- 未安装 WebView2 运行环境（Windows 10/11 通常自带）
- 端口被占用（默认使用 1146 端口）
- 防火墙阻止程序运行

解决方案：

- 安装 Microsoft Edge WebView2 Runtime
- 检查端口占用情况
- 将程序添加到防火墙白名单

### 2. 浏览器驱动问题

可能原因：

- 驱动版本与浏览器版本不匹配
- 不兼容系统
- 驱动路径配置错误
- 驱动文件损坏

解决方案：

- 下载与浏览器版本匹配的驱动
- 检查框架如 X86，与系统兼容
- 检查并正确配置驱动路径
- 重新下载驱动文件

<sub>可以点个 star 吗 🌟</sub>