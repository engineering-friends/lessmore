import copy

from typing import Optional

from airflow_etl.lib.mattermostdriver_client import MattermostDriverClient

from lessmore.utils.alerter.alert import Alert


def post_mattermost_alert(
    mattermost_client: MattermostDriverClient,
    channel_id: str,
    alert: Alert,
    files: Optional[dict] = None,
    extra_to_reply: Optional[bool] = False,
    resolved_alert_reaction: Optional[str] = "white_check_mark",
) -> dict:
    """
    Post an alert message to Mattermost.

    Parameters
    ----------
    mattermost_client : MattermostDriverClient
        The Mattermost client to use for posting the alert message.
    channel_id : str
        The Mattermost channel ID where the message should be posted.
    alert : Alert
        The alert to post.
    files : Optional[dict], optional
        The files to attach to the message, by default None. Format: {"filename": binary_file}.
    extra_to_reply : Optional[bool], optional
        Whether to add the extra information to the reply in root message. By default False.
    resolved_alert_reaction : Optional[str], optional
        The Mattermost reaction that should be added to the message when the alert is resolved, by default
        "white_check_mark".

    Returns
    -------
    dict
        Returns message data if the alert is successfully posted.

    Raises
    ------
    MattermostAPIException
        If an error occurs while posting the alert message.
    """

    # - Preprocess arguments

    alert = copy.deepcopy(alert)

    # - Process

    messages = mattermost_client.posts__search_for_team_posts(
        terms=f"{alert.hash_alert_id} from:{mattermost_client.bot_user_id} in:{channel_id}",
    )

    if messages.get("order"):
        message = messages["posts"][messages["order"][0]]
        message_reactions = message["metadata"].get("reactions", [])

        if resolved_alert_reaction in [reaction["emoji_name"] for reaction in message_reactions]:
            # mattermost_client.posts__delete_post(post_id=message["id"]) # only cleaner can delete messages
            new_message = mattermost_client.posts__create_post(
                username_or_channel_id=channel_id, **alert.to_mattermost_message_options()
            )

        else:
            old_alert = message["props"]["metadata"]["alert"]
            new_alert = copy.deepcopy(alert)

            new_alert.first_alert_timestamp = old_alert["first_alert_timestamp"]
            new_alert.counter = old_alert["counter"] + 1
            new_alert.last_mention_at = old_alert["last_mention_at"]
            new_alert.notification_text = f"Alert '{new_alert.name}' has been updated"

            new_message = mattermost_client.posts__patch_post(
                post_id=message["id"],
                message="",
                additional_options=new_alert.to_mattermost_message_options(),
            )

    else:
        new_message = mattermost_client.posts__create_post(
            username_or_channel_id=channel_id, **alert.to_mattermost_message_options()
        )

    if extra_to_reply or files:
        alert.extra.pop("card", None)

        if alert.extra or files:
            mattermost_client.posts__create_post(
                username_or_channel_id=channel_id,
                message="\n\n".join([f"*{key}*:\n\n{value}" for key, value in alert.extra.items()]),
                root_id=new_message["id"],
                file_name_to_binaries=files,
            )

    return new_message


def test_post_alert():
    # - Init connections

    mattermost_test_channel_id = "jcctu9nxyjfp3xkmf94a4tua7w"  # test-alerts-data-etl

    test_client_config = {"options": {"url": "localhost", "port": 8065, "token": "my-token", "scheme": "http"}}

    # # [DEBUG] - Get connection from Airflow
    # from airflow_etl.lib.get_connection import get_connection
    # connection = get_connection('mattermost_reporter')
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

    alerts = [
        {
            # no extra
            "name": "network_hhpoker_public.hand_history__transformed",
            "priority": "info",
            "responsible": "3dg95419k3df9dexjt11gbn1ce",
            "mentions": ["3dg95419k3df9dexjt11gbn1ce"],
            "short_description": "Completeness of data for the last 7 days",
            "extra": {
                "text": "За последние сутки в таблице network_hhpoker_public.hand_history__transformed на 65% меньше записей, чем в среднем за последние 14 дней",
                "Emotion": "😆",
            },
            "alert_id": "click_hhpoker_hh_t2",
        },
        {
            # two extra rows
            "name": "network_jackpoker_public.hand_history__transformed_from_observer",
            "priority": "info",
            "responsible": "3dg95419k3df9dexjt11gbn1ce",
            "mentions": ["3dg95419k3df9dexjt11gbn1ce"],
            "short_description": "Completeness of data for the last 14 days",
            "extra": {
                "text": "За последние сутки в таблице network_jackpoker_public.hand_history__transformed_from_observer на 65% меньше записей, чем в среднем за последние 14 дней",
                "Emotion": "😆",
            },
            "alert_id": "click_jackpoker_hh_t_fo2",
        },
        {
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
        },
    ]

    # - Init mattermost alerter

    mattermost_client = MattermostDriverClient(client_config=test_client_config)

    # - Alert

    messages = []
    for alert in alerts:
        message = post_mattermost_alert(
            mattermost_client=mattermost_client,
            channel_id=mattermost_test_channel_id,
            alert=Alert(**alert),
        )
        messages.append(message)

    # - Change priorities

    for alert in alerts:
        alert["priority"] = "critical"

    # - Alert

    messages = []
    for alert in alerts:
        message = post_mattermost_alert(
            mattermost_client=mattermost_client,
            channel_id=mattermost_test_channel_id,
            alert=Alert(**alert),
        )
        messages.append(message)

    # - Clean up

    for message in messages:
        mattermost_client.posts__delete_post(message["id"])


if __name__ == "__main__":
    test_post_alert()
