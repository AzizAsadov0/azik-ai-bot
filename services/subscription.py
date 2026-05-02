from aiogram import Bot

from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError
)

from database.db import (
    get_required_channels
)


VALID_STATUSES = [

    "creator",

    "administrator",

    "member"

]


async def check_subscription(
    bot: Bot,
    user_id: int
):

    channels = get_required_channels()

    if not channels:

        return True, []


    not_subscribed = []


    for channel in channels:

        try:

            link = channel["link"]


            if link.startswith(
                "https://t.me/"
            ):

                username = link.replace(
                    "https://t.me/",
                    ""
                )

                chat_id = f"@{username}"

            else:

                chat_id = link


            member = await bot.get_chat_member(

                chat_id=chat_id,

                user_id=user_id

            )


            if member.status not in VALID_STATUSES:

                not_subscribed.append({

                    "name": channel["name"],

                    "link": channel["link"]

                })


        except (

            TelegramBadRequest,

            TelegramForbiddenError

        ):

            not_subscribed.append({

                "name": channel["name"],

                "link": channel["link"]

            })


        except Exception:

            not_subscribed.append({

                "name": channel["name"],

                "link": channel["link"]

            })


    return (

        len(not_subscribed) == 0,

        not_subscribed

    )