from typing import Callable

from lessmore.utils.decorators.enable_arguments import enable_arguments
from loguru import logger
from teletalk.blocks.build_default_message_callback import CancelError
from teletalk.models.response import Response


# @enable_arguments
def handle_errors(
    func: Callable,
    error_message: str = "Something went wrong, sorry about that",
):
    async def wrapper(response: Response):
        try:
            return await func(response)
        except CancelError:
            return await response.ask()
        except Exception as e:
            logger.exception("Something went wrong", error=e)
            await response.tell(error_message)
            return await response.ask()

    return wrapper
