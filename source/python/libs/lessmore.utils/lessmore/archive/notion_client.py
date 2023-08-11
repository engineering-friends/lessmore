from typing import *

from loguru import logger
from notion_client import Client


# todo later: подгружать или не подгружать обратные ссылки связей (relations) [@marklidenberg]

NOTION_PROPERTY_TYPES = [
    "title",
    "rich_text",
    "select",
    "checkbox",
    "multi_select",
    "number",
    "date",
    "created_by",
    "last_edited_by",
    "last_edited_time",
    "relation",
]


class NotionSimpleClient:
    def __init__(
        self,
        token: str,
    ) -> None:
        self.token = token
        self.client = Client(auth=self.token)

    def get_database_pages(self, database_id: str) -> List:
        """Забираем в исходном формате Notion API записи из базы данных Notion

        Пример выходных данных:
        >>> [ { "object": "page", "id": "ef981df9-0bd1-4c40-994d-bba7772a5ffb", "created_time": "2023-01-24T17:17:00.000Z", "last_edited_time": "2023-01-27T10:15:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "cover": None, "icon": None, "parent": {"type": "database_id", "database_id": "02dcbd52-7c89-4225-ba5c-bde4d7f24c8a"}, "archived": False, "properties": { "Last edited time": { "id": "%3B%3BQ%3E", "type": "last_edited_time", "last_edited_time": "2023-01-27T10:15:00.000Z", }, "data_lag": {"id": "SIeq", "type": "relation", "relation": [], "has_more": False}, "Alerts": {"id": "a%3AUh", "type": "relation", "relation": [], "has_more": False}, "weekly_average": { "id": "sBDA", "type": "relation", "relation": [{"id": "f0850215-2042-45ec-b880-875ea3aed5fc"}], "has_more": False, }, "Created by": { "id": "vBnD", "type": "created_by", "created_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", "name": "Никита polorad", "avatar_url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/a027e378-157c-40df-b3ec-c08348cbc382/Tails.png", "type": "person", "person": {"email": "polorad@deeplay.io"}, }, }, "responsible": {"id": "~L%3CD", "type": "relation", "relation": [], "has_more": False}, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "weekly_average: orrr.games_noneco-0.8-3-StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "weekly_average: orrr.games_noneco-0.8-3-StartedDateTime", "href": None, } ], }, }, "url": "https://www.notion.so/weekly_average-orrr-games_noneco-0-8-3-StartedDateTime-ef981df90bd14c40994dbba7772a5ffb", }, {...} ]
        """

        # - Init

        next_cursor = None
        database_pages = []
        is_has_more = True

        # - Get data from notion

        while is_has_more:
            response = self.client.databases.query(
                database_id=database_id,
                next_cursor=next_cursor,
            )

            if not isinstance(response, dict) and "results" not in response:
                raise Exception(f"Empty response from '{database_id = }'")

            database_pages.extend(response["results"])

            next_cursor = response["next_cursor"]
            is_has_more = response["has_more"]

        return database_pages

    def get_notion_property_value(self, type_, property_):
        """Забираем значение свойства Notion объекта"""
        if type_ == "rich_text":
            if not property_["rich_text"]:
                return ""
            return "".join([value["plain_text"] for value in property_["rich_text"]])
        elif type_ == "select":
            if not property_["select"]:
                return ""
            return property_["select"]["name"]
        elif type_ == "checkbox":
            return property_["checkbox"]
        elif type_ == "multi_select":
            return [value["name"] for value in property_["multi_select"]]
        elif type_ == "title":
            if not property_["title"]:
                return ""
            return "".join([value["plain_text"] for value in property_["title"]])
        elif type_ == "created_by":
            return property_["created_by"]["name"]
        elif type_ == "last_edited_time":
            return property_["last_edited_time"]
        elif type_ == "number":
            return property_["number"]
        elif type_ == "relation":
            return property_["relation"]  # [{"id": ...}, ...]

    def enrich_notion_object(self, notion_object, page_id_to_page: Optional[dict] = None):
        """Обогащаем Notion объект.

        - Рекурсивно скачиваем зависимости (relation) и добавляем к объекту
        - Рекурсивно к каждому Notion объекту добавляем "value"

        Пример выходных данных:
        >>> [ { "object": "page", "id": "ef981df9-0bd1-4c40-994d-bba7772a5ffb", "created_time": "2023-01-24T17:17:00.000Z", "last_edited_time": "2023-01-27T10:15:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "cover": None, "icon": None, "parent": {"type": "database_id", "database_id": "02dcbd52-7c89-4225-ba5c-bde4d7f24c8a"}, "archived": False, "properties": { "Last edited time": { "id": "%3B%3BQ%3E", "type": "last_edited_time", "last_edited_time": "2023-01-27T10:15:00.000Z", "value": "2023-01-27T10:15:00.000Z", }, "data_lag": {"id": "SIeq", "type": "relation", "relation": [], "has_more": False, "value": []}, "Alerts": {"id": "a%3AUh", "type": "relation", "relation": [], "has_more": False, "value": []}, "weekly_average": { "id": "sBDA", "type": "relation", "relation": [ { "object": "page", "id": "f0850215-2042-45ec-b880-875ea3aed5fc", "created_time": "2023-01-24T18:33:00.000Z", "last_edited_time": "2023-01-26T15:27:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": {"object": "user", "id": "d6221771-d12f-4f13-95a8-5d952ea5f963"}, "cover": None, "icon": None, "parent": {"type": "database_id", "database_id": "9494600a-cba1-4f32-9170-5d857b3646a0"}, "archived": False, "properties": { "time_column": { "id": "%3DkAx", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "StartedDateTime", "href": None, } ], "value": "StartedDateTime", }, "dataset1": { "id": "_Xlz", "type": "relation", "relation": [ { "object": "page", "id": "29c8366b-595e-4a26-8fae-24830ec5b85d", "created_time": "2023-01-24T08:14:00.000Z", "last_edited_time": "2023-01-24T08:14:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", }, "cover": None, "icon": None, "parent": { "type": "database_id", "database_id": "00466865-877d-43cc-b83d-20fce17a3f49", }, "archived": False, "properties": { "update": { "id": "%3F%7D%7CW", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "Live", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "Live", "href": None, } ], "value": "Live", }, "weekly_average": { "id": "aYav", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "guarantees": { "id": "cLGL", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "1 hour", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "1 hour", "href": None, } ], "value": "1 hour", }, "data_lag": { "id": "rbd%3E", "type": "relation", "relation": [], "has_more": False, "value": [], }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "", "href": None, }, { "type": "text", "text": {"content": "orrr.games_noneco", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": True, "color": "default", }, "plain_text": "orrr.games_noneco", "href": None, }, ], "value": "orrr.games_noneco", }, }, "url": "https://www.notion.so/orrr-games_noneco-29c8366b595e4a268fae24830ec5b85d", } ], "has_more": False, "value": [ { "object": "page", "id": "29c8366b-595e-4a26-8fae-24830ec5b85d", "created_time": "2023-01-24T08:14:00.000Z", "last_edited_time": "2023-01-24T08:14:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", }, "cover": None, "icon": None, "parent": { "type": "database_id", "database_id": "00466865-877d-43cc-b83d-20fce17a3f49", }, "archived": False, "properties": { "update": { "id": "%3F%7D%7CW", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "Live", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "Live", "href": None, } ], "value": "Live", }, "weekly_average": { "id": "aYav", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "guarantees": { "id": "cLGL", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "1 hour", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "1 hour", "href": None, } ], "value": "1 hour", }, "data_lag": { "id": "rbd%3E", "type": "relation", "relation": [], "has_more": False, "value": [], }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "", "href": None, }, { "type": "text", "text": {"content": "orrr.games_noneco", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": True, "color": "default", }, "plain_text": "orrr.games_noneco", "href": None, }, ], "value": "orrr.games_noneco", }, }, "url": "https://www.notion.so/orrr-games_noneco-29c8366b595e4a268fae24830ec5b85d", } ], }, "Дата чеки": { "id": "d%3CXa", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "last_edited_time": { "id": "e%7Dje", "type": "last_edited_time", "last_edited_time": "2023-01-26T15:27:00.000Z", "value": "2023-01-26T15:27:00.000Z", }, "border": { "id": "nd%3C%60", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "0.8", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "0.8", "href": None, } ], "value": "0.8", }, "day_to_continue": { "id": "~aVg", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "3", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "3", "href": None, } ], "value": "3", }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "orrr.games_noneco-0.8-3-StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "orrr.games_noneco-0.8-3-StartedDateTime", "href": None, } ], "value": "orrr.games_noneco-0.8-3-StartedDateTime", }, }, "url": "https://www.notion.so/orrr-games_noneco-0-8-3-StartedDateTime-f0850215204245ecb880875ea3aed5fc", } ], "has_more": False, "value": [ { "object": "page", "id": "f0850215-2042-45ec-b880-875ea3aed5fc", "created_time": "2023-01-24T18:33:00.000Z", "last_edited_time": "2023-01-26T15:27:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": {"object": "user", "id": "d6221771-d12f-4f13-95a8-5d952ea5f963"}, "cover": None, "icon": None, "parent": {"type": "database_id", "database_id": "9494600a-cba1-4f32-9170-5d857b3646a0"}, "archived": False, "properties": { "time_column": { "id": "%3DkAx", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "StartedDateTime", "href": None, } ], "value": "StartedDateTime", }, "dataset1": { "id": "_Xlz", "type": "relation", "relation": [ { "object": "page", "id": "29c8366b-595e-4a26-8fae-24830ec5b85d", "created_time": "2023-01-24T08:14:00.000Z", "last_edited_time": "2023-01-24T08:14:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", }, "cover": None, "icon": None, "parent": { "type": "database_id", "database_id": "00466865-877d-43cc-b83d-20fce17a3f49", }, "archived": False, "properties": { "update": { "id": "%3F%7D%7CW", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "Live", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "Live", "href": None, } ], "value": "Live", }, "weekly_average": { "id": "aYav", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "guarantees": { "id": "cLGL", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "1 hour", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "1 hour", "href": None, } ], "value": "1 hour", }, "data_lag": { "id": "rbd%3E", "type": "relation", "relation": [], "has_more": False, "value": [], }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "", "href": None, }, { "type": "text", "text": {"content": "orrr.games_noneco", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": True, "color": "default", }, "plain_text": "orrr.games_noneco", "href": None, }, ], "value": "orrr.games_noneco", }, }, "url": "https://www.notion.so/orrr-games_noneco-29c8366b595e4a268fae24830ec5b85d", } ], "has_more": False, "value": [ { "object": "page", "id": "29c8366b-595e-4a26-8fae-24830ec5b85d", "created_time": "2023-01-24T08:14:00.000Z", "last_edited_time": "2023-01-24T08:14:00.000Z", "created_by": {"object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845"}, "last_edited_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", }, "cover": None, "icon": None, "parent": { "type": "database_id", "database_id": "00466865-877d-43cc-b83d-20fce17a3f49", }, "archived": False, "properties": { "update": { "id": "%3F%7D%7CW", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "Live", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "Live", "href": None, } ], "value": "Live", }, "weekly_average": { "id": "aYav", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "guarantees": { "id": "cLGL", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "1 hour", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "1 hour", "href": None, } ], "value": "1 hour", }, "data_lag": { "id": "rbd%3E", "type": "relation", "relation": [], "has_more": False, "value": [], }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "", "href": None, }, { "type": "text", "text": {"content": "orrr.games_noneco", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": True, "color": "default", }, "plain_text": "orrr.games_noneco", "href": None, }, ], "value": "orrr.games_noneco", }, }, "url": "https://www.notion.so/orrr-games_noneco-29c8366b595e4a268fae24830ec5b85d", } ], }, "Дата чеки": { "id": "d%3CXa", "type": "relation", "relation": [{...}], "has_more": False, "value": [{...}], }, "last_edited_time": { "id": "e%7Dje", "type": "last_edited_time", "last_edited_time": "2023-01-26T15:27:00.000Z", "value": "2023-01-26T15:27:00.000Z", }, "border": { "id": "nd%3C%60", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "0.8", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "0.8", "href": None, } ], "value": "0.8", }, "day_to_continue": { "id": "~aVg", "type": "rich_text", "rich_text": [ { "type": "text", "text": {"content": "3", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "3", "href": None, } ], "value": "3", }, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "orrr.games_noneco-0.8-3-StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "orrr.games_noneco-0.8-3-StartedDateTime", "href": None, } ], "value": "orrr.games_noneco-0.8-3-StartedDateTime", }, }, "url": "https://www.notion.so/orrr-games_noneco-0-8-3-StartedDateTime-f0850215204245ecb880875ea3aed5fc", } ], }, "Created by": { "id": "vBnD", "type": "created_by", "created_by": { "object": "user", "id": "a787e8ce-dddc-461d-a236-c3232684e845", "name": "Никита polorad", "avatar_url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/a027e378-157c-40df-b3ec-c08348cbc382/Tails.png", "type": "person", "person": {"email": "polorad@deeplay.io"}, }, "value": "Никита polorad", }, "responsible": {"id": "~L%3CD", "type": "relation", "relation": [], "has_more": False, "value": []}, "name": { "id": "title", "type": "title", "title": [ { "type": "text", "text": {"content": "weekly_average: orrr.games_noneco-0.8-3-StartedDateTime", "link": None}, "annotations": { "bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default", }, "plain_text": "weekly_average: orrr.games_noneco-0.8-3-StartedDateTime", "href": None, } ], "value": "weekly_average: orrr.games_noneco-0.8-3-StartedDateTime", }, }, "url": "https://www.notion.so/weekly_average-orrr-games_noneco-0-8-3-StartedDateTime-ef981df90bd14c40994dbba7772a5ffb", }, {...} ]
        """

        # - Инициируем аргументы

        if page_id_to_page is None:
            page_id_to_page = {}

        if isinstance(notion_object, list):
            return [self.enrich_notion_object(value, page_id_to_page=page_id_to_page) for value in notion_object]

        elif isinstance(notion_object, dict):
            # - Извлекаем страницу

            is_page = notion_object.get("object") == "page" or list(notion_object.keys()) == [
                "id"
            ]  # {"object": "page", ...} or {"id": ...}

            if not is_page:
                # - Применяем рекурсию

                return {
                    key: self.enrich_notion_object(value, page_id_to_page=page_id_to_page)
                    for key, value in notion_object.items()
                }

            else:
                page_id = notion_object["id"]

                # - Возвращяем страницу если она уже имеется в сохраненных

                if page_id in page_id_to_page.keys():
                    return page_id_to_page[page_id]

                logger.info(f"Retrieving page {page_id}", page_id=page_id)
                page = self.client.pages.retrieve(page_id=page_id)

                # - Проверка на корректную страницу

                assert isinstance(page, dict), f"Wrong response for '{page_id = }'"
                assert "properties" in page, f"Empty properties for '{page_id = }'"

                # - Сохраняем страницу

                page_id_to_page[page["id"]] = page

                # - Обогащаем

                for key, property_ in page["properties"].items():
                    property_["value"] = self.get_notion_property_value(type_=property_["type"], property_=property_)

                page["properties"] = self.enrich_notion_object(page["properties"], page_id_to_page=page_id_to_page)

                return page
        else:
            return notion_object

    def simplify_notion_object(self, notion_object: Any) -> Any:
        """Упрощаем Notion объект. Вместо словаря с набором значений каждое свойство будет иметь только своё текстовое значение

        Пример выходных данных:
        >>> [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:27:00.000Z", "__id": "8c6d204d-c9a5-4399-a98b-9cf41d3ffab2", "__url": "https://www.notion.so/data_lag-orrr-games-24-RowCreatedAt-8c6d204dc9a54399a98b9cf41d3ffab2", "Last edited time": "2023-01-26T15:27:00.000Z", "data_lag": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:27:00.000Z", "__id": "9a0ecaab-f493-4d4d-85d2-285029f020bc", "__url": "https://www.notion.so/orrr-games-24-RowCreatedAt-9a0ecaabf4934d4d85d2285029f020bc", "time_column": "RowCreatedAt", "dataset1": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-25T11:09:00.000Z", "__id": "faa85d1f-b1a7-4da0-ac2f-810e058297e9", "__url": "https://www.notion.so/orrr-games-faa85d1fb1a74da0ac2f810e058297e9", "update": "Live", "weekly_average": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:28:00.000Z", "__id": "624fc306-40f0-4825-bd28-e6b6a610c6e2", "__url": "https://www.notion.so/orrr-games-0-8-3-StartedDateTime-624fc30640f04825bd28e6b6a610c6e2", "time_column": "StartedDateTime", "dataset1": [{...}], "Дата чеки": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-27T10:16:00.000Z", "__id": "d6e1b6ed-1f50-4ede-9ee8-9a9bf3cd0bcf", "__url": "https://www.notion.so/weekly_average-orrr-games-0-8-3-StartedDateTime-d6e1b6ed1f504ede9ee89a9bf3cd0bcf", "Last edited time": "2023-01-27T10:16:00.000Z", "data_lag": [], "Alerts": [ { "__created_time": "2023-01-18T11:08:00.000Z", "__last_edited_time": "2023-01-26T15:29:00.000Z", "__id": "c8b97ec9-201b-4f51-a001-2cf6bf9f2f54", "__url": "https://www.notion.so/orrr-games-c8b97ec9201b4f51a0012cf6bf9f2f54", "priority": "🟠", "data_checks": [{...}, {...}], "group": "ETL-Python", "mentions": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "active": { "id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None, }, "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "Среднее за неделю orrr.games", }, { "__created_time": "2023-01-24T15:57:00.000Z", "__last_edited_time": "2023-01-27T09:56:00.000Z", "__id": "9d095e0d-6af2-4ebd-b0f5-5003ea4993e4", "__url": "https://www.notion.so/orrr-games-9d095e0d6af24ebdb0f55003ea4993e4", "priority": "🟡", "data_checks": [{...}], "group": "ETL-Python", "mentions": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "active": { "id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None, }, "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "Среднее за неделю orrr.games для Сани", }, ], "weekly_average": [{...}], "Created by": "Mark Lessmore", "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "weekly_average: orrr.games-0.8-3-StartedDateTime", } ], "last_edited_time": "2023-01-26T15:28:00.000Z", "border": "0.8", "day_to_continue": "3", "name": "orrr.games-0.8-3-StartedDateTime", } ], "guarantees": "1 hour", "data_lag": [{...}], "name": "orrr.games", } ], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:27:00.000Z", "max_hour_lag": "24", "name": "orrr.games-24-RowCreatedAt", } ], "Alerts": [ { "__created_time": "2023-01-18T11:08:00.000Z", "__last_edited_time": "2023-01-26T15:29:00.000Z", "__id": "c8b97ec9-201b-4f51-a001-2cf6bf9f2f54", "__url": "https://www.notion.so/orrr-games-c8b97ec9201b4f51a0012cf6bf9f2f54", "priority": "🟠", "data_checks": [ {...}, { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-27T10:16:00.000Z", "__id": "d6e1b6ed-1f50-4ede-9ee8-9a9bf3cd0bcf", "__url": "https://www.notion.so/weekly_average-orrr-games-0-8-3-StartedDateTime-d6e1b6ed1f504ede9ee89a9bf3cd0bcf", "Last edited time": "2023-01-27T10:16:00.000Z", "data_lag": [], "Alerts": [ {...}, { "__created_time": "2023-01-24T15:57:00.000Z", "__last_edited_time": "2023-01-27T09:56:00.000Z", "__id": "9d095e0d-6af2-4ebd-b0f5-5003ea4993e4", "__url": "https://www.notion.so/orrr-games-9d095e0d6af24ebdb0f55003ea4993e4", "priority": "🟡", "data_checks": [{...}], "group": "ETL-Python", "mentions": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "active": {"id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None}, "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "Среднее за неделю orrr.games для Сани", }, ], "weekly_average": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:28:00.000Z", "__id": "624fc306-40f0-4825-bd28-e6b6a610c6e2", "__url": "https://www.notion.so/orrr-games-0-8-3-StartedDateTime-624fc30640f04825bd28e6b6a610c6e2", "time_column": "StartedDateTime", "dataset1": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-25T11:09:00.000Z", "__id": "faa85d1f-b1a7-4da0-ac2f-810e058297e9", "__url": "https://www.notion.so/orrr-games-faa85d1fb1a74da0ac2f810e058297e9", "update": "Live", "weekly_average": [{...}], "guarantees": "1 hour", "data_lag": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:27:00.000Z", "__id": "9a0ecaab-f493-4d4d-85d2-285029f020bc", "__url": "https://www.notion.so/orrr-games-24-RowCreatedAt-9a0ecaabf4934d4d85d2285029f020bc", "time_column": "RowCreatedAt", "dataset1": [{...}], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:27:00.000Z", "max_hour_lag": "24", "name": "orrr.games-24-RowCreatedAt", } ], "name": "orrr.games", } ], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:28:00.000Z", "border": "0.8", "day_to_continue": "3", "name": "orrr.games-0.8-3-StartedDateTime", } ], "Created by": "Mark Lessmore", "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [{...}], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "weekly_average: orrr.games-0.8-3-StartedDateTime", }, ], "group": "ETL-Python", "mentions": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-27T10:16:00.000Z", "__id": "d6e1b6ed-1f50-4ede-9ee8-9a9bf3cd0bcf", "__url": "https://www.notion.so/weekly_average-orrr-games-0-8-3-StartedDateTime-d6e1b6ed1f504ede9ee89a9bf3cd0bcf", "Last edited time": "2023-01-27T10:16:00.000Z", "data_lag": [], "Alerts": [ {...}, { "__created_time": "2023-01-24T15:57:00.000Z", "__last_edited_time": "2023-01-27T09:56:00.000Z", "__id": "9d095e0d-6af2-4ebd-b0f5-5003ea4993e4", "__url": "https://www.notion.so/orrr-games-9d095e0d6af24ebdb0f55003ea4993e4", "priority": "🟡", "data_checks": [{...}], "group": "ETL-Python", "mentions": [{...}], "active": {"id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None}, "responsible": [{...}], "name": "Среднее за неделю orrr.games для Сани", }, ], "weekly_average": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:28:00.000Z", "__id": "624fc306-40f0-4825-bd28-e6b6a610c6e2", "__url": "https://www.notion.so/orrr-games-0-8-3-StartedDateTime-624fc30640f04825bd28e6b6a610c6e2", "time_column": "StartedDateTime", "dataset1": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-25T11:09:00.000Z", "__id": "faa85d1f-b1a7-4da0-ac2f-810e058297e9", "__url": "https://www.notion.so/orrr-games-faa85d1fb1a74da0ac2f810e058297e9", "update": "Live", "weekly_average": [{...}], "guarantees": "1 hour", "data_lag": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:27:00.000Z", "__id": "9a0ecaab-f493-4d4d-85d2-285029f020bc", "__url": "https://www.notion.so/orrr-games-24-RowCreatedAt-9a0ecaabf4934d4d85d2285029f020bc", "time_column": "RowCreatedAt", "dataset1": [{...}], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:27:00.000Z", "max_hour_lag": "24", "name": "orrr.games-24-RowCreatedAt", } ], "name": "orrr.games", } ], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:28:00.000Z", "border": "0.8", "day_to_continue": "3", "name": "orrr.games-0.8-3-StartedDateTime", } ], "Created by": "Mark Lessmore", "responsible": [{...}], "name": "weekly_average: orrr.games-0.8-3-StartedDateTime", } ], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "active": {"id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None}, "responsible": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-24T09:10:00.000Z", "__id": "21c515d0-cd8f-4b71-a469-47d0c6601d9a", "__url": "https://www.notion.so/Polorad-21c515d0cd8f4b71a46947d0c6601d9a", "Phone": "", "Дата чеки": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-27T10:16:00.000Z", "__id": "d6e1b6ed-1f50-4ede-9ee8-9a9bf3cd0bcf", "__url": "https://www.notion.so/weekly_average-orrr-games-0-8-3-StartedDateTime-d6e1b6ed1f504ede9ee89a9bf3cd0bcf", "Last edited time": "2023-01-27T10:16:00.000Z", "data_lag": [], "Alerts": [ {...}, { "__created_time": "2023-01-24T15:57:00.000Z", "__last_edited_time": "2023-01-27T09:56:00.000Z", "__id": "9d095e0d-6af2-4ebd-b0f5-5003ea4993e4", "__url": "https://www.notion.so/orrr-games-9d095e0d6af24ebdb0f55003ea4993e4", "priority": "🟡", "data_checks": [{...}], "group": "ETL-Python", "mentions": [{...}], "active": {"id": "o_Rp", "type": "checkbox", "checkbox": True, "value": None}, "responsible": [{...}], "name": "Среднее за неделю orrr.games для Сани", }, ], "weekly_average": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:28:00.000Z", "__id": "624fc306-40f0-4825-bd28-e6b6a610c6e2", "__url": "https://www.notion.so/orrr-games-0-8-3-StartedDateTime-624fc30640f04825bd28e6b6a610c6e2", "time_column": "StartedDateTime", "dataset1": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-25T11:09:00.000Z", "__id": "faa85d1f-b1a7-4da0-ac2f-810e058297e9", "__url": "https://www.notion.so/orrr-games-faa85d1fb1a74da0ac2f810e058297e9", "update": "Live", "weekly_average": [{...}], "guarantees": "1 hour", "data_lag": [ { "__created_time": "2023-01-17T19:24:00.000Z", "__last_edited_time": "2023-01-26T15:27:00.000Z", "__id": "9a0ecaab-f493-4d4d-85d2-285029f020bc", "__url": "https://www.notion.so/orrr-games-24-RowCreatedAt-9a0ecaabf4934d4d85d2285029f020bc", "time_column": "RowCreatedAt", "dataset1": [{...}], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:27:00.000Z", "max_hour_lag": "24", "name": "orrr.games-24-RowCreatedAt", } ], "name": "orrr.games", } ], "Дата чеки": [{...}], "last_edited_time": "2023-01-26T15:28:00.000Z", "border": "0.8", "day_to_continue": "3", "name": "orrr.games-0.8-3-StartedDateTime", } ], "Created by": "Mark Lessmore", "responsible": [{...}], "name": "weekly_average: orrr.games-0.8-3-StartedDateTime", } ], "slack_username": "@Никита Polorad", "slack_user_id": "U037X5VJJP4", "Related to Алерты (1) (Responsible)": [], "Name": "Никита Polorad", } ], "name": "Среднее за неделю orrr.games", } ], "weekly_average": [], "Created by": "Mark Lessmore", "responsible": [], "name": "data_lag: orrr.games-24-RowCreatedAt", }, {...} ]
        """

        # - Упрощаем

        if isinstance(notion_object, list):
            return [self.simplify_notion_object(value) for value in notion_object]
        elif isinstance(notion_object, dict):
            # - Page

            if "__id" in notion_object:
                # Возвращаем объект если он уже обработан
                return notion_object
            elif "properties" in notion_object:
                # - Удаляем лишние ключи в объекте

                for key in set(notion_object.keys()) - {"created_time", "last_edited_time", "id", "url", "properties"}:
                    notion_object.pop(key, None)

                # - Заполняем системные свойства

                for key in ["created_time", "last_edited_time", "id", "url"]:
                    notion_object[f"__{key}"] = notion_object.pop(key, None)

                # - Заполняем не системные свойства рекурсивно

                notion_object["properties"] = {
                    key: self.simplify_notion_object(value) for key, value in notion_object["properties"].items()
                }

                for key, value in notion_object["properties"].items():
                    notion_object[key] = value

                notion_object.pop("properties")

                return notion_object

            elif "type" in notion_object and notion_object["type"] in NOTION_PROPERTY_TYPES:
                return self.simplify_notion_object(notion_object["value"])
            else:
                return {key: self.simplify_notion_object(value) for key, value in notion_object.items()}

        else:
            return notion_object

    def set_page_text_property(self, page_id: str, property_name: str, property_value: str):
        """Устанавливаем значение текстовому свойству Notion страницы."""

        property_ = {property_name: {"rich_text": [{"type": "text", "text": {"content": property_value}}]}}

        return self.client.pages.update(page_id=page_id, properties=property_)

    def set_page_title(self, page_id: str, title: str):
        """Устанавливаем значение заголовка у страницы Notion"""

        title_object = {"title": [{"type": "text", "text": {"content": f"{title}"}}]}

        return self.client.pages.update(page_id=page_id, properties=title_object)


def test_all():
    # - Init connection data

    database_id = "fb7f9118-ad67-4148-bf22-946b03ec5a30"  # DB only for tests
    NOTION_TOKEN = ""

    # - Init Notion client

    client = NotionSimpleClient(token=NOTION_TOKEN)

    # - Get original pages from Notion database

    pages = client.get_database_pages(database_id=database_id)

    assert "properties" in pages[0], "Page has no properties!"

    # - Get original page from Notion

    page = pages[0]
    page_id = page["id"]

    print("original page from Notion @@@", page)

    # - Transform original Notion page to enriched page

    enriched_page = client.enrich_notion_object(page)

    assert "relation" in enriched_page["properties"]["Related for test db"], "Needed properties has no relation!"

    print("enriched_page from notion @@@", enriched_page)

    # - Transform enriched page to simplified page

    simplified_page = client.simplify_notion_object(enriched_page)

    assert "__id" in simplified_page, "Page has no property '__id'!"
    assert "id" not in simplified_page, "Page has property 'id'!"

    print("simplified_page from notion @@@", simplified_page)

    # - Update data in page in Notion

    update_properties = {
        "name": {"title": [{"type": "text", "text": {"content": f"{simplified_page['second name']}"}}]},
        "second name": {"rich_text": [{"type": "text", "text": {"content": f"{simplified_page['Name']}"}}]},
    }

    updated_page = client.set_page_text_property(page_id=page_id, value=update_properties)

    updated_enriched_page = client.enrich_notion_object(notion_object=updated_page)
    updated_simplified_page = client.simplify_notion_object(notion_object=updated_enriched_page)

    assert updated_simplified_page["name"] == simplified_page["second name"], "Failed to refresh page 'name'!"
    assert updated_simplified_page["second name"] == simplified_page["name"], "Failed to refresh page 'second name'!"

    print("updated_simplified_page from notion @@@", updated_simplified_page)


if __name__ == "__main__":
    test_all()
