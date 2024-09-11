# - `App`

"""

App contains current talks.

Each chat has a focus talk, which is the talk with the latest message. By default, dispatcher will send the new message to the focus talk of the chat.

Also, app updates the chat `reply_keyboard_markup` to match the focus talk.

"""

# -- Start polling

"""Starts telegram polling with global `App.on_message`, `App.on_delete_message` and `App.on_callback_query` handlers"""

# -- `on_message`

"""Builds `RawResponse` with one-message `BundleMessage` and runs `dispatcher` with it. Updates the focus talk for the chat"""

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
- Talk can 'Talk.ask' a query and wait for the `RawResponse` (which will be awaited from the queue). You can also use the queue directly as you see fit
"""

# -- `Talk.ask`

""" 

- Renders the `MultiQuery` an gets a list of `BundleMessage`
- Sets the current `Talk.current_reply_keyboard_markup`, which will be used when the chat focus is updated 
- Updates the messages in telegram (creates new, deletes old, updates existing), depending on the `update_mode` argument
- Saves a list of `CallbackInfo` for the "MultiQuery" in the `Talk.callback_infos`, that will be used to match incoming `callback_data, or callback id to the appropriate query
- Awaits the `RawResponse`
- Build the `Response` run appropriate callback (`message_callback` or `callback_query`)
"""


# - Todo
"""
1. Флоу команд 

"""
