import re
import ast
import html
import urllib.parse
import wikipedia
from ncatbot.core.message import GroupMessage
from ncatbot.plugin import CompatibleEnrollment, BasePlugin
from wikipedia.exceptions import DisambiguationError, PageError

# 加载敏感词列表
with open(r"C:\Users\Administrator\Desktop\wikipediabot\plugins\WikiLink\profanities.txt", encoding="utf-8") as f:
    SENSITIVE_WORDS = [line.strip() for line in f if line.strip()]

bot = CompatibleEnrollment

class WikiLink(BasePlugin):
    name = "WikiLink"
    version = "1.3"

    REGEX_PATTERNS = {
        # 指定语言条目 [[ :lang:entry ]]
        "lang": re.compile(r"\[\[:(?P<lang>[a-zA-Z0-9\-]+):(?P<entry>.*?)\]\]"),
        # 中文条目 [[entry]], 排除以 ':' 开头
        "wiki": re.compile(r"\[\[(?!:)(?P<content>.*?)\]\]"),
        # 模板 {{template}} 或 {{:lang:template}}
        "template": re.compile(r"\{\{(?P<content>.*?)\}\}"),
        "template_colon": re.compile(r":\s*(?P<lang>[a-zA-Z0-9\-]+):(?P<template>.*)"),
    }

    usage_instructions = """维基百科链接与摘要生成器使用方法：
1. 基本格式：
   - [[关键词]] —— 中文维基百科链接并输出第一段摘要
   - [[:语言:关键词]] —— 指定语言链接并输出摘要
   - {{模板名}} —— 中文模板链接并输出摘要
   - {{:语言:模板名}} —— 指定语言模板链接并输出摘要

2. 管理员命令：
   - !wiki撤回 —— 撤回机器人最后一条维基消息

示例：
- [[Python]]
- [[:en:Python]]"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 存储机器人发送的消息ID和内容
        self.sent_messages = {}
        self.message_contents = {}

    def parse_raw_message(self, raw: str) -> str:
        raw = html.unescape(raw)
        if not raw.lstrip().startswith("[{"):
            return raw
        try:
            parsed = ast.literal_eval(raw)
            if not isinstance(parsed, list):
                return str(parsed)
            return "".join(
                el.get("data", {}).get("text", "")
                if isinstance(el, dict) and el.get("type") == "text"
                else str(el)
                for el in parsed
            )
        except Exception:
            return raw

    def build_wiki_url(self, text: str) -> (str, str):
        """
        返回 (语言, 完整URL)
        """
        if m := self.REGEX_PATTERNS["lang"].search(text):
            lang = m.group("lang").strip()
            entry = m.group("entry").strip().replace(" ", "_")
            url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(entry)}"
            return lang, url

        if m := self.REGEX_PATTERNS["wiki"].search(text):
            lang, entry = "zh", m.group("content").strip().replace(" ", "_")
            url = f"https://zh.wikipedia.org/wiki/{urllib.parse.quote(entry)}"
            return lang, url

        if m := self.REGEX_PATTERNS["template"].search(text):
            content = m.group("content").strip()
            if c := self.REGEX_PATTERNS["template_colon"].search(content):
                lang = c.group("lang").strip()
                tpl = c.group("template").strip().replace(" ", "_")
                url = f"https://{lang}.wikipedia.org/wiki/Template:{urllib.parse.quote(tpl)}"
                return lang, url
            tpl = content.replace(" ", "_")
            return "zh", f"https://zh.wikipedia.org/wiki/Template:{urllib.parse.quote(tpl)}"

        return "", ""

    async def fetch_intro(self, lang: str, entry: str) -> str:
        """
        使用 wikipedia 库获取摘要，若为消歧义页则列出所有候选
        """
        try:
            wikipedia.set_lang(lang)
            full_summary = wikipedia.summary(entry).strip()
            if not full_summary:
                return "未找到摘要内容"

            full_summary = re.sub(r'==+\s*(.*?)\s*==+', '', full_summary)
            sentence_pattern = re.compile(r'(?<!\bSt)(?<!\bMr)(?<!\bDr)(?<!\bMs)(?<!\bMrs)(?<!\bJr)(?<!\bSr)(?<!\bInc)(?<!\bLtd)(?<!\bCo)[。.!?！？](?=\s|\n|$)')
            match = sentence_pattern.search(full_summary)
            if match:
                summary = full_summary[: match.end()].strip()
            else:
                paragraphs = full_summary.split('\n\n')
                summary = paragraphs[0].strip() if paragraphs and paragraphs[0] else full_summary

            for word in SENSITIVE_WORDS:
                if word.lower() in summary.lower():
                    return "内容包含敏感词，已被过滤。"
            return summary
        except DisambiguationError as e:
            if hasattr(e, 'options') and e.options:
                options = "\n".join(f"- {opt}" for opt in e.options[:10])
                return f"该条目为消歧义页，请选择具体条目：\n{options}"
            return "该条目为消歧义页，但未能获取候选项列表。"
        except PageError:
            return "未找到相关条目"
        except Exception as e:
            return f"获取摘要时出错: {e}"

    async def is_admin_or_owner(self, group_id, user_id):
        try:
            group_member_info = await self.api.get_group_member_info(
                group_id=group_id,
                user_id=user_id,
                no_cache=True
            )
            role = group_member_info["data"].get("role", "") if group_member_info else ""
            return role in ["owner", "admin"]
        except Exception:
            return False

    @bot.group_event()
    async def handle_wiki_link(self, msg: GroupMessage):
        text = self.parse_raw_message(msg.raw_message)
        if text.startswith("!wiki撤回"):
            if not await self.is_admin_or_owner(msg.group_id, msg.user_id):
                await self.api.post_group_msg(
                    group_id=msg.group_id,
                    text="只有群主或管理员可以执行此命令"
                )
                return

            if msg.group_id in self.sent_messages and self.sent_messages[msg.group_id]:
                last_message_id = self.sent_messages[msg.group_id].pop()
                try:
                    await self.api.delete_msg(last_message_id)
                    await self.api.post_group_msg(group_id=msg.group_id, text=f"已撤回最后一条维基消息")
                except Exception as e:
                    await self.api.post_group_msg(
                        group_id=msg.group_id,
                        text=f"撤回消息失败: {str(e)}"
                    )
            else:
                await self.api.post_group_msg(group_id=msg.group_id, text="没有可撤回的消息")
            return

        match_texts = []
        wiki_matches = set()
        for pattern_name in ["wiki", "lang", "template"]:
            for match in self.REGEX_PATTERNS[pattern_name].finditer(text):
                if pattern_name == "wiki":
                    content = match.group("content").strip()
                    match_texts.append(content)
                    wiki_matches.add((content, "zh"))
                elif pattern_name == "lang":
                    lang = match.group("lang").strip()
                    entry = match.group("entry").strip()
                    match_texts.append(entry)
                    wiki_matches.add((entry, lang))
                elif pattern_name == "template":
                    content = match.group("content").strip()
                    if c := self.REGEX_PATTERNS["template_colon"].search(content):
                        lang = c.group("lang").strip()
                        template = c.group("template").strip()
                        match_texts.append(template)
                        wiki_matches.add((template, lang))
                    else:
                        match_texts.append(content)
                        wiki_matches.add((content, "zh"))

        for txt in match_texts:
            for word in SENSITIVE_WORDS:
                if word.lower() in txt.lower():
                    await self.api.delete_msg(msg.message_id)
                    await self.api.post_group_msg(
                        group_id=msg.group_id,
                        text=f"检测到违禁词，已撤回消息并对用户禁言10分钟。"
                    )
                    await self.api.set_group_ban(group_id=msg.group_id, user_id=msg.user_id, duration=600)
                    return

        if not wiki_matches:
            return

        for entry, lang in wiki_matches:
            if lang == "zh":
                url = f"https://zh.wikipedia.org/wiki/{urllib.parse.quote(entry.replace(' ', '_'))}"
            else:
                url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(entry.replace(' ', '_'))}"

            intro = await self.fetch_intro(lang, entry)
            
            if intro == "内容包含敏感词，已被过滤。":
                await self.api.delete_msg(msg.message_id)
                return
            
            reply = f"{url}\n\n{intro}" if intro else url

            is_sensitive = False
            for word in SENSITIVE_WORDS:
                if word.lower() in reply.lower():
                    is_sensitive = True
                    break

            if is_sensitive:
                await self.api.post_group_msg(
                    group_id=msg.group_id,
                    text=f"该条目内容包含敏感词，已被过滤。"
                )
                continue

            try:
                result = await self.api.post_group_msg(group_id=msg.group_id, text=reply)
                data = result.get("data") or {}
                message_id = data.get("message_id")
                if message_id:
                    self.sent_messages.setdefault(msg.group_id, []).append(message_id)
                    self.message_contents[message_id] = reply
                    if len(self.sent_messages[msg.group_id]) > 20:
                        oldest_id = self.sent_messages[msg.group_id].pop(0)
                        self.message_contents.pop(oldest_id, None)
            except Exception as e:
                error = f"生成维基摘要时出错：{e}\n\n{self.usage_instructions}"
                await self.api.post_group_msg(group_id=msg.group_id, text=error)

    async def on_load(self):
        print(f"{self.name} 插件已加载，版本 {self.version}")

    async def on_unload(self):
        print(f"{self.name} 插件已卸载")
