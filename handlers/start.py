from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database.db import upsert_user, get_setting
from keyboards.main_kb import main_menu_kb, subscription_kb, back_to_menu_kb
from services.subscription import check_subscription

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    upsert_user(user.id, user.username, user.first_name)

    bot = message.bot
    is_subscribed, not_subbed = await check_subscription(bot, user.id)

    if is_subscribed:
        welcome = get_setting("welcome_text")
        await message.answer(
            welcome,
            reply_markup=main_menu_kb()
        )
    else:
        sub_text = get_setting("subscription_text")
        await message.answer(
            f"👋 Salom, <b>{user.first_name}</b>!\n\n{sub_text}",
            reply_markup=subscription_kb(not_subbed),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "check_sub")
async def check_subscription_cb(callback: CallbackQuery):
    user = callback.from_user
    upsert_user(user.id, user.username, user.first_name)

    bot = callback.bot
    is_subscribed, not_subbed = await check_subscription(bot, user.id)

    if is_subscribed:
        await callback.answer()
        welcome = get_setting("welcome_text")
        await callback.message.edit_text(
            welcome,
            reply_markup=main_menu_kb()
        )
    else:
        await callback.answer("❌ Siz hali obuna bo'lmadingiz!", show_alert=True)
        sub_text = get_setting("subscription_text")
        await callback.message.edit_text(
            f"⚠️ Iltimos, barcha kanallarga obuna bo'ling:\n\n{sub_text}",
            reply_markup=subscription_kb(not_subbed)
        )


@router.callback_query(F.data == "skip_sub")
async def skip_subscription_cb(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    upsert_user(user.id, user.username, user.first_name)

    welcome = get_setting("welcome_text")
    await callback.message.edit_text(
        welcome,
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "back_menu")
async def back_to_menu_cb(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user = callback.from_user
    upsert_user(user.id, user.username, user.first_name)

    await state.clear()

    welcome = get_setting("welcome_text")
    await callback.message.edit_text(
        welcome,
        reply_markup=main_menu_kb()
    )

