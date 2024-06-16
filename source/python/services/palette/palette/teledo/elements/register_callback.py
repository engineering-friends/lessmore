import uuid

from typing import Callable, Optional

from palette.teledo.context import context
from palette.teledo.elements.callback_info import CallbackInfo
from palette.teledo.elements.element import Element


def register_callback(
    callback: Callable,
    element: Element,
):
    _id = str(uuid.uuid4())
    context.callbacks_infos[_id] = CallbackInfo(callback=callback, element=element)
    return _id
