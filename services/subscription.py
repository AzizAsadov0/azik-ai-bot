from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database.db import get_required_channels


async def check_subscription(bot: Bot, user_id: int) -> tuple[bool, list[dict]]:
    channels = get_required_channels()

    if not channels:
        return True, []

    not_subscribed = []

    for channel in channels:
        try:
            link = channel["link"]

            if link.startswith("https://t.me/"):
                chat_id = "@" + link.replace("https://t.me/", "")
            else:
                chat_id = link

            member = await bot.get_chat_member(
                chat_id=chat_id,
                user_id=user_id
            )

            if member.status == "left":
                not_subscribed.append(channel)

        except Exception as e:
            print(e)
            not_subscribed.append(channel)

    return len(not_subscribed) == 0, not_subscribed
