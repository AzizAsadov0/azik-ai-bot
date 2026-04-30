from deep_translator import GoogleTranslator


LANGUAGES = {

    "ingliz": "en",
    "inglizcha": "en",

    "nemis": "de",
    "nemischa": "de",

    "rus": "ru",
    "ruscha": "ru",

    "fransuz": "fr",
    "fransuzcha": "fr",

    "turk": "tr",
    "turkcha": "tr",

    "arab": "ar",
    "arabcha": "ar",

    "ispan": "es",
    "ispancha": "es",

    "italyan": "it",
    "italyancha": "it",

    "o'zbek": "uz",
    "uzbek": "uz",

}


async def smart_translate(

    text,

    target_language

):

    lower = target_language.lower()

    target = "en"


    for key, code in LANGUAGES.items():

        if key in lower:

            target = code

            break


    result = GoogleTranslator(

        source="auto",

        target=target

    ).translate(text)


    return result
