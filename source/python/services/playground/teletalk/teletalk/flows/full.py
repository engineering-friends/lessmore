from teletalk.app import App


# - `App`

# -- Start polling

""" Starts telegram polling with global `App.on_message`, `App.on_delete_message` and `App.on_callback_query` handlers"""

# -- `on_message`

"""Build `RawResponse` with one-message `BundleMessage` and send it to the dispatcher. Updates the chat focus"""

# -- `on_delete_message`

"""Updates the chat focus"""

# -- `on_callback_query`

"""Build `RawResponse` and send it to the dispatcher"""


# - `Dispatcher`

""" Receives `RawResponse`, collects the buffer and when the buffer is full, builds the `Response` and sends it to the appropriate `Talk` or creates a new `Talk`"""

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
- Saves a list of `CallbackInfo` for the "MultiQuery" in the `Talk.callback_infos`
- Awaits the `RawResponse`
- For each `Query` runs the `on_query_reply` callback (for example, to disable buttons or show progress bars)
(weak point, a logic is flawed here) 
- Runs and returns the appropriate callback (`message_callback` or `callback_query`)
"""
