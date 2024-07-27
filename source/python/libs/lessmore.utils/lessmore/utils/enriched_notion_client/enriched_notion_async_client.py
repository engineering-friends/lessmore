import asyncio
import re

from typing import Callable, Optional

from loguru import logger
from more_itertools import first, only
from notion_client import AsyncClient

from lessmore.utils.enriched_notion_client.test_paginated_request import test_paginated_request
from lessmore.utils.enriched_notion_client.test_parse_markdown_table import test_parse_markdown_table
from lessmore.utils.enriched_notion_client.test_plainify_database_property import test_plainify_database_property
from lessmore.utils.enriched_notion_client.test_upsert_database import test_upsert_database
from lessmore.utils.enriched_notion_client.test_upsert_page import test_upsert_page
from lessmore.utils.functional.contains_nested import contains_nested
from lessmore.utils.functional.dict.drop import drop
from lessmore.utils.tested import tested


class EnrichedNotionAsyncClient(AsyncClient):
    @staticmethod
    @tested(tests=[test_paginated_request])
    async def get_paginated_request(method, method_kwargs):
        # - Init

        result = []
        start_cursor = None
        has_more = True

        # - Get data from notion

        while has_more:
            response = await method(start_cursor=start_cursor, **method_kwargs)
            result.extend(response["results"])
            start_cursor = response["next_cursor"]
            has_more = response["has_more"]

        return result

    @tested(tests=[test_upsert_page])
    async def upsert_page(
        self,
        page: Optional[dict] = None,
        old_page: Optional[dict] = None,
        children: Optional[list] = None,
    ):
        # - Prepare kwargs

        # Note: it's very important to filter None values, or Notion will throw an ambiguous error
        page = {k: v for k, v in page.items() if v is not None}

        # - If not page_id: create page

        if "id" not in page:
            # - Create page

            logger.debug("Creating page", page=page)

            assert page.get("parent") is not None, "Parent is required to create a new page"

            page = await self.pages.create(**drop(page, ["id"]))

            # - Update children

            if children is not None:
                await self.blocks.children.append(block_id=page["id"], children=children)

            # - Return page

            return page

        assert "id" in page

        # - Update children if needed

        if children is not None:
            logger.debug("Get children", page=page)

            # - Get old children

            old_children = await self.get_paginated_request(
                method=self.blocks.children.list,
                method_kwargs=dict(block_id=page["id"]),
            )

            # - Update children if needed

            if not contains_nested(whole=old_children, part=children):
                logger.debug("Updating children", page=page)

                # - Delete old children

                for child in old_children:
                    try:
                        await self.blocks.delete(block_id=child["id"])
                    except Exception as e:
                        logger.error("Failed to delete child", child=child, error=e)

                # - Create new children

                await self.blocks.children.append(block_id=page["id"], children=children)

        # - Return if no update needed for properties and stuff

        if not drop(page, ["id"]):
            return old_page

        # - Update page

        # -- If old page provided - check if nothing has changed (to avoid unnecessary requests)

        if old_page and contains_nested(whole=old_page, part=page):
            return old_page

        # -- Update page

        logger.debug("Updating page", page=page)

        return await self.pages.update(page_id=page["id"], **drop(page, ["id"]))

    @tested(tests=[test_upsert_database])
    async def upsert_database(
        self,
        database: Optional[dict] = None,
        pages: list[dict] = [],
        children_list: Optional[list[list[dict]]] = None,
        remove_others: bool = False,
        page_unique_id_func: Optional[Callable] = None,
        archive: Optional[bool] = None,
    ):
        # - Validate pages has the same length as children

        if children_list is not None:
            assert len(pages) == len(children_list), "Pages and children_list should have the same length"

        # - If archived - just archive

        if archive is not None:
            assert "id" in database, "Database id is required to archive it"
            return await self.blocks.update(block_id=database["id"], archived=True)

        # - Prepare kwargs

        database = {k: v for k, v in database.items() if v is not None}

        # - Create database if not exists

        if "id" not in database:
            logger.debug("Creating new database", database=database)

            database = await self.databases.create(**database)
            database_id = database["id"]

            if pages:
                await asyncio.gather(
                    *[self.upsert_page(page={**{"database_id": database_id}, **page}) for page in pages]
                )

            return database

        assert "id" in database

        # - Update metadata first

        if drop(database, ["id"]):
            # - Update database

            logger.info("Updating database", database_id=database, database=database)

            database = await self.databases.update(database_id=database["id"], **drop(database, ["id"]))
        else:
            # - Just retrieve database

            database = await self.databases.retrieve(database_id=database["id"])

        # - Update pages

        # -- Return if no pages provided

        if not pages:
            return database

        # - -- Get old pages

        old_pages = await self.get_paginated_request(
            method=self.databases.query,
            method_kwargs=dict(database_id=database["id"]),
        )

        # -- Find correct page_id for each page

        if page_unique_id_func:
            # - Set _unique_id

            for page in old_pages + pages:
                page["_unique_id"] = page_unique_id_func(page)

            # - Set page id for matching _unique_id

            for page in pages:
                # todo maybe: should be only here, but sometimes if fails for some reason [@marklidenberg]
                old_page = first(
                    [old_page for old_page in old_pages if old_page["_unique_id"] == page["_unique_id"]], default=None
                )
                if old_page:
                    page["id"] = old_page["id"]

            # - Remove _unique_id

            for page in old_pages + pages:
                del page["_unique_id"]

        # -- Remove pages if needed

        if remove_others:
            to_remove = [page for page in old_pages if page["id"] not in [page.get("id") for page in pages]]

            logger.debug("Removing pages", n_pages=len(to_remove))

            await asyncio.gather(*[self.upsert_page(page={"id": page["id"], "archived": True}) for page in to_remove])

        # -- Create or update new pages

        logger.debug(
            "Upserting pages",
            pages=[
                {
                    "database_id": database["id"],
                    **page,
                }
                for page in pages
            ],
        )

        await asyncio.gather(
            *[
                self.upsert_page(
                    page={
                        "parent": {"database_id": database["id"]},
                        **page,
                    },
                    old_page=only(
                        [old_page for old_page in old_pages if old_page["id"] == page.get("id")],
                        default=None,
                    ),
                    children=children_list[i] if children_list else None,
                )
                for i, page in enumerate(pages)
            ]
        )

        return database

    @tested(tests=[test_parse_markdown_table])
    @staticmethod
    def parse_markdown_table(markdown_table: str, annotations: Optional[Callable] = None) -> dict:
        """
        Parameters
        ----------
        markdown: str
        | Subject Pronoun | Conjugation |
        | --- | --- |
        | ich (I) |  |
        | du (you, singular informal) |  |
        | er/sie/es (he/she/it) |  |
        | wir (we) |  |
        | ihr (you, plural informal) |  |
        | sie/Sie (they/you, formal) |  |

        annotations: Optional[Callable]
            def annotations(header: str, row: list) -> dict:

        Returns
        -------
        {
        "type": "table",
        "table": {"has_column_header": True, "has_row_header": False, "table_width": 2, "children": [...]}
        }
        """

        def parse_markdown_table(md_table):
            rows = md_table.strip().split("\n")
            header = rows[0]
            delimiter = rows[1]
            data = rows[2:]

            headers = [h.strip() for h in re.split(r"\s*\|\s*", header.strip("|"))]
            table_data = []

            for row in data:
                cells = [cell.strip() for cell in re.split(r"\s*\|\s*", row.strip("|"))]
                table_data.append(cells)

            return headers, table_data

        def create_notion_table(headers, data):
            notion_table = {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": len(headers),
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [],
                },
            }

            # Create header row
            header_row = {
                "type": "table_row",
                "table_row": {"cells": [[{"type": "text", "text": {"content": header}}] for header in headers]},
            }
            notion_table["table"]["children"].append(header_row)

            # Create data rows
            for row in data:
                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                notion_row = {"type": "table_row", "table_row": {"cells": []}}
                for col_index, cell in enumerate(row):
                    cell_content = {"type": "text", "text": {"content": cell}}

                    # Apply annotations if the function is provided and returns non-None
                    if annotations:
                        annotation = annotations(headers[col_index], row_dict)
                        if annotation:
                            cell_content["annotations"] = annotation
                    notion_row["table_row"]["cells"].append([cell_content])
                notion_table["table"]["children"].append(notion_row)

            return notion_table

        headers, data = parse_markdown_table(markdown_table)
        notion_table = create_notion_table(headers, data)
        return notion_table

    @tested(tests=[test_plainify_database_property])
    def plainify_database_property(self, property: dict) -> bool | str | list[str]:
        """
              Parameters
              ----------
              property: dict

                  Examples:
                  {
          "Checkbox": {
            "checkbox": true,
            "id": "x%3AWM",
            "type": "checkbox"
          },
          "Created by": {
            "created_by": {
              "avatar_url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/1cdd4edd-c36c-4707-b2d0-add156945b34/serious.jpeg",
              "id": "bdb47407-ca48-4745-9aff-74763ad1bae0",
              "name": "Mark Lidenberg",
              "object": "user",
              "person": {
                "email": "marklidenberg@gmail.com"
              },
              "type": "person"
            },
            "id": "aXeg",
            "type": "created_by"
          },
          "Created time": {
            "created_time": "2024-07-22T08:56:00.000Z",
            "id": "B%7DsS",
            "type": "created_time"
          },
          "Date": {
            "date": {
              "end": null,
              "start": "2024-07-18",
              "time_zone": null
            },
            "id": "VBT%60",
            "type": "date"
          },
          "Email": {
            "email": "marklidenberg@gmail.com",
            "id": "a%3Azs",
            "type": "email"
          },
          "Files & media": {
            "files": [
              {
                "file": {
                  "expiry_time": "2024-07-22T09:59:08.505Z",
                  "url": "https://prod-files-secure.s3.us-west-2.amazonaws.com/3249c2aa-1717-4003-b846-e9d6eb0fb98f/c4092125-8011-4350-8bfd-bae2f4ff2c52/cover_letter.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45HZZMZUHI%2F20240722%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240722T085908Z&X-Amz-Expires=3600&X-Amz-Signature=7f6cc075cea8f321038c7d0e53d97683a5b4df446e76852e817773049b0e9fe6&X-Amz-SignedHeaders=host&x-id=GetObject"
                },
                "name": "cover_letter.txt",
                "type": "file"
              }
            ],
            "id": "%5BGdh",
            "type": "files"
          },
          "Last edited by": {
            "id": "_fBq",
            "last_edited_by": {
              "avatar_url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/1cdd4edd-c36c-4707-b2d0-add156945b34/serious.jpeg",
              "id": "bdb47407-ca48-4745-9aff-74763ad1bae0",
              "name": "Mark Lidenberg",
              "object": "user",
              "person": {
                "email": "marklidenberg@gmail.com"
              },
              "type": "person"
            },
            "type": "last_edited_by"
          },
          "Last edited time": {
            "id": "e%3Ac%5E",
            "last_edited_time": "2024-07-22T08:58:00.000Z",
            "type": "last_edited_time"
          },
          "Number": {
            "id": "HBvK",
            "number": 3,
            "type": "number"
          },
          "Person": {
            "id": "uB%7C%3B",
            "people": [
              {
                "avatar_url": "https://s3-us-west-2.amazonaws.com/public.notion-static.com/1cdd4edd-c36c-4707-b2d0-add156945b34/serious.jpeg",
                "id": "bdb47407-ca48-4745-9aff-74763ad1bae0",
                "name": "Mark Lidenberg",
                "object": "user",
                "person": {
                  "email": "marklidenberg@gmail.com"
                },
                "type": "person"
              }
            ],
            "type": "people"
          },
          "Phone": {
            "id": "rk%40%7D",
            "phone_number": "+995551185124",
            "type": "phone_number"
          },
          "Select": {
            "id": "%5Eq%3F%3B",
            "select": {
              "color": "red",
              "id": "a7842663-7443-4372-ac1d-60c2a97af7c6",
              "name": "a"
            },
            "type": "select"
          },
          "Status": {
            "id": "Rozo",
            "status": {
              "color": "default",
              "id": "3b0c37fa-905f-4156-a686-9e65aba33efc",
              "name": "Not started"
            },
            "type": "status"
          },
          "URL": {
            "id": "wUQN",
            "type": "url",
            "url": "https://meet.google.com/pth-hmic-wup"
          },
          "multi-select": {
            "id": "Bn%5DR",
            "multi_select": [
              {
                "color": "red",
                "id": "32c2c3d9-04cf-4318-9405-63d622cabc86",
                "name": "a"
              }
            ],
            "type": "multi_select"
          },
          "title": {
            "id": "title",
            "title": [
              {
                "annotations": {
                  "bold": false,
                  "code": false,
                  "color": "default",
                  "italic": false,
                  "strikethrough": false,
                  "underline": false
                },
                "href": null,
                "plain_text": "a",
                "text": {
                  "content": "a",
                  "link": null
                },
                "type": "text"
              }
            ],
            "type": "title"
          }
        }

              Returns
              -------
        """
        if property["type"] == "checkbox":
            return property["checkbox"]
        elif property["type"] == "created_by":
            return property["created_by"]["name"]
        elif property["type"] == "created_time":
            return property["created_time"]
        elif property["type"] == "date":
            if not property["date"]:
                return ""
            return [property["date"]["start"], property["date"].get("end")]
        elif property["type"] == "email":
            return property["email"]
        elif property["type"] == "files":
            return [file["name"] for file in property["files"]]
        elif property["type"] == "last_edited_by":
            return property["last_edited_by"]["name"]
        elif property["type"] == "last_edited_time":
            return property["last_edited_time"]
        elif property["type"] == "number":
            return property["number"]
        elif property["type"] == "phone_number":
            return property["phone_number"]
        elif property["type"] == "select":
            if not property["select"]:
                return ""
            return property["select"].get("name", "")
        elif property["type"] == "status":
            return property["status"]["name"]
        elif property["type"] == "url":
            return property["url"]
        elif property["type"] == "multi_select":
            return [select["name"] for select in property["multi_select"]]
        elif property["type"] == "title":
            return "".join([text["plain_text"] for text in property["title"]])
        elif property["type"] == "rich_text":
            return "".join([text["plain_text"] for text in property["rich_text"]])
        else:
            raise ValueError(f"Unknown property type: {property['type']}")
