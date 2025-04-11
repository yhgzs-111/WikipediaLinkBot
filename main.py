# ========= 导入必要模块 ==========
from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage
from ncatbot.core.element import MessageChain, Text
from ncatbot.utils import config, get_log
import re
import ast
import html
import urllib.parse

# ========= 设置配置项 ==========
config.set_bot_uin("your_bot_uin_here")  # 设置 bot QQ 号

# ========= 创建 BotClient ==========
bot = BotClient()

# ========= 获取日志实例 ==========
_log = get_log()

# 定义允许处理消息的群聊列表
allowed_groups = [
    123456789,  # 群A
    987654321,  # 群B
    112233445   # 群C
]

# ========== 预编译正则表达式 ==========
# 匹配形如 [[:lang:entry]] 格式，用于构造跨语言 Wikipedia 链接
REGEX_LANG = re.compile(r'\[\[:([a-zA-Z0-9\-]+):(.*?)\]\]')
# 匹配形如 [[keyword]] 格式
REGEX_WIKI = re.compile(r'\[\[(.*?)\]\]')
# 匹配形如 {{...}} 的模板格式
REGEX_TEMPLATE = re.compile(r'\{\{(.*?)\}\}')
# 匹配模板内部类似 ":lang:template" 的格式（使用 search 更灵活）
REGEX_TEMPLATE_COLON = re.compile(r'\:\s*([a-zA-Z0-9\-]+):(.*)')

# ========== 工具函数 ==========

def parse_raw_message(raw: str) -> str:
    """
    处理原始消息文本，将转义字符转换为正常字符，
    并解析 JSON 格式的消息（如果符合格式）。
    """
    raw = html.unescape(raw)
    text_content = ""
    if raw.lstrip().startswith("[{"):
        try:
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, list):
                for element in parsed:
                    if isinstance(element, dict) and element.get("type") == "text":
                        text_content += element.get("data", {}).get("text", "")
                    else:
                        text_content += str(element)
            else:
                text_content = str(parsed)
        except Exception as e:
            _log.error({
                "event": "parse_message_error",
                "error": str(e),
                "raw_message": raw
            })
            text_content = raw
    else:
        text_content = raw
    return text_content

def build_wiki_url(text: str) -> str:
    """
    根据输入文本构造对应的 Wikipedia URL。
    支持以下几种格式：
     1. [[:lang:entry]] -> 构造 https://{lang}.wikipedia.org/wiki/{entry} 链接
     2. [[keyword]] -> 默认构造中文 Wikipedia 链接：https://zh.wikipedia.org/wiki/{keyword}
     3. {{...}} 模板格式 -> 构造相应 Template 链接
    """
    # 尝试匹配 [[:lang:entry]] 格式
    lang_match = REGEX_LANG.search(text)
    if lang_match:
        lang = lang_match.group(1).strip()
        entry = lang_match.group(2).strip()
        # 将空格替换为下划线
        entry = entry.replace(' ', '_')
        entry_enc = urllib.parse.quote(entry)
        return f"https://{lang}.wikipedia.org/wiki/{entry_enc}"

    # 尝试匹配 [[keyword]] 格式
    wiki_match = REGEX_WIKI.search(text)
    if wiki_match:
        keyword = wiki_match.group(1).strip()
        keyword = keyword.replace(' ', '_')
        keyword_enc = urllib.parse.quote(keyword)
        return f"https://zh.wikipedia.org/wiki/{keyword_enc}"
    
    # 尝试匹配模板格式 {{...}}
    template_match = REGEX_TEMPLATE.search(text)
    if template_match:
        content = template_match.group(1).strip()
        # 使用 search 而非 match，以便匹配字符串中的 :lang: 模式
        colon_match = REGEX_TEMPLATE_COLON.search(content)
        if colon_match:
            lang = colon_match.group(1).strip()
            template_name = colon_match.group(2).strip()
            template_name = template_name.replace(' ', '_')
            template_enc = urllib.parse.quote(template_name)
            return f"https://{lang}.wikipedia.org/wiki/Template:{template_enc}"
        else:
            content = content.replace(' ', '_')
            template_enc = urllib.parse.quote(content)
            return f"https://zh.wikipedia.org/wiki/Template:{template_enc}"

    # 如果没有匹配到任何格式，则记录日志并返回空字符串
    _log.debug({
        "event": "wiki_url_not_found",
        "text": text
    })
    return ""

async def reply_and_log(msg: GroupMessage, reply_text: str):
    """
    将构造好的 URL 回复给群组，并记录回复日志。
    """
    reply_message = MessageChain([Text(reply_text)])
    _log.debug({
        "event": "group_message_reply",
        "reply_to": msg.group_id,
        "reply_message": reply_text
    })
    await msg.reply(rtf=reply_message)

# ========= 注册群聊消息回调函数 ==========
@bot.group_event()
async def on_group_message(msg: GroupMessage):
    """
    当收到群消息时，解析文本并检查是否需要回复 Wikipedia 的链接。
    仅处理允许的群组消息。
    """
    text_content = parse_raw_message(msg.raw_message)
    
    _log.debug({
        "event": "group_message_received",
        "group_id": msg.group_id,
        "user_id": msg.user_id,
        "message": text_content
    })

    if msg.group_id not in allowed_groups:
        return

    wiki_url = build_wiki_url(text_content)
    if wiki_url:
        await reply_and_log(msg, wiki_url)

# ========= 启动 BotClient ==========
if __name__ == "__main__":
    bot.run()
