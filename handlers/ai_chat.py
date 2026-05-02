```python id="aichatv2"
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

from services.subscription import (
    check_subscription
)

from services.ai_service import (
    get_ai_response
)

from services.translate_service import (
    smart_translate
)

router = Router()


MAX_HISTORY = 10


MODE_LABELS = {

    "ad": "📝 Reklama",

    "content": "🔥 Kontent G'oya",

    "script": "🎬 Video Script",

    "chat": "💬 AI Chat",

    "prompt": "🧠 Prompt Generator",

    "translate": "🌍 Tarjima"

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
        "🧠 Prompt uchun idea yozing:"

}


class AIState(StatesGroup):

    waiting_message = State()

    waiting_translate_language = State()

    waiting_translate_text = State()


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

    is_subscribed, not_subscribed = await check_subscription(

        callback.bot,

        user.id

    )

    if not is_subscribed:

        sub_text = get_setting(
            "subscription_text"
        )

        await callback.message.edit_text(

            f"⚠️ {sub_text}",

            reply_markup=subscription_kb(
                not_subscribed
            )

        )

        return


    mode = callback.data.split(":")[1]

    await state.clear()


    if mode == "translate":

        await state.set_state(

            AIState.waiting_translate_language

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

                        callback_data="prompt_lang:uz"

                    ),

                    InlineKeyboardButton(

                        text="🇺🇸 English",

                        callback_data="prompt_lang:en"

                    )

                ]

            ]

        )

        await callback.message.edit_text(

            "🧠 Prompt tilini tanlang:",

            reply_markup=kb

        )

        return


    await state.set_state(
        AIState.waiting_message
    )

    await state.update_data(

        mode=mode,

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
    F.data.startswith(
        "prompt_lang:"
    )
)
async def choose_prompt_language(
    callback: CallbackQuery,
    state: FSMContext
):

    lang = callback.data.split(":")[1]

    language = (

        "Uzbek"

        if lang == "uz"

        else "English"

    )

    await state.set_state(
        AIState.waiting_message
    )

    await state.update_data(

        mode="prompt",

        prompt_language=language,

        history=[]

    )

    await callback.message.edit_text(

        f"✅ Til: {language}\n\n"

        "Endi idea yozing.",

        reply_markup=back_to_menu_kb()

    )


@router.message(
    AIState.waiting_translate_language
)
async def get_translate_language(
    message: Message,
    state: FSMContext
):

    await state.update_data(

        translate_language=message.text

    )

    await state.set_state(

        AIState.waiting_translate_text

    )

    await message.answer(

        "✍️ Endi tarjima qilinadigan matnni yuboring.",

        reply_markup=back_to_menu_kb()

    )


@router.message(
    AIState.waiting_translate_text
)
async def translate_text(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    language = data.get(
        "translate_language"
    )

    wait = await message.answer(
        "⏳ Tarjima qilinmoqda..."
    )

    try:

        response = await smart_translate(

            message.text,

            language

        )

        await wait.delete()

        await message.answer(

            f"<b>🌍 Tarjima</b>\n\n"

            f"<pre>{response}</pre>",

            parse_mode="HTML",

            reply_markup=back_to_menu_kb()

        )

    except Exception as e:

        await wait.edit_text(

            f"❌ Xatolik:\n{e}"

        )


@router.message(
    AIState.waiting_message
)
async def ai_message(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    mode = data.get(
        "mode",
        "chat"
    )

    history = data.get(
        "history",
        []
    )

    wait = await message.answer(
        "⏳ AI o'ylamoqda..."
    )

    try:

        user_prompt = message.text


        if mode == "prompt":

            language = data.get(

                "prompt_language",

                "English"

            )

            user_prompt = f"""

Create this in {language}

USER IDEA:

{message.text}

Make it cinematic,
ultra detailed,
high quality,
AI optimized.

"""


        response = await get_ai_response(

            mode,

            user_prompt,

            history

        )

    except Exception as e:

        response = f"❌ Xatolik:\n{e}"


    try:

        await wait.delete()

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
        -(MAX_HISTORY * 2):
    ]


    await state.update_data(

        history=history

    )


    label = MODE_LABELS.get(
        mode,
        "AI"
    )


    await message.answer(

        f"<b>{label}</b>\n\n"

        f"<pre>{response}</pre>",

        parse_mode="HTML",

        reply_markup=back_to_menu_kb()

    )
```
