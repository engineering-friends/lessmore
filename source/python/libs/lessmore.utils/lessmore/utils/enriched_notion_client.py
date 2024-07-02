from notion_client import Client


class EnrichedNotionClient(Client):
    @staticmethod
    def get_paginated_request(method, **kwargs):
        # - Init

        result = []
        start_cursor = None
        has_more = True

        # - Get data from notion

        while has_more:
            response = method(start_cursor=start_cursor, **kwargs)
            result.extend(response["results"])
            start_cursor = response["next_cursor"]
            has_more = response["has_more"]

        return result


def test():
    from learn_language_magic.deps import Deps

    client = EnrichedNotionClient(
        auth=Deps.load().config.notion_token,
    )
    from lessmore.utils.printy import printy

    # printy(
    #     client.get_paginated_request(
    #         method=client.databases.query,
    #         database_id="a4f6eaf88dbc4402a8232ab56484ee03",
    #     ),
    # )

    printy(client.blocks.children.list(block_id="f19dad84-5aaf-47bf-8a55-6616bec46bf0"))


if __name__ == "__main__":
    test()
