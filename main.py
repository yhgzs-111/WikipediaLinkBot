# ========= 导入必要模块 ==========
# 导入 ncatbot 的核心模块，用于实现 QQ 机器人功能
from ncatbot.core import BotClient           # 机器人客户端类
from ncatbot.core.message import GroupMessage  # 群聊消息类
from ncatbot.core.element import MessageChain, Text  # 消息链和文本元素类
from ncatbot.utils import config, get_log    # 配置和日志工具
import re                                    # 正则表达式模块，用于匹配消息格式
import ast                                   # 抽象语法树模块，用于安全解析消息链
import html                                  # HTML 解码模块，用于处理消息中的 HTML 实体
from urllib.parse import quote               # URL 编码模块，用于处理特殊字符

# ========== 设置配置项 ==========
# 设置机器人的 QQ 号（必填项，请替换为实际 QQ 号）
config.set_bot_uin("123456789")  # 示例 QQ 号，请替换为您的实际 QQ 号

# ========== 创建 BotClient ==========
# 创建一个 BotClient 实例，用于与 QQ 服务器通信并处理消息
bot = BotClient()

# ========= 获取日志实例 ==========
# 获取日志记录器实例，用于记录信息、调试和错误
_log = get_log()

# ========= 定义允许处理消息的群聊 ==========
# 定义一个列表，包含允许机器人处理消息的群聊 ID（请替换为实际群号）
allowed_groups = [987654321, 123456789]  # 示例群号，请替换为您的实际群聊 ID

# ========= 注册群聊消息回调函数 ==========
@bot.group_event()  # 使用装饰器注册群聊消息事件处理器
async def on_group_message(msg: GroupMessage):
    """
    群聊消息回调函数，用于处理接收到的群聊消息。
    
    :param msg: GroupMessage 类型，包含消息的详细信息（如群 ID、用户 ID、原始消息等）
    """
    # 对原始消息进行 HTML 解码，以处理可能存在的 HTML 实体（如 &amp; 转换为 &）
    raw = html.unescape(msg.raw_message)
    
    # 初始化一个空字符串，用于存储解析后的消息文本内容
    text_content = ""
    
    # 检查消息是否以 "[{" 开头，这是 QQ 消息链的典型 JSON 格式
    if raw.lstrip().startswith("[{"):
        try:
            # 使用 ast.literal_eval 安全地将字符串解析为 Python 对象，避免直接使用 eval 的安全风险
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, list):  # 如果解析结果是一个列表（消息链）
                # 遍历消息链中的每个元素
                for element in parsed:
                    if isinstance(element, dict) and element.get("type") == "text":
                        # 如果元素是文本类型，提取 "data" 字典中的 "text" 字段
                        text_content += element.get("data", {}).get("text", "")
                    else:
                        # 如果不是文本类型（如图片、表情等），将其转换为字符串并追加
                        text_content += str(element)
            else:
                # 如果解析结果不是列表，直接将其转换为字符串
                text_content = str(parsed)
        except Exception as e:
            # 如果解析失败（可能是格式错误），记录错误并使用原始消息内容
            _log.error({
                "event": "parse_message_error",    # 事件类型
                "error": str(e),                   # 错误信息
                "raw_message": raw                 # 原始消息内容
            })
            text_content = raw  # 解析失败时回退到原始消息
    else:
        # 如果消息不以 "[{" 开头，说明不是消息链，直接使用原始消息内容
        text_content = raw

    # 记录收到的群聊消息的信息（使用 info 级别）
    _log.info({
        "event": "group_message_received",  # 事件类型
        "group_id": msg.group_id,           # 群聊 ID
        "user_id": msg.user_id,             # 发送者 ID
        "message": text_content             # 解析后的消息内容
    })

    # 仅处理来自允许群聊的消息
    if msg.group_id in allowed_groups:
        # 使用正则表达式检查消息是否包含维基链接格式 [[语言代码:关键词]] 或 [[关键词]]
        wiki_match = re.search(r'\[\[(?:(\w+):)?(.+?)\]\]', text_content)
        # 使用正则表达式检查消息是否包含 Template 格式 {{内容}}
        template_match = re.search(r'\{\{(.*?)\}\}', text_content)
        
        if wiki_match:
            # 提取语言代码（如果有）和关键词
            lang = wiki_match.group(1) or "zh"  # 默认使用中文
            keyword = wiki_match.group(2).strip()  # 去除首尾空白
            if keyword:  # 确保关键词不为空
                # 构造 Wikipedia 链接并进行 URL 编码
                wiki_url = f"https://{lang}.wikipedia.org/wiki/{quote(keyword)}"
                # 创建回复消息链
                reply_message = MessageChain([Text(wiki_url)])
                # 记录回复的信息（使用 info 级别）
                _log.info({
                    "event": "group_message_reply",  # 事件类型
                    "reply_to": msg.group_id,        # 回复的目标群聊 ID
                    "reply_message": wiki_url        # 回复的消息内容
                })
                # 异步发送回复消息
                await msg.reply(rtf=reply_message)
        elif template_match:
            # 提取 {{ }} 中的内容并去除首尾空白
            content = template_match.group(1).strip()
            if content:  # 确保内容不为空
                # 构造 Wikipedia Template 页面链接并进行 URL 编码
                template_url = f"https://zh.wikipedia.org/wiki/Template:{quote(content)}"
                # 创建回复消息链
                reply_message = MessageChain([Text(template_url)])
                # 记录回复的信息（使用 info 级别）
                _log.info({
                    "event": "group_message_reply",  # 事件类型
                    "reply_to": msg.group_id,        # 回复的目标群聊 ID
                    "reply_message": template_url    # 回复的消息内容
                })
                # 异步发送回复消息
                await msg.reply(rtf=reply_message)

# ========== 启动 BotClient ==========
if __name__ == "__main__":
    # 在主程序中启动机器人客户端，开始监听和处理消息
    bot.run()
