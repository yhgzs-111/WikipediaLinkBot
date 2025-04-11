# ========= 导入必要模块 ==========
from ncatbot.core import BotClient
from ncatbot.core.message import GroupMessage
from ncatbot.core.element import MessageChain, Text
from ncatbot.utils import config, get_log
import re
import ast
import html
from urllib.parse import quote  # 新增URL编码模块

# ========== 设置配置项 ==========
config.set_bot_uin("")  # 设置 bot QQ 号 (必填)

# ========== 创建 BotClient ==========
bot = BotClient()

# ========= 获取日志实例 ==========
_log = get_log()

# ========= 定义允许处理消息的群聊 ==========
allowed_groups = [123456, 12345678]  # 修正为英文逗号

# ========= 注册群聊消息回调函数 ==========
@bot.group_event()
async def on_group_message(msg: GroupMessage):
    # 先对 raw_message 进行 HTML 解码
    raw = html.unescape(msg.raw_message)
    text_content = ""
    
    # 解析消息内容
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

    _log.debug({
        "event": "group_message_received",
        "group_id": msg.group_id,
        "user_id": msg.user_id,
        "message": text_content
    })

    # 仅处理允许的群聊消息
    if msg.group_id in allowed_groups:
        # 处理维基链接格式 [[关键词]]
        wiki_match = re.search(r'\[\[(.*?)\]\]', text_content)
        # 处理Template格式 {{内容}}
        template_match = re.search(r'\{\{(.*?)\}\}', text_content)
        
        if wiki_match:
            keyword = wiki_match.group(1)
            # 对关键词进行URL编码
            encoded_keyword = quote(keyword, encoding='utf-8')
            wiki_url = f"https://zh.wikipedia.org/wiki/{encoded_keyword}"
            reply_message = MessageChain([Text(wiki_url)])
            _log.debug({
                "event": "group_message_reply",
                "reply_to": msg.group_id,
                "reply_message": wiki_url
            })
            await msg.reply(rtf=reply_message)
            
        elif template_match:
            content = template_match.group(1)
            # 对模板内容进行URL编码
            encoded_content = quote(content, encoding='utf-8')
            template_text = f"https://zh.wikipedia.org/wiki/Template:{encoded_content}"
            reply_message = MessageChain([Text(template_text)])
            _log.debug({
                "event": "group_message_reply",
                "reply_to": msg.group_id,
                "reply_message": template_text
            })
            await msg.reply(rtf=reply_message)

# ========== 启动 BotClient ==========
if __name__ == "__main__":
    bot.run()
