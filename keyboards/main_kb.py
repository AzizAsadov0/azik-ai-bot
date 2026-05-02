from aiogram.types import (

    InlineKeyboardMarkup,

    InlineKeyboardButton,

    WebAppInfo

)


WEB_APP_URL = "https://azizasadov935-hue.github.io/AzizjonAsaodov/"


def main_menu_kb():

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(
                    text="📝 Reklama yozish",
                    callback_data="mode:ad"
                ),

                InlineKeyboardButton(
                    text="🎥 Kontent g'oya",
                    callback_data="mode:content"
                )

            ],

            [

                InlineKeyboardButton(
                    text="🌍 Tarjima",
                    callback_data="mode:translate"
                ),

                InlineKeyboardButton(
                    text="🎬 Video script",
                    callback_data="mode:script"
                )

            ],

            [

                InlineKeyboardButton(
                    text="🧠 Prompt Generator",
                    callback_data="mode:prompt"
                )

            ],

            [

                InlineKeyboardButton(
                    text="💬 AI Chat",
                    callback_data="mode:chat"
                )

            ],

            [

                InlineKeyboardButton(

                    text="🌐 Open App",

                    web_app=WebAppInfo(

                        url=WEB_APP_URL

                    )

                )

            ]

        ]

    )


def subscription_kb(
    channels
):

    buttons = []

    for ch in channels:

        buttons.append([

            InlineKeyboardButton(

                text=f"📢 {ch['name']}",

                url=ch["link"]

            )

        ])


    buttons.append([

        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_sub"
        )

    ])


    return InlineKeyboardMarkup(

        inline_keyboard=buttons

    )


def back_to_menu_kb():

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="🏠 Asosiy menyu",

                    callback_data="back_menu"

                )

            ]

        ]

    )


def admin_menu_kb():

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin:stats"
                ),

                InlineKeyboardButton(
                    text="📢 Broadcast",
                    callback_data="admin:broadcast"
                )

            ],

            [

                InlineKeyboardButton(
                    text="📡 Kanallar",
                    callback_data="admin:channels"
                )

            ]

        ]

    )


def admin_back_kb():

    return InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="🔙 Orqaga",

                    callback_data="admin:back"

                )

            ]

        ]

    )


def channels_manage_kb(
    channels
):

    buttons = []

    for ch in channels:

        buttons.append([

            InlineKeyboardButton(

                text=f"❌ {ch['name']}",

                callback_data=f"del_channel:{ch['id']}"

            )

        ])


    buttons.append([

        InlineKeyboardButton(

            text="➕ Kanal qo'shish",

            callback_data="add_channel"

        )

    ])


    buttons.append([

        InlineKeyboardButton(

            text="🔙 Orqaga",

            callback_data="admin:back"

        )

    ])


    return InlineKeyboardMarkup(

        inline_keyboard=buttons

    )
