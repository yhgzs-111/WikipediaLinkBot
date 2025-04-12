from ncatbot.core import BotClient
from ncatbot.utils import config
from ncatbot.utils import get_log

_log = get_log()
config.set_bot_uin("123456")  # 设置 bot qq 号 (必填)
config.set_ws_uri("ws://localhost:3001")  # 设置 napcat websocket server 地址

bot = BotClient()

if __name__ == "__main__":
    _log.info("Bot 启动中")
    bot.run()
