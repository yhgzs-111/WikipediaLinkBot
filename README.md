# WikipediaLinkBot
本项目用于在用户发送”[[Example]]""{{Example}}"时，QQ机器人会回复” https://zh.wikipedia.org/wiki/ “+ "[[]]里的内容"或Template:“{{}}里的内容”
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
   - 修改代码中的 `config.set_bot_uin("")`，填入你的机器人 QQ 号
   - 修改 `allowed_groups` 列表，添加允许机器人处理的群号

## 使用方法

### 基本功能
机器人会自动识别两种特殊格式的消息并回复：

1. **维基百科词条链接**
   - 格式：`[[关键词]]`
   - 示例：`[[Python]]`
   - 回复：`https://zh.wikipedia.org/wiki/Python`

2. **维基百科模板链接**
   - 格式：`{{模板名}}`
   - 示例：`{{Infobox software}}`
   - 回复：`https://zh.wikipedia.org/wiki/Template:Infobox_software`

## 新增功能
1. **多语言支持**
   可以通过 `[[en:Python]]` 或 `[[Python]]` 生成对应语言的 Wikipedia 链接，默认中文。

2. **防崩溃**
   通过输入验证和错误处理，确保程序不会因无效输入而崩溃。

3. **实用性**
   支持 Wikipedia 页面和 Template 页面链接生成，满足多种使用场景。

### 运行机器人
```python
python main.py
```

## 注意事项
1. 机器人只会响应 `allowed_groups` 列表中指定的群聊
2. 确保机器人账号已加入这些群聊并有发送消息的权限
3. 机器人会自动忽略不符合上述两种格式的消息
4. 如需查看运行日志，请检查控制台输出或配置日志系统

## 鸣谢
* [Napcat](https://napneko.github.io/)
* [Ncatbot](https://docs.ncatbot.xyz/)
* [User:FennelMa](https://zh.wikipedia.org/wiki/User:FennelMa) (Chinese Wikipedia)
