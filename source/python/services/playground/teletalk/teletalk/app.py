from typing import Callable


class TeletalkApp:
    def __init__(self):
        self.talks = []

    def start_new_talk(self, starter: Callable, starter_kwargs: dict):
        # - Create talk and add it to the list

        pass

        # - Run the starter

        pass

        # - Remove the talk from the list

        pass

    def on_ui_event(self, message):
        # - Find the talk by message_id

        pass

        # - Send the event to the talk

        pass

    def on_user_message(self, message):
        # - Send the message to the buffer of the chat

        pass

        # - Close the buffer if needed

        pass

        # -- Find the talk by message_id

        pass

        # -- Send the event to the talk

        pass

        # - Create timers if needed to try to close the buffer

        pass

    def start_polling(self, starter: Callable):
        # - Configure global handlers (UI and text)

        pass

        # - Start polling

        pass
