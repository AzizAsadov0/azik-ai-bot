from aiogram import Router

from aiogram.types import (
    Message,
    FSInputFile
)

from services.image_service import (
    generate_image
)

router = Router()


@router.message()
async def image_handler(
    message: Message
):

    prompt = message.text

    wait = await message.answer(

        "🎨 AI rasm yaratilmoqda..."

    )

    try:

        image_bytes = await generate_image(
            prompt
        )

        with open(
            "generated.png",
            "wb"
        ) as f:

            f.write(image_bytes)

        photo = FSInputFile(
            "generated.png"
        )

        await wait.delete()

        await message.answer_photo(

            photo=photo,

            caption=(
                "✅ Rasm tayyor"
            )

        )

    except Exception as e:

        await wait.edit_text(

            f"❌ Xatolik:\n{e}"

        )


