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
config.set_bot_uin("your_bot_uin_here")  # 设置 bot QQ 号（已脱敏）

# ========= 创建 BotClient ==========
bot = BotClient()

# ========= 获取日志实例 ==========
_log = get_log()

# 定义允许处理消息的群聊列表（群号已脱敏为示意）
allowed_groups = [
    123456789,  # 群A
    987654321,  # 群B
    112233445   # 群C
]

# --- 工具函数 ---

def parse_raw_message(raw: str) -> str:
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
    lang_match = re.search(r'\[\[\:\s*([a-zA-Z0-9\-]+)\s*:(.*?)\]\]', text)
    if lang_match:
        lang = lang_match.group(1).strip()
        entry = lang_match.group(2).strip()
        entry_enc = urllib.parse.quote(entry)
        return f"https://{lang}.wikipedia.org/wiki/{entry_enc}"

    wiki_match = re.search(r'\[\[(.*?)\]\]', text)
    if wiki_match:
        keyword = wiki_match.group(1).strip()
        keyword_enc = urllib.parse.quote(keyword)
        return f"https://zh.wikipedia.org/wiki/{keyword_enc}"
    
    template_match = re.search(r'\{\{(.*?)\}\}', text)
    if template_match:
        content = template_match.group(1).strip()
        colon_match = re.match(r'\:\s*([a-zA-Z0-9\-]+)\s*:(.*)', content)
        if colon_match:
            lang = colon_match.group(1).strip()
            template_name = colon_match.group(2).strip()
            template_enc = urllib.parse.quote(template_name)
            return f"https://{lang}.wikipedia.org/wiki/Template:{template_enc}"
        else:
            template_enc = urllib.parse.quote(content)
            return f"https://zh.wikipedia.org/wiki/Template:{template_enc}"

    return ""


async def reply_and_log(msg: GroupMessage, reply_text: str):
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
