from teletalk.models.response import Response


async def mark_text_with_inline_response(response: Response):
    # - Remove inline keyboard buttons + mark text with inline response

    # -- Return if no inline keyboard buttons

    if not any(block.current_output.inline_keyboard_markup for block in response.prompt_page.blocks):
        return

    # -- Keep old values

    old_values = [block.is_inline_keyboard_visible for block in response.prompt_page.blocks]

    # -- Set values to True

    for block in response.prompt_page.blocks:
        block.is_inline_keyboard_visible = False

    # -- If the inline button was pressed - mark text with inline response

    if response.callback_id:
        response.prompt_block.text = f"{response.prompt_block.text} {response.callback_info.callback_text}"

    # -- Update active page again

    await response.tell(response, mode="inplace")

    # -- Restore old values

    for block, old_value in zip(response.prompt_page.blocks, old_values):
        block.is_inline_keyboard_visible = old_value