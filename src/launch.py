from ncatbot.core import BotClient
from ncatbot.utils import config
from ncatbot.utils import get_log

_log = get_log()

bot = BotClient()

if __name__ == "__main__":
    _log.info("Bot 启动中")
    bot.run(bt_uin="123456")
