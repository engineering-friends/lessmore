from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from teletalk.models.response import Response


async def default_on_response(response: "Response"):
    # - Remove inline keyboard buttons

    # -- Return if no inline keyboard buttons

    if not any(block.current_output.inline_keyboard_markup for block in response.prompt_page.blocks):
        return

    # -- Keep old values

    old_values = [block.is_inline_keyboard_visible for block in response.prompt_page.blocks]

    # -- Set values to True

    for block in response.prompt_page.blocks:
        block.is_inline_keyboard_visible = False

    # -- Update active page again

    await response.tell(response, mode="inplace")

    # -- Restore old values

    for block, old_value in zip(response.prompt_page.blocks, old_values):
        block.is_inline_keyboard_visible = old_value
