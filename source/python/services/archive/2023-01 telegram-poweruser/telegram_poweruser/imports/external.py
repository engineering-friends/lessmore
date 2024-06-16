# - Imports

import asyncio
import json
import os
import random
import re
import time

from datetime import datetime, timedelta
from pprint import pprint
from typing import List, Literal, Optional, Tuple, cast

import numpy as np
import pandas as pd
import tqdm

from loguru import logger
from pydantic import BaseSettings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)
from telethon import events, functions, types
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage


# - Missing dependencies


def get_complex_attribute(value, expression, default=None, is_safe=False):
    if not is_safe:
        assert not default, "Default is meaningless in non-safe-mode"

    if isinstance(expression, list):
        for sub_expression in expression:
            res = get_complex_attribute(value, sub_expression, is_safe=True)
            if res is not None:
                return res
    else:
        try:
            for attribute in expression.split("."):
                value = getattr(value, attribute)
            return value
        except:
            pass

    if is_safe:
        return default

    raise KeyError(expression)


import os


def get_root_directory(path, directory_name=None):
    current_path = path
    while current_path and current_path != "/":
        current_path = os.path.dirname(current_path)

        if directory_name and os.path.basename(current_path) == directory_name:
            return current_path

        if os.path.exists(os.path.join(current_path, "pyproject.toml")):
            return current_path

    raise Exception("Failed to find root directory")


# - To_datetime and to_timedelta

from datetime import date, datetime
from typing import Union

import pendulum

from dateutil.parser import parse as parse_date
from loguru import logger


COMMON_DATETIME_PATTERNS = [
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%Y.%m.%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y%m%d%H%M%S",
    "%Y%m%d",
    "%Y-%m-%d--%H-%M-%S",  # filename safe pattern
    "%Y-%m-%d--%H-%M-%S--%f",  # filename safe pattern,
    "%Y-%m-%dT%H:%M:%SZ",  # ISO8061
    "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO8061
]

DatetimeLike = Union[datetime, pendulum.DateTime, str, int, float]


class UnifiedDatetime:
    def __call__(self, value):
        # logger.warning("unified_datetime() is deprecated and soon will be removed, use to_datetime() instead")
        return UnifiedDatetime.to_datetime(value)

    @staticmethod
    def to_datetime(value, **kwargs):
        if isinstance(value, datetime) and not isinstance(value, pendulum.DateTime):
            if value.tzinfo:
                value = value.astimezone(pendulum.UTC).replace(tzinfo=None)
            return value
        elif isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        elif isinstance(value, pendulum.DateTime):
            return UnifiedDatetime.to_datetime(value.in_timezone(pendulum.UTC).timestamp())
        elif isinstance(value, (int, float)):
            # - Try in seconds

            try:
                return datetime.fromtimestamp(value, pendulum.tz.UTC).replace(tzinfo=None)
            except:
                # too small or too big
                pass

            # - Try in milliseconds

            try:
                return datetime.fromtimestamp(value / 1_000, pendulum.tz.UTC).replace(tzinfo=None)
            except:
                pass

            # - Try in microseconds

            try:
                return datetime.fromtimestamp(value / 1_000_000, pendulum.tz.UTC).replace(tzinfo=None)
            except:
                pass

            raise Exception(f"Integer out of bounds for datetime: {value}")
        elif isinstance(value, str):
            # - Try most common patterns

            for pattern in COMMON_DATETIME_PATTERNS:
                try:
                    return datetime.strptime(value, pattern)
                except:
                    continue

            # - Try dateutils.parser.parse

            try:
                result = parse_date(value, **kwargs)
                if result and result.tzinfo:
                    result = result.astimezone(pendulum.UTC).replace(tzinfo=None)
                return result
            except:
                pass

            raise Exception(f"Unknown string datetime format: {value}")
        raise Exception("Unknown datetime type")

    @staticmethod
    def to_pendulum(value):
        if isinstance(value, pendulum.DateTime):
            return value
        else:
            value = UnifiedDatetime.to_datetime(value)
            return pendulum.instance(value, tz=pendulum.UTC)

    @staticmethod
    def get_pattern_by_string(datetime_string):
        for pattern in COMMON_DATETIME_PATTERNS:
            try:
                datetime.strptime(datetime_string, pattern)
                return pattern
            except:
                continue

        raise Exception(f"Failed to get pattern for string {datetime_string}")

    @staticmethod
    def to_str(value, pattern=None, like=None):
        value = UnifiedDatetime.to_datetime(value)
        if like:
            pattern = UnifiedDatetime.get_pattern_by_string(like)
        else:
            pattern = pattern or "%Y-%m-%d %H:%M:%S.%f"
        return datetime.strftime(value, pattern)

    @staticmethod
    def to_filename_str(value, include_milliseconds=False):
        return UnifiedDatetime.to_str(
            value,
            pattern="%Y-%m-%d--%H-%M-%S" if not include_milliseconds else "%Y-%m-%d--%H-%M-%S--%f",
        )

    @staticmethod
    def to_filename_safe_string(value, include_milliseconds=False):
        logger.warning(
            "unified_datetime.to_filename_safe_string() is deprecated and soon will be removed, use to_filename_safe_str() instead"
        )
        return UnifiedDatetime.to_filename_str(value, include_milliseconds=include_milliseconds)

    @staticmethod
    def to_timestamp(value):
        value = UnifiedDatetime.to_datetime(value)
        return value.replace(tzinfo=pendulum.tz.UTC).timestamp()


unified_datetime = UnifiedDatetime()


def to_datetime(value, **kwargs):
    return unified_datetime.to_datetime(value, **kwargs)


def to_pendulum(value):
    return unified_datetime.to_pendulum(value)


def to_datetime_str(value, pattern=None, like=None):
    return unified_datetime.to_str(value, pattern=pattern, like=like)


def to_datetime_filename_str(value, include_milliseconds=False):
    return unified_datetime.to_filename_str(value, include_milliseconds=include_milliseconds)


def to_timestamp(value):
    return unified_datetime.to_timestamp(value)
