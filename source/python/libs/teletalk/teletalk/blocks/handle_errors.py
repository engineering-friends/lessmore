import functools

from typing import Callable

from lessmore.utils.decorators.enable_arguments import enable_arguments
from loguru import logger
from teletalk.blocks.build_default_message_callback import CancelError
from teletalk.models.response import Response


@enable_arguments
def handle_errors(
    func: Callable,
    error_message: str = "Something went wrong, sorry about that",
):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except CancelError:
            # - Get response

            if len(args) >= 2:
                response = args[1]
            else:
                response = kwargs.get("response")

            assert isinstance(response, Response), "response is required"

            # - Go back to the main response

            return await response.ask()

        except Exception as e:
            # - Get response

            if len(args) >= 2:
                response = args[1]
            else:
                response = kwargs.get("response")

            assert isinstance(response, Response), "response is required"

            logger.exception("Something went wrong")

            # - Tell error message if specified

            if error_message:
                await response.tell(error_message)

            # - Go back to the main response

            return await response.ask()

    return wrapper
