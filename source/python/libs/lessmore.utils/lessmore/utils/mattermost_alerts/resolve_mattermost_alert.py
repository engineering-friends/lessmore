import copy
import re

from datetime import datetime, timedelta
from typing import Optional

from lessmore.utils.alerter.alert import Alert
from lessmore.utils.unified import to_timedelta

from airflow_etl.lib.mattermostdriver_client import MattermostDriverClient


def resolve_mattermost_alert(
    mattermost_client: MattermostDriverClient,
    channel_id: str,
    alert: Alert,
    resolved_alert_reaction: Optional[str] = "white_check_mark",
    lookback_period: str = "30d",
    extra_to_reply: Optional[bool] = True,
) -> None:
    """

    Find all alert messages, make attachment color green and add resolved_alert_reaction.

    Parameters
    ----------
    mattermost_client : MattermostDriverClient
        The Mattermost client to use for posting the alert message.
    channel_id : str
        The Mattermost channel ID where the message should be posted.
    alert : Alert
        Alert to resolve
    resolved_alert_reaction : Optional[str], optional
        The Mattermost reaction that should be added to the message when the alert is resolved, by default
        "white_check_mark".
    lookback_period : str, optional
        How far to look back for messages to resolve, by default "30d".
    extra_to_reply : Optional[bool], optional
        Whether to add the extra information to the reply in root message. By default False.
    """

    # - Process

    messages = mattermost_client.posts__search_for_team_posts(
        terms=f"{alert.hash_alert_id} from:{mattermost_client.bot_user_id} in:{channel_id} after:{(datetime.utcnow() - to_timedelta(lookback_period)).date()}",
    )

    # - Skip if no messages found

    if not messages.get("order"):

        # no messages found
        return

    # - Get messages

    messages = list(messages["posts"].values())

    # - Filter out messages that are not resolved yet

    messages = [message for message in messages if message["props"]["attachments"][0]["color"] != "#00FF00"]

    # - Process messages

    for message in messages:

        # - Set color to green

        message["props"]["attachments"][0]["color"] = "#00FF00"

        # - Patch message

        mattermost_client.posts__patch_post(
            post_id=message["id"],
            message=message["message"],
            additional_options=message,
        )

        # - Add resolved_alert_reaction

        mattermost_client.reactions__create_reaction(
            post_id=message["id"],
            emoji_name=resolved_alert_reaction,
            user_id=mattermost_client.bot_user_id,
        )

        # - Send extra info to root message

        if extra_to_reply and alert.extra:
            alert.extra.pop("card", None)

            mattermost_client.posts__create_post(
                username_or_channel_id=channel_id,
                message="\n\n".join([f"*{key}*:\n\n{value}" for key, value in alert.extra.items()]),
                root_id=message["id"],
            )


def test_post_alert():
    from lessmore.utils.alerter import post_mattermost_alert

    # - Init connections

    mattermost_test_channel_id = "jcctu9nxyjfp3xkmf94a4tua7w"  # test-alerts-data-etl

    test_client_config = {"options": {"url": "localhost", "port": 8065, "token": "my-token", "scheme": "http"}}

    # # [DEBUG] - Get connection from Airflow
    # from airflow_etl.lib.get_connection import get_connection
    #
    # connection = get_connection("mattermost_reporter")
    # test_client_config = {
    #     "options": {
    #         **{
    #             "url": connection.host.replace("https://", "").replace("http://", ""),
    #             "port": connection.port,
    #             "token": connection.password,
    #             "scheme": connection.schema,
    #             "verify": True,
    #         },
    #     },
    # }

    # - Init alerts

    alert = {
        # normal priority + mentions
        "name": "network_pokersaint_public.hand_history__transformed",
        "priority": "info",
        "responsible": "3dg95419k3df9dexjt11gbn1ce",
        "mentions": ["3dg95419k3df9dexjt11gbn1ce"],
        "short_description": "Completeness of data for the last 14 days",
        "extra": {
            "text": "За последние сутки в таблице network_pokersaint_public.hand_history__transformed на 60% меньше записей, чем в среднем за последние 14 дней"
        },
        "alert_id": "click_pokersaint_hh_t2",
    }

    # - Init mattermost alerter

    mattermost_client = MattermostDriverClient(client_config=test_client_config)

    # - Alert

    message = post_mattermost_alert(
        mattermost_client=mattermost_client,
        channel_id=mattermost_test_channel_id,
        alert=Alert(**alert),
    )

    resolve_mattermost_alert(
        alert=Alert(**alert),
        mattermost_client=mattermost_client,
        channel_id=mattermost_test_channel_id,
    )

    # - Clean up

    mattermost_client.posts__delete_post(message["id"])


if __name__ == "__main__":
    test_post_alert()
