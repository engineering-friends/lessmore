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

- Renders the `Page` an gets a list of `BlockMessage`
- Sets the current `Talk.current_reply_keyboard_markup`, which will be used when the chat focus is updated 
- Updates the messages in telegram (creates new, deletes old, updates existing), depending on the `update_mode` argument
- Saves a list of `CallbackInfo` for the "Page" in the `Talk.callback_infos`, that will be used to match incoming `callback_data, or callback id to the appropriate block
- Awaits the `RawResponse`
- Build the `Response` run appropriate callback (`message_callback` or `callback_query`)
"""


# - Todo
"""
1. Флоу комманд 
3. talk хранит active_page. Есть функция update_active_page. Все вторичные данные лежат внутри active_page, в т.ч. используемые messages. history в todo maybe 
4. Пройтись по разным типичным сценариям ботов и как это будет работать 

"""
