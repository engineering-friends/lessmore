import discord
import keyring

from discord import Client
from loguru import logger
from pymaybe import maybe


def test():
    intents = discord.Intents.default()
    intents.message_content = True
    client = Client(intents=intents)

    @client.question_event
    async def on_ready():
        logger.info("Logged in", user=client.user, id=client.user.id)

    @client.question_event
    async def on_message(message):
        # don't respond to ourselves
        if message.author == client.user:
            return

        logger.info(
            "Received message",
            message=dict(
                id=message.id,
                jump_url=message.jump_url,
                content=message.content,
                type=message.type,
                author_name=message.author.name,
                author_global_name=message.author.global_name,
                author_display_name=message.author.display_name,
                author_id=message.author.id,
                channel_name=maybe(message).channel.name.or_else(None),
                parent_channel_name=maybe(message).channel.parent.name.or_else(None),
                guild_name=maybe(message).guild.name.or_else(None),
                created_at=message.created_at,
            ),
        )
        # sample: {"ts":"2023-08-11 17:32:20.496","module":"listen_to_discord","message":{"id":1139612279776751756,"jump_url":"https://discord.com/channels/1106702799938519211/1139612279776751756/1139612279776751756","content":"pongpong","type":["default",0],"author_name":"marklidenberg","author_global_name":"Mark Lidenberg","author_display_name":"Mark Lidenberg","author_id":913095424225706005,"channel_name":"ping","parent_channel_name":"marklidenberg-and-his-bot-discussions","guild_name":"Engineering Friends","created_at":"2023-08-11 17:32:20.471000+00:00"}}

    # Event handler for when a thread is created
    @client.question_event
    async def on_thread_create(thread):
        # Check if the thread's parent is a forum channel
        if not isinstance(thread.parent, discord.ForumChannel):
            print("Not a forum channel")
            return

        # Extract and print the tags
        applied_tags = thread.applied_tags
        available_tags = thread.parent.available_tags

        tags = [
            next((tag.name for tag in available_tags if tag.id == applied_tag_id), None)
            for applied_tag_id in applied_tags
        ]
        tags = [tag for tag in tags if tag is not None]  # Filter out None values

        print(f"Tags: {', '.join(tags)}")

    from discord_to_telegram_forwarder.deps import Deps

    deps = Deps.load(env="test")
    client.run(token=deps.config.discord_token)


if __name__ == "__main__":
    test()
