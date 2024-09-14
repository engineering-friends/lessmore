# - `App`

"""

`App` contains current `Talk`s.

Each chat has a focus `Talk`, which is the `Talk` with the latest message. By default, `dispatcher` will send the new message to the focus talk of the chat.

Also, `App` updates the chat `reply_keyboard_markup` to match the focus talk.

"""

# -- Start polling

"""Starts telegram polling with global `App.on_message`, `App.on_delete_message` and `App.on_callback_query` handlers"""

# -- `on_message`

"""Builds `RawResponse` with one-message `BlockMessage` and runs `dispatcher` with it. Updates the focus talk for the chat"""

# -- `on_delete_message`

"""Updates the focus talk for the chat"""

# -- `on_callback_query`

"""Builds `RawResponse` and sends it to the dispatcher"""

# - `Dispatcher`

""" Receives `RawResponse`, collects the buffer and when the buffer is full, builds the `RawResponse` and sends it to the appropriate `Talk` or creates a new `Talk`"""

# - `Talk`

""" 
- Talk is basically a coroutine. When the coroutine is finished, the talk is removed from the `App`
- Talk may receive `Response` with `Talk.receive_response` method, which will put it in the queue (`Talk.input_channel`)
- Talk can 'Talk.ask' a `Page` and wait for the `RawResponse` (which will be awaited from the queue). You can also use the queue directly as you see fit
"""

# -- `Talk.ask`

""" 
Updates the `Talk.active_page` with the provided `Page` and `update_mode`, waits for the `Response` and processes it
"""


# - Todo
"""
4. Пройтись по разным типичным сценариям ботов и как это будет работать 
"""
