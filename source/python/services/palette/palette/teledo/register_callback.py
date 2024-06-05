import uuid

from typing import Callable, Optional

from palette.teledo.callback_info import CallbackInfo
from palette.teledo.context import Context
from palette.teledo.element_primitives import Element


def register_callback(element: Element, callback: Callable, context: Context):
    _id = str(uuid.uuid4())
    context.callbacks_infos[_id] = CallbackInfo(callback=callback, element=element)
    return _id
