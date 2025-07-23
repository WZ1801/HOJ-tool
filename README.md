

# HOJ tool

此项目已被![](http://saobby.pythonanywhere.com/api/webcounter?id=s6d4DBNcr508Rklx)台设备访问（每ip算一个）

## 介绍
这是一个用于在线评测系统（OJ）的自动化工具，主要功能包括：
- 自动刷题
- 账号封禁
- 题目代码自动提交

## 安装教程
1. 确保已安装Python环境
2. 安装依赖库：
```bash
pip install selenium requests pyperclip hashlib re logging json threading datetime
```
3. 下载并配置ChromeDriver
4. 克隆本仓库：
```bash
git clone https://gitee.com/wzokee/hoj-tool
```

## 使用说明

### 自动刷题模块
该模块可以:
- 自动获取训练题目
- 使用AI生成解决方案
- 自动提交代码
- 处理WA情况下的回调修复

### 封禁账号模块
该模块可以:
- 封禁指定账号
- 封禁所有非白名单账号
- 从排行榜获取用户名进行批量封禁

## 参与贡献
欢迎对本项目进行改进和优化，包括：
1. 提升代码的稳定性和容错能力
2. 增加新的功能模块
3. 优化AI提示词和交互逻辑
4. 改进文档和使用说明

## 配置说明
在首次运行时，需要配置以下信息：
- OJ网址
- OJ API网址
- OJ用户名和密码
- AI对话地址
- ChromeDriver路径

## 注意事项
- 本工具仅供学习参考
- 使用前请确保已正确配置信息
- 封号功能只可用于合法授权的账号管理
- 自动刷题功能请适度使用，避免对OJ服务器造成过大压力

## 开源协议
本项目采用MIT协议，请遵守相关开源协议规定。