""" """

from dataclasses import dataclass
from typing import Any, Callable, Literal

from aiogram.types import InlineKeyboardMarkup
from teletalk.models.block_message import BlockMessage


class SimpleQuery(Block):
    def __init__(self, text: str, buttons: list[Any]):
        self.text = text
        self.buttons = buttons
        self.parent = None
        self.children = []


@dataclass
class Button:
    text: str
    callback: Callable


@dataclass
class User:
    chat_id: str
    followed_posts: list[str]
    last_read_comment_id_by_post_id: dict[str, str]


class Thread(Block):
    def __init__(self, chat_id: str, user: User, post_id: str):
        self.chat_id = chat_id
        self.user = user
        self.post_id = post_id
        self.parent = None
        self.children = []
        self.is_mute = False
        self.is_following = False
        self.tutorial_finished = False

    def render(self, callback_wrapper: Callable) -> BlockMessage:
        # - Get post status

        post_status: Literal["read", "unread"] = "unread"

        # - Get comments for the post

        # - Render the block

        return SimpleQuery(
            text="""
                                [🔕+5]: Название поста (ссылкой)
                                
                                Andrew Tropin: Привет, я тут Андрей Тропин. Я помогу вам с вашими запросами и ответами. Если у вас есть какие-то вопросы, не стесняйтесь спрашивать.
                                
                                """,
            buttons=[
                Button(
                    text="🔔Размьютить",
                    callback=lambda response: (response.prompt_block.is_mute, response.ask(response.root)),
                ),
                Button(
                    text="⌫ Отписаться",
                    callback=lambda response: (response.prompt_block.is_following, response.ask(response.root)),
                ),
            ],
        ).render(callback_wrapper)


# here we run page: one query is multiple queries per thread
# Обучение
# - Кидает ссылку на тестовый пост
# - После коммента появится тред и удаляться сообщения с посылом оставить комментарий
