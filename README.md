# OJ自动刷题爬虫

## 介绍

利用AI（ 360bot ）对HOJ类OJ的自动爬虫刷题系统，适配于 $Windows$

## 安装教程

⚠EXE现阶段不稳定，非必要不建议下载

1. 克隆仓库至本地 (下载EXE的忽略)

   ```Shell
   git clone https://gitee.com/wzokee/oj-auto-problem-solver-bot.git
   ```

2. 安装谷歌浏览器

3. 安装谷歌浏览器的对应的爬虫驱动（ chromedriver ）: [下载地址1](https://googlechromelabs.github.io/chrome-for-testing/)、[下载地址2](http://chromedriver.storage.googleapis.com/index.html)

4. 安装 Python 第三方库（ 运行 install_packages.bat ） (下载EXE的忽略)

## 使用说明

1. 打开  main.py  或  main.exe

   ![](README_md_files/083065a0-e789-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

   打开后显示为（主菜单）：

   ![](README_md_files/3c353330-e789-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

2. 配置信息（按照提示操作，之前配置过会保存）

   1. 输入1，回车

      ![](README_md_files/51c78220-e789-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

   2. 输入OJ网址（保留 http:// 或 https:// ）、账号、密码，回车

      ![](README_md_files/d3ae8360-e789-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

   3. 注册登录[360bot](https://bot.n.cn/)账号，随便建个聊天页面，选择模型，聊一句，复制网址，填入程序内的AI对话地址（保留 http:// 或 https://），回车

      ![](README_md_files/7769f2f0-e78a-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

      ![](README_md_files/b82154f0-e78a-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

   4. 输入 ChromeDriver 地址（不要套双引号或单引号），回车

      ![](README_md_files/4b7f7790-e78b-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

   5. 在弹出的页面登录 360bot（以获取Cookies自动登录），登录后回车，完成配置，配置会保存在同目录下的 user_data.json

      ![](README_md_files/ee2c0f30-e78b-11ef-a208-5967ca193d2f.jpeg?v=1&type=image)

3. 开始刷题（按照提示操作，可刷训练，可刷个题）

## 参与贡献

1. Fork 本仓库

2. 新建 Pull Request

3. 提交 issues

