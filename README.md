# ~~代码作者：ChatGPT~~
~~# 本代码尊崇能跑就行，不建议拿来使用~~。目前已修复，欢迎有志之士提交PRs :) 
~~![image](https://github.com/user-attachments/assets/7a4b8c1e-d886-43df-af92-d047dd9d1ffb)~~

~~至少目前还没爆炸😇~~
# 说明
## 准备
* [NapCat.Shell](https://napneko.github.io/guide/boot/Shell#napcat-shell-win%E6%89%8B%E5%8A%A8%E5%90%AF%E5%8A%A8%E6%95%99%E7%A8%8B)
* 支持Windows 7+系统，其它系统未测试
* [Python](https://www.python.org) 3.7+
* [Ncatbot](https://docs.ncatbot.xyz/)
```python
pip install Ncatbot
```
## 安装与配置

1. **环境准备**
   - 确保已安装 Python 3.7+
   - 安装必要的依赖库：`pip install ncatbot`
   - 确保NapCat.Shell已下载并解压到同文件夹中的"Napcat"文件夹并按照[官方文档](https://napneko.github.io/)进行登陆操作
   - 确保Ncatbot按照[官方文档](https://docs.ncatbot.xyz/)配置完成

2. **配置机器人**
   - 修改launch.py中的 `bot.run(bt_uin="123456")`，改为你的机器人 QQ 号

## 使用方法

### 基本功能

机器人会自动识别以下三种格式的消息并生成对应的维基百科链接进行回复：

#### 📘 支持的格式：

1. `[[关键词]]`  
   - 生成中文维基百科条目链接，如：  
     `[[计算机]]` → `https://zh.wikipedia.org/wiki/计算机`

2. `[[:语言:条目名字]]`  
   - 支持指定语言的维基百科链接，如：  
     `[[:en:Computer]]` → `https://en.wikipedia.org/wiki/Computer`

3. `{{内容}}` （模板链接）  
   - 若为 `{{:语言:模板名}}`，则使用对应语言的模板页面：  
     `{{:en:Infobox}}` → `https://en.wikipedia.org/wiki/Template:Infobox`  
   - 否则默认使用中文模板链接：  
     `{{信息框}}` → `https://zh.wikipedia.org/wiki/Template:信息框`

### 运行机器人
```python
python launch.py
```

## 注意事项
1. 机器人默认响应所有已加入的群聊
2. 确保机器人账号已加入这些群聊并有发送消息的权限
3. 机器人会自动忽略不符合上述格式的消息
4. 如需查看运行日志，请检查控制台输出或配置日志系统
5. 使用非官方机器人均有**冻结/封号**风险

## 鸣谢
* [Napcat](https://napneko.github.io/)
* [Ncatbot](https://docs.ncatbot.xyz/)
* [User:FennelMa](https://zh.wikipedia.org/wiki/User:FennelMa) (Chinese Wikipedia)
* [User:Xiumuzidiao](https://zh.wikipedia.org/wiki/User:Xiumuzidiao) (Chinese Wikipedia)
* [mononobealice](https://github.com/HermaeusMoraMainTank)
