from typing import Callable, Optional

from teletalk.models.response import Response


class CancelError(Exception):
    pass


def build_default_message_callback(
    supress_messages: bool = False,
    response_formatter: Optional[Callable] = lambda response: "".join(
        [message.text for message in response.block_messages]
    ),
):
    async def _callback(response: Response):
        if response.block_messages[-1].text == "/cancel":
            raise CancelError("Cancelled")
        elif response.block_messages[-1].text:
            if supress_messages:
                # - Remove response messages # todo later: put into on_response? [@marklidenberg]

                for block_message in response.block_messages:
                    for message in block_message.messages:
                        await response.talk.app.bot.delete_messages(
                            chat_id=response.chat_id,
                            message_ids=[message.message_id],
                        )
                        block_message.messages.remove(message)

                # - Ask again

                return await response.ask(mode="inplace")
            else:
                return response_formatter(response)

    return _callback


default_message_callback = build_default_message_callback(supress_messages=True)
handle_cancel_callback = build_default_message_callback(supress_messages=False)
