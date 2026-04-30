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

from database.db import (
    upsert_user,
    get_setting
)

from keyboards.main_kb import (
    back_to_menu_kb,
    subscription_kb
)

from services.ai_service import (
    get_ai_response
)

from services.subscription import (
    check_subscription
)

from services.translate_service import (
    smart_translate
)


router = Router()


MODE_LABELS = {

    "ad": "📝 Reklama",

    "content": "🔥 Viral G'oya",

    "translate": "🌍 Tarjima",

    "script": "🎬 Video Script",

    "chat": "💬 AI Chat",

    "prompt": "🧠 Prompt Generator",

}


MODE_PROMPTS = {

    "ad":
        "📝 Mahsulot yoki xizmat haqida yozing:",

    "content":
        "🔥 Kontent mavzusini yozing:",

    "script":
        "🎬 Video mavzusini yozing:",

    "chat":
        "💬 Savolingizni yozing:",

    "prompt":
        "🧠 Prompt uchun idea yozing:",

}


MAX_HISTORY_PAIRS = 10


class AIState(StatesGroup):

    waiting_for_input = State()


@router.callback_query(
    F.data.startswith("mode:")
)
async def choose_mode(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.answer()

    user = callback.from_user

    upsert_user(

        user.id,

        user.username,

        user.first_name

    )

    bot = callback.bot

    is_subscribed, not_subbed = await check_subscription(

        bot,

        user.id

    )

    if not is_subscribed:

        sub_text = get_setting(
            "subscription_text"
        )

        await callback.message.edit_text(

            f"⚠️ Obuna bo'ling:\n\n{sub_text}",

            reply_markup=subscription_kb(
                not_subbed
            )

        )

        return

    mode = callback.data.split(":")[1]


    if mode == "translate":

        await state.set_state(
            AIState.waiting_for_input
        )

        await state.update_data(

            mode="translate",

            processing=False,

            history=[],

            waiting_language=True

        )

        await callback.message.edit_text(

            "🌍 Qaysi tilga tarjima qilish kerak?\n\n"

            "Misollar:\n"

            "• Ingliz tiliga\n"
            "• Nemis tiliga\n"
            "• Rus tiliga\n"
            "• Turk tiliga",

            reply_markup=back_to_menu_kb()

        )

        return


    if mode == "prompt":

        kb = InlineKeyboardMarkup(

            inline_keyboard=[

                [

                    InlineKeyboardButton(
                        text="🇺🇿 Uzbek",
                        callback_data="promptlang:uz"
                    ),

                    InlineKeyboardButton(
                        text="🇺🇸 English",
                        callback_data="promptlang:en"
                    )

                ]

            ]

        )

        await callback.message.edit_text(

            "🧠 Prompt Generator\n\n"
            "Tilni tanlang:",

            reply_markup=kb

        )

        return


    await state.set_state(
        AIState.waiting_for_input
    )

    await state.update_data(

        mode=mode,

        processing=False,

        history=[]

    )

    await callback.message.edit_text(

        MODE_PROMPTS.get(
            mode,
            "Yozing:"
        ),

        reply_markup=back_to_menu_kb()

    )


@router.callback_query(
    F.data.startswith("promptlang:")
)
async def prompt_language(
    callback: CallbackQuery,
    state: FSMContext
):

    lang = callback.data.split(":")[1]

    selected = (

        "Uzbek"

        if lang == "uz"

        else "English"

    )

    await state.set_state(
        AIState.waiting_for_input
    )

    await state.update_data(

        mode="prompt",

        prompt_language=selected,

        processing=False,

        history=[]

    )

    await callback.message.answer(

        f"✅ Til: {selected}\n\n"

        "Endi idea yozing."

    )


@router.message(
    AIState.waiting_for_input
)
async def handle_ai_input(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    if data.get("processing"):
        return

    await state.update_data(
        processing=True
    )

    mode = data.get(
        "mode",
        "chat"
    )

    history = data.get(
        "history",
        []
    )

    thinking = await message.answer(
        "⏳ Tayyorlanmoqda..."
    )

    try:


        if mode == "translate":

            waiting_language = data.get(
                "waiting_language",
                False
            )

            if waiting_language:

                await state.update_data(

                    translate_target=
                    message.text,

                    waiting_language=False,

                    waiting_text=True,

                    processing=False

                )

                await thinking.delete()

                await message.answer(

                    "✍️ Endi tarjima qilinadigan "
                    "matnni yuboring."

                )

                return


            waiting_text = data.get(
                "waiting_text",
                False
            )

            if waiting_text:

                target_language = data.get(
                    "translate_target",
                    "English"
                )

                response = await smart_translate(

                    message.text,

                    target_language

                )

                await state.update_data(
                    processing=False
                )

            else:

                response = (
                    "❌ Tarjima xatosi."
                )


        else:

            if mode == "prompt":

                language = data.get(
                    "prompt_language",
                    "English"
                )

                user_prompt = f"""

Create this in {language}:

{message.text}

Make it ultra professional,
cinematic,
highly detailed,
AI optimized.

"""

            else:

                user_prompt = message.text


            response = await get_ai_response(

                mode,

                user_prompt,

                history

            )


    except Exception as e:

        response = f"❌ Xatolik:\n{e}"


    try:

        await thinking.delete()

    except:
        pass


    history.append({

        "role": "user",

        "content": message.text

    })


    history.append({

        "role": "assistant",

        "content": response

    })


    history = history[
        -(MAX_HISTORY_PAIRS * 2):
    ]


    await state.update_data(

        processing=False,

        history=history

    )


    label = MODE_LABELS.get(
        mode,
        "AI"
    )


    formatted = f"""
<b>{label}</b>

<pre>{response}</pre>
"""


    await message.answer(

        formatted,

        parse_mode="HTML",

        reply_markup=back_to_menu_kb()

    )

