import uuid

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import blake2b
from typing import List, Literal, Optional

import humanize

from lessmore.utils.time import round_datetime
from lessmore.utils.to_anything import unified_datetime


@dataclass
class Alert:
    name: str
    priority: Literal["page", "info", "warning", "error", "critical"]
    extra: Optional[dict] = None
    is_show_extra_in_message: Optional[bool] = True
    alert_id: Optional[str] = None
    responsible: Optional[str] = None
    mentions: Optional[List[str]] = None
    short_description: Optional[str] = None
    backup: Optional[str] = None
    link_urls_by_name: Optional[dict] = None
    file_urls_by_name: Optional[dict] = None
    expected_resolving_period: Optional[timedelta] = None
    counter: int = 1
    notification_text: str = ""
    first_alert_timestamp: Optional[datetime] = None
    last_mention_at: Optional[datetime] = None
    timestamp: Optional[datetime] = None
    message_id: Optional[str] = None
    custom_metadata: Optional[dict] = None
    """ 
    Represents an alert with a name, priority level, and additional metadata.

    Parameters
    ----------
    name : str
        The name of the alert.
    priority : Literal["page", "info", "warning", "error", "critical"]
        The priority level of the alert.
    extra : Optional[dict], optional
        Additional metadata about the alert, by default None.
    is_show_extra_in_message : Optional[bool], optional
        Whether to show the extra metadata in the alert message, by default True.
    alert_id : str
        The ID of the alert.
    responsible : Optional[str], optional
        The person responsible for the alert, by default None.
    mentions : Optional[List[str]], optional
        A list of people mentioned in the alert, by default None.
    short_description : Optional[str], optional
        A short description of the alert, by default None.
    backup : Optional[str], optional
        The backup person responsible for the alert, by default None.
    link_urls_by_name : Optional[dict], optional
        A dictionary mapping link names to URLs, by default None.
    file_urls_by_name : Optional[dict], optional
        A dictionary mapping file names to URLs, by default None.
    expected_resolving_period : Optional[timedelta], optional
        The expected time period to resolve the alert, by default None.
    counter : int, optional
        The number of times the alert has occurred, by default 1.
    notification_text : str, optional
        The text to be used in the notification, by default "".
    first_alert_timestamp : Optional[datetime], optional
        The timestamp for the first alert, by default None.
    last_mention_at : Optional[datetime], optional
        The timestamp for the last mention, by default None.
    timestamp : Optional[datetime], optional
        The timestamp for the alert, by default None.
    message_id : Optional[str], optional
        The ID of the message, by default None.
    custom_metadata : Optional[dict], optional
        Custom metadata about the alert, by default None.

    Attributes
    ----------
    name : str
        The name of the alert.
    priority : Literal["page", "info", "warning", "error", "critical"]
        The priority level of the alert.
    extra : Optional[dict]
        Additional metadata about the alert, by default None.
    alert_id : str
        The ID of the alert.
    responsible : Optional[str]
        The person responsible for the alert, by default None.
    mentions : Optional[List[str]]
        A list of people mentioned in the alert, by default None.
    short_description : Optional[str]
        A short description of the alert, by default None.
    backup : Optional[str]
        The backup person responsible for the alert, by default None.
    link_urls_by_name : Optional[dict]
        A dictionary mapping link names to URLs, by default None.
    file_urls_by_name : Optional[dict]
        A dictionary mapping file names to URLs, by default None.
    expected_resolving_period : Optional[timedelta]
        The expected time period to resolve the alert, by default None.
    counter : int
        The number of times the alert has occurred, by default 1.
    notification_text : str
        The text to be used in the notification, by default "".
    first_alert_timestamp : Optional[datetime]
        The timestamp for the first alert, by default None.
    last_mention_at : Optional[datetime]
        The timestamp for the last mention, by default None.
    timestamp : Optional[datetime]
        The timestamp for the alert, by default None.
    message_id : Optional[str]
        The ID of the message, by default None.
    custom_metadata : Optional[dict]
        Custom metadata about the alert, by default None.
    """

    # Needed for search message in Mattermost
    @property
    def hash_alert_id(self):
        return blake2b((self.alert_id or self.name).encode(), digest_size=10).hexdigest()

    def to_slack_message_options(self):
        utcnow = datetime.utcnow()

        first_alert_timestamp = self.first_alert_timestamp or utcnow
        last_mention_at = self.last_mention_at or utcnow
        timestamp = self.timestamp or utcnow
        message_id = self.message_id or str(uuid.uuid4())

        alert_id = self.alert_id or self.hash_alert_id

        priority = {
            "page": ":large_blue_circle:",
            "info": ":large_purple_circle:",
            "warning": ":large_yellow_circle:",
            "error": ":large_orange_circle:",
            "critical": ":red_circle:",
        }

        # - Create template

        result = {
            "text": self.notification_text,
            "metadata": {
                "event_type": "alert_counter",
                "event_payload": {
                    "counter": self.counter,
                    "name": self.name,
                    "message_id": message_id,
                    "alert_id": alert_id,
                    "first_alert_timestamp": unified_datetime.to_str(first_alert_timestamp),
                    "last_mention_at": unified_datetime.to_str(last_mention_at),
                    "timestamp": unified_datetime.to_str(timestamp),
                },
            },
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"  {priority[self.priority]}  {self.name}",
                        "emoji": True,
                    },
                },
                None
                if not self.short_description
                else {"type": "section", "text": {"type": "mrkdwn", "text": f"{self.short_description}"}},
                None
                if not self.extra
                else {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "\n".join([f"*{k[0].upper() + k[1:]}*: {v}" for k, v in self.extra.items()]),
                    },
                },
                None
                if not self.link_urls_by_name and not self.file_urls_by_name
                else {
                    "type": "context",
                    "elements": [
                        None
                        if not self.file_urls_by_name
                        else {
                            "type": "mrkdwn",
                            "text": f"*Files*: {' | '.join([f'<{value}|{key}>' for (key, value) in self.file_urls_by_name.items()])}",
                        },
                        None
                        if not self.link_urls_by_name
                        else {
                            "type": "mrkdwn",
                            "text": f"*Links*: {' | '.join([f'<{value}|{key}>' for (key, value) in self.link_urls_by_name.items()])}",
                        },
                    ],
                },
                None
                if not self.expected_resolving_period
                else {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Expected resolve time*: {humanize.precisedelta(self.expected_resolving_period)} ({unified_datetime.to_str(round_datetime(first_alert_timestamp + self.expected_resolving_period, '5m' if self.expected_resolving_period >= timedelta(minutes=30) else '1m'),pattern='%Y-%m-%d %H:%M:%S')} UTC)",
                        },
                    ],
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"*Count*: {self.counter}"},
                        {
                            "type": "mrkdwn",
                            "text": f"*Last firing*: {unified_datetime.to_str(timestamp,pattern='%Y-%m-%d %H:%M:%S')} UTC",
                        },
                        {"type": "mrkdwn", "text": f"*ID*: {alert_id}"},
                    ],
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"*Responsible*: {self.responsible}"},
                        None if not self.backup else {"type": "mrkdwn", "text": f"*Backup*: {self.backup}"},
                        None
                        if not self.mentions
                        else {"type": "mrkdwn", "text": f"*Mentions*: {' '.join(self.mentions)}\n"},
                    ],
                },
                {"type": "divider"},
            ],
        }

        # - Filter empty blocks

        result["blocks"] = [block for block in result["blocks"] if block]

        # - Filter empty elements

        result["blocks"][-2]["elements"] = [block for block in result["blocks"][-2]["elements"] if block]

        # - Return

        return result

    # get to_mattermost_message function

    def to_mattermost_message_options(self):
        priority = {
            "page": "#3AA3E3",
            "info": "#A020F0",
            "warning": "#FFCC00",
            "error": "#FFA500",
            "critical": "#FF3B30",
        }

        priority_emoji = {
            "page": ":large_blue_circle:",
            "info": ":large_purple_circle:",
            "warning": ":large_yellow_circle:",
            "error": ":large_orange_circle:",
            "critical": ":red_circle:",
        }

        utcnow: str = unified_datetime.to_str(datetime.utcnow(), pattern="%Y-%m-%d %H:%M:%S")

        first_alert_timestamp = self.first_alert_timestamp or utcnow
        last_mention_at = self.last_mention_at or utcnow
        timestamp = self.timestamp or utcnow

        extra = deepcopy(self.extra) or {}

        metrics = extra.pop("metrics", None)
        table_metrics = extra.pop("table_metrics", {})
        card = extra.pop("card", {})

        alert_id = self.hash_alert_id

        responsible = (
            None
            if not self.responsible
            else self.responsible
            if self.responsible.startswith("@")
            else f"@{self.responsible}"
        )
        mentions = (
            " ".join([mention if mention.startswith("@") else f"@{mention}" for mention in self.mentions])
            if self.mentions
            else None
        )

        # - Create template
        result = {
            "message": f"Alert ID: {alert_id}",
            "props": {
                "attachments": [
                    {
                        "fallback": self.notification_text,
                        "color": priority[self.priority],
                        "title": f"{priority_emoji[self.priority]}  {self.name}",
                        "fields": [
                            None if not self.short_description else {"short": True, "value": self.short_description},
                            None if not metrics else {"short": False, "value": metrics},
                            {"short": False, "value": table_metrics}
                            if table_metrics and self.is_show_extra_in_message
                            else None,
                            {
                                "short": False,
                                "value": "\n".join([f"**{k[0].upper() + k[1:]}**: {v}" for k, v in extra.items()]),
                            }
                            if extra and self.is_show_extra_in_message
                            else None,
                            None
                            if not responsible and not mentions
                            else {
                                "short": False,
                                "value": f"Responsible: {responsible} | Mentions: {mentions}"
                                if responsible and mentions
                                else f"Responsible: {responsible}"
                                if responsible
                                else f"Mentions: {mentions}",
                            },
                        ],
                        "footer": f"Count: {str(self.counter)}"
                        + f" | Last firing: {unified_datetime.to_str(timestamp,pattern='%Y-%m-%d %H:%M:%S')} UTC",
                    }
                ],
                None if not card else "card": "\n----------\n".join([f"{k}:\n\n \n{v}\n" for k, v in card.items()]),
                "metadata": {
                    "alert": {
                        "counter": self.counter,
                        "name": self.name,
                        "alert_id": alert_id,
                        "first_alert_timestamp": first_alert_timestamp,
                        "last_mention_at": last_mention_at,
                        "timestamp": timestamp,
                        None if not self.custom_metadata else "custom_metadata": self.custom_metadata,
                    }
                },
            },
        }

        return result


def all_test():
    slack_alert = Alert(
        name="network_hhpoker_public.hand_history__transformed",
        priority="critical",
        responsible="<@U04MMTL90Q7>",
        backup="<@U04MMTL90Q7>",
        mentions=["<@U04MMTL90Q7>", "<@U04MMTL90Q7>"],
        short_description="Completeness of data for the last 7 days",
        extra={
            "Text": "In the last 24 hours, the network_hhpoker_public.hand_history__transformed table has 85% fewer records than the average over the last 7 days"
        },
        expected_resolving_period=timedelta(hours=8, minutes=30),
        alert_id="click_hhpoker_hh_t",
        counter=1,
    )

    print(slack_alert.to_slack_message_options())

    mattermost_alert = Alert(
        name="network_hhpoker_public.hand_history__transformed",
        priority="critical",
        responsible="@polorad",
        mentions=["@polorad"],
        short_description="Completeness of data for the last 7 days",
        extra={
            "Text": "In the last 24 hours, the network_hhpoker_public.hand_history__transformed table has 85% fewer records than the average over the last 7 days"
        },
        alert_id="click_hhpoker_hh_t",
        counter=1,
    )

    print(mattermost_alert.to_mattermost_message_options())


if __name__ == "__main__":
    all_test()
