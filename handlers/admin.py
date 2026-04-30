from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database.db import (
    get_user_count, get_active_users, get_all_users,
    get_channels, add_channel, delete_channel,
    get_setting, set_setting
)
from keyboards.main_kb import (
    admin_menu_kb, channels_manage_kb, settings_kb, admin_back_kb
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == 7534509370


class AdminState(StatesGroup):
    broadcast_waiting = State()
    add_channel_name = State()
    add_channel_link = State()
    add_channel_required = State()
    edit_setting_value = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Ruxsat yo'q.")
        return
    await message.answer(
        "🛠 <b>Admin Panel</b>\n\nNimani qilmoqchisiz?",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "🛠 <b>Admin Panel</b>\n\nNimani qilmoqchisiz?",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
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
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total}</b>\n"
        f"📅 Bugungi aktiv: <b>{daily}</b>\n"
        f"📆 Haftalik aktiv: <b>{weekly}</b>\n"
        f"🗓 Oylik aktiv: <b>{monthly}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.answer()
    users = get_all_users()
    total = len(users)

    if not users:
        await callback.message.edit_text(
            "Hozircha foydalanuvchilar yo'q.",
            reply_markup=admin_back_kb()
        )
        return

    header = f"👤 <b>Barcha foydalanuvchilar ({total} ta)</b>\n\n"
    lines = []
    for i, u in enumerate(users, 1):
        uname = f"@{u['username']}" if u.get("username") else "—"
        lines.append(
            f"{i}. <b>{u['first_name']}</b> ({uname})\n"
            f"   ID: <code>{u['id']}</code> | {u['last_active'][:16]}"
        )

    chunk_size = 30
    chunks = [lines[i:i+chunk_size] for i in range(0, len(lines), chunk_size)]

    await callback.message.edit_text(
        header + "\n\n".join(chunks[0]) + (f"\n\n<i>... va yana {total - chunk_size} ta</i>" if len(chunks) > 1 else ""),
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )

    for chunk in chunks[1:]:
        await callback.message.answer(
            "\n\n".join(chunk),
            reply_markup=admin_back_kb(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminState.broadcast_waiting)
    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yuboriladigan xabarni yozing.\n"
        "<i>Matn, rasm, video yoki audio yuborishingiz mumkin.</i>\n\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )


@router.message(AdminState.broadcast_waiting, F.from_user.func(lambda u: u.id == ADMIN_ID))
async def admin_broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    bot = message.bot
    sent = 0
    failed = 0
    status_msg = await message.answer(f"📤 Yuborilmoqda... (0/{len(users)})")

    for i, user in enumerate(users):
        try:
            if message.photo:
                await bot.send_photo(
                    user["id"],
                    message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            elif message.video:
                await bot.send_video(
                    user["id"],
                    message.video.file_id,
                    caption=message.caption or ""
                )
            elif message.audio:
                await bot.send_audio(
                    user["id"],
                    message.audio.file_id,
                    caption=message.caption or ""
                )
            elif message.document:
                await bot.send_document(
                    user["id"],
                    message.document.file_id,
                    caption=message.caption or ""
                )
            else:
                await bot.send_message(user["id"], message.text)
            sent += 1
        except Exception:
            failed += 1

        if (i + 1) % 10 == 0:
            try:
                await status_msg.edit_text(f"📤 Yuborilmoqda... ({i + 1}/{len(users)})")
            except Exception:
                pass

    await state.clear()
    await status_msg.edit_text(
        f"✅ Broadcast yakunlandi!\n"
        f"✔ Yuborildi: {sent}\n"
        f"❌ Muvaffaqiyatsiz: {failed}"
    )


@router.callback_query(F.data == "admin:channels")
async def admin_channels(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    channels = get_channels()
    text = "📡 <b>Kanallar boshqaruvi</b>\n\n"
    if channels:
        for ch in channels:
            req = "✅ Majburiy" if ch["required"] else "🔓 Ixtiyoriy"
            text += f"• <b>{ch['name']}</b> — {ch['link']} [{req}]\n"
    else:
        text += "Hozircha kanallar qo'shilmagan."
    await callback.message.edit_text(
        text,
        reply_markup=channels_manage_kb(channels),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("del_channel:"))
async def delete_channel_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    channel_id = int(callback.data.split(":")[1])
    delete_channel(channel_id)
    channels = get_channels()
    await callback.answer("✅ Kanal o'chirildi!")
    await callback.message.edit_reply_markup(reply_markup=channels_manage_kb(channels))


@router.callback_query(F.data == "add_channel")
async def add_channel_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminState.add_channel_name)
    await callback.message.edit_text(
        "➕ <b>Kanal qo'shish</b>\n\nKanal username yozing (masalan: @AZIK_AI_bot):",
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )


@router.message(AdminState.add_channel_name, F.from_user.func(lambda u: u.id == ADMIN_ID))
async def add_channel_name(message: Message, state: FSMContext):
    await state.update_data(channel_name=message.text)
    await state.set_state(AdminState.add_channel_link)
    await message.answer(
        "Kanal linkini yozing (masalan: https://t.me/example yoki @example):",
        reply_markup=admin_back_kb()
    )


@router.message(AdminState.add_channel_link, F.from_user.func(lambda u: u.id == ADMIN_ID))
async def add_channel_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("https://t.me/") or link.startswith("@")):
        await message.answer("❌ Link noto'g'ri. https://t.me/... yoki @username formatida kiriting:")
        return
    await state.update_data(channel_link=link)
    await state.set_state(AdminState.add_channel_required)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, majburiy", callback_data="ch_req:1"),
            InlineKeyboardButton(text="🔓 Yo'q, ixtiyoriy", callback_data="ch_req:0"),
        ]
    ])
    await message.answer("Bu kanal majburiy bo'lsinmi?", reply_markup=kb)


@router.callback_query(F.data.startswith("ch_req:"))
async def add_channel_required_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    required = callback.data.split(":")[1] == "1"
    data = await state.get_data()
    add_channel(data["channel_name"], data["channel_link"], required)
    await state.clear()
    channels = get_channels()
    req_label = "Majburiy" if required else "Ixtiyoriy"
    await callback.answer(f"✅ Kanal qo'shildi ({req_label})!")
    await callback.message.edit_text(
        "📡 <b>Kanallar boshqaruvi</b>",
        reply_markup=channels_manage_kb(channels),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:settings")
async def admin_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    welcome = get_setting("welcome_text")
    sub = get_setting("subscription_text")
    text = (
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"<b>Xush kelibsiz matni:</b>\n{welcome}\n\n"
        f"<b>Obuna matni:</b>\n{sub}"
    )
    await callback.message.edit_text(
        text,
        reply_markup=settings_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("settings:"))
async def edit_setting_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split(":")[1]
    await state.set_state(AdminState.edit_setting_value)
    await state.update_data(setting_key=key)
    current = get_setting(key)
    labels = {
        "welcome_text": "Xush kelibsiz matni",
        "subscription_text": "Obuna matni",
    }
    label = labels.get(key, key)
    await callback.message.edit_text(
        f"✏️ <b>{label}</b>\n\nHozirgi qiymat:\n<i>{current}</i>\n\nYangi matnni yozing:",
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )


@router.message(AdminState.edit_setting_value, F.from_user.func(lambda u: u.id == ADMIN_ID))
async def edit_setting_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    key = data.get("setting_key")
    set_setting(key, message.text)
    await state.clear()
    await message.answer(
        "✅ Sozlama saqlandi!",
        reply_markup=admin_back_kb()
    )
