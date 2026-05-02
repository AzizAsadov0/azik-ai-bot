from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    State,
    StatesGroup
)

from config import ADMIN_ID

from database.db import (
    get_user_count,
    get_active_users,
    get_all_users,
    get_channels,
    add_channel,
    delete_channel,
)

from keyboards.main_kb import (
    admin_menu_kb,
    admin_back_kb,
    channels_manage_kb
)

router = Router()


def is_admin(user_id: int) -> bool:
    return str(user_id) == str(ADMIN_ID)


class AdminState(StatesGroup):

    waiting_broadcast = State()

    waiting_channel_name = State()

    waiting_channel_link = State()

    waiting_channel_type = State()


@router.message(F.text == "/admin")
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(

        "🛠 Admin panel",

        reply_markup=admin_menu_kb()

    )


@router.callback_query(F.data == "admin:back")
async def admin_back(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.clear()

    await callback.message.edit_text(

        "🛠 Admin panel",

        reply_markup=admin_menu_kb()

    )


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    total = get_user_count()

    daily = get_active_users(1)

    weekly = get_active_users(7)

    monthly = get_active_users(30)

    text = (

        f"📊 Statistika\n\n"

        f"👥 Users: {total}\n"

        f"📅 1 kun: {daily}\n"

        f"📆 7 kun: {weekly}\n"

        f"🗓 30 kun: {monthly}"

    )

    await callback.message.edit_text(

        text,

        reply_markup=admin_back_kb()

    )


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.clear()

    await state.set_state(
        AdminState.waiting_broadcast
    )

    await callback.message.edit_text(

        "📢 Broadcast xabar yuboring.\n\n"

        "Matn yoki media yuborishingiz mumkin.",

        reply_markup=admin_back_kb()

    )


@router.message(AdminState.waiting_broadcast)
async def send_broadcast(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    users = get_all_users()

    sent = 0

    failed = 0

    status = await message.answer(
        "📤 Yuborilmoqda..."
    )

    for user in users:

        try:

            if message.photo:

                await message.bot.send_photo(

                    chat_id=user["id"],

                    photo=message.photo[-1].file_id,

                    caption=message.caption

                )

            elif message.video:

                await message.bot.send_video(

                    chat_id=user["id"],

                    video=message.video.file_id,

                    caption=message.caption

                )

            else:

                await message.bot.send_message(

                    chat_id=user["id"],

                    text=message.text

                )

            sent += 1

        except:

            failed += 1

    await state.clear()

    await status.edit_text(

        f"✅ Tugadi\n\n"

        f"✔ Sent: {sent}\n"

        f"❌ Failed: {failed}"

    )


@router.callback_query(F.data == "admin:channels")
async def channels_panel(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    channels = get_channels()

    text = "📡 Kanallar\n\n"

    if not channels:

        text += "Kanallar yo'q"

    else:

        for ch in channels:

            status = (
                "Majburiy"
                if ch["required"]
                else "Ixtiyoriy"
            )

            text += (

                f"• {ch['name']}\n"

                f"{ch['link']}\n"

                f"🔹 {status}\n\n"

            )

    await callback.message.edit_text(

        text,

        reply_markup=channels_manage_kb(
            channels
        )

    )


@router.callback_query(F.data == "add_channel")
async def add_channel_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.clear()

    await state.set_state(
        AdminState.waiting_channel_name
    )

    await callback.message.edit_text(

        "➕ Kanal nomini yuboring\n\n"

        "Misol:\n"

        "AZIK AI Channel"

    )


@router.message(
    AdminState.waiting_channel_name
)
async def get_channel_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(

        channel_name=message.text

    )

    await state.set_state(

        AdminState.waiting_channel_link

    )

    await message.answer(

        "🔗 Kanal linkini yuboring\n\n"

        "Misol:\n"

        "https://t.me/test"

    )


@router.message(
    AdminState.waiting_channel_link
)
async def get_channel_link(
    message: Message,
    state: FSMContext
):

    link = message.text.strip()

    if not (

        link.startswith(
            "https://t.me/"
        )

        or

        link.startswith("@")

    ):

        await message.answer(

            "❌ Noto'g'ri link"

        )

        return

    await state.update_data(

        channel_link=link

    )

    kb = InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="✅ Majburiy",

                    callback_data="channel_type:1"

                ),

                InlineKeyboardButton(

                    text="🔓 Ixtiyoriy",

                    callback_data="channel_type:0"

                )

            ]

        ]

    )

    await state.set_state(

        AdminState.waiting_channel_type

    )

    await message.answer(

        "Kanal turi:",

        reply_markup=kb

    )


@router.callback_query(
    F.data.startswith(
        "channel_type:"
    )
)
async def save_channel(
    callback: CallbackQuery,
    state: FSMContext
):

    data = await state.get_data()

    required = (

        callback.data.split(":")[1]
        == "1"

    )

    add_channel(

        name=data["channel_name"],

        link=data["channel_link"],

        required=required

    )

    await state.clear()

    await callback.answer(
        "✅ Kanal qo'shildi"
    )

    channels = get_channels()

    await callback.message.edit_text(

        "📡 Kanal qo'shildi",

        reply_markup=channels_manage_kb(
            channels
        )

    )


@router.callback_query(
    F.data.startswith(
        "del_channel:"
    )
)
async def remove_channel(
    callback: CallbackQuery
):

    if not is_admin(
        callback.from_user.id
    ):
        return

    channel_id = int(

        callback.data.split(":")[1]

    )

    delete_channel(channel_id)

    channels = get_channels()

    await callback.answer(
        "✅ O'chirildi"
    )

    await callback.message.edit_text(

        "📡 Kanal o'chirildi",

        reply_markup=channels_manage_kb(
            channels
        )

    )