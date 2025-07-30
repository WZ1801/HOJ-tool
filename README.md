# HOJ Tool

## 项目介绍

HOJ Tool 是一个针对 HOJ 类在线评测系统(OJ)的辅助工具，主要功能包括自动刷题和账号管理，适用于 Windows 平台。

## 主要功能

1. **自动刷题模块**：利用 AI 辅助自动解答 OJ 平台上的编程题目
2. **账号管理模块**：提供账号相关的管理功能
3. **配置管理**：支持保存用户配置信息，方便后续使用

## 安装教程

### 方法一：源码安装

1. 克隆仓库至本地

   ```shell
   git clone https://gitee.com/wzokee/oj-auto-problem-solver-bot.git
   ```

2. 安装谷歌浏览器

3. 安装谷歌浏览器对应的爬虫驱动（chromedriver）
   - 下载地址1：<https://googlechromelabs.github.io/chrome-for-testing/>
   - 下载地址2：<http://chromedriver.storage.googleapis.com/index.html>

4. 安装 Python 第三方库
   - 运行 `install_packages.bat` 或手动安装依赖包

### 方法二：EXE 安装（推荐）

1. 下载最新版本的 EXE 文件
2. 安装谷歌浏览器
3. 安装谷歌浏览器对应的爬虫驱动（chromedriver）

## 使用说明

### 1. 配置信息

首次使用需要进行配置：

1. 运行 `main.py` 或 `main.exe`
2. 在主菜单中选择 "1.配置信息"
3. 按照提示依次输入：
   - OJ 网址（保留 http:// 或 https://）
   - OJ API 网址（如不清楚，可填写与 OJ 网址相同）
   - OJ 用户名和密码
   - AI 对话地址（需注册登录 [360bot](https://bot.n.cn/)，创建聊天页面后复制网址）
   - ChromeDriver 路径
4. 在弹出的页面登录 360bot 以获取 Cookies，登录后回车完成配置

### 2. 自动刷题

1. 在主菜单中选择 "2.自动刷题"
2. 根据提示选择刷题模式：
   - 刷训练题目
   - 刷指定题目
   - 刷全部题目
3. 程序会自动使用 AI 解答题目并提交

### 3. 账号管理

1. 在主菜单中选择 "3.封禁他人账号"
2. 选择操作模式：
   - 封禁所有账户（可设置白名单）
   - 封禁指定账户

## 技术实现

- 使用 Selenium 进行网页自动化操作
- 利用 360bot AI 接口生成代码解答
- 通过 OJ API 进行题目获取和代码提交
- 支持自动化测试和错误处理

## 参与贡献

1. Fork 本仓库
2. 新建 Pull Request
3. 提交 issues
4. Star 本仓库

## 免责声明

本工具仅供学习和研究使用，请勿用于任何违反学术诚信或相关规定的行为。使用本工具产生的一切后果由使用者自行承担。
