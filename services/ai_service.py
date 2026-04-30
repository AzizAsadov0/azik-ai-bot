import warnings
import random

from groq import AsyncGroq

with warnings.catch_warnings():

    warnings.simplefilter("ignore")

    import google.generativeai as genai


from config import (
    GROQ_API_KEY,
    GEMINI_API_KEY
)


if GEMINI_API_KEY:

    genai.configure(
        api_key=GEMINI_API_KEY
    )


groq_client = AsyncGroq(
    api_key=GROQ_API_KEY
)


MAX_HISTORY = 8


STYLE_SEEDS = [

    "luxury cinematic",

    "premium branding",

    "viral emotional",

    "psychological persuasion",

    "modern luxury",

    "high-conversion marketing",

]


SYSTEM_PROMPTS = {


    "ad": """

You are a WORLD-CLASS direct response copywriter.

TASK:

Create HIGH-CONVERTING advertisement copy
for the user's product or service.

STRICT RULES:

- NEVER write generic text
- NEVER repeat the user's words
- deeply understand the product
- focus on emotional desire
- focus on real benefits
- create urgency naturally
- use premium persuasive language
- write like a luxury modern brand
- make every sentence impactful
- avoid robotic structure
- avoid nonsense claims

STYLE:

- modern marketing
- psychological persuasion
- emotional triggers
- premium branding
- concise but powerful

FORMAT:

🔥 Hook

Short persuasive body

⚡ Strong CTA

Write ONLY in Uzbek language.

""",


    "content": """

You are an ELITE viral content strategist.

TASK:

Generate VIRAL content ideas
for the user's niche or business.

STRICT RULES:

- think like TikTok strategist
- think like Instagram Reels expert
- create scroll-stopping hooks
- use audience psychology
- use curiosity loops
- create retention-focused ideas
- avoid boring ideas
- every idea must feel visual
- every idea must feel modern
- avoid generic advice

FOR EACH IDEA INCLUDE:

1. Viral Hook
2. Video Concept
3. Scene Flow
4. Caption
5. CTA

Write ONLY in Uzbek language.

""",


    "script": """

You are a CINEMATIC short-form video scriptwriter.

TASK:

Write HIGH-RETENTION video scripts.

STRICT RULES:

- first 3 seconds must hook hard
- create curiosity instantly
- write scene-by-scene
- use emotional pacing
- use cinematic storytelling
- avoid boring dialogue
- every second must keep attention
- create visual moments
- create strong ending payoff

FORMAT:

1. Hook
2. Scene 1
3. Scene 2
4. Emotional Shift
5. Final CTA

Write ONLY in Uzbek language.

""",

    "translate": """

You are a STRICT professional translator.

TASK:

Translate the user's text accurately.

STRICT RULES:

- NEVER change the meaning
- NEVER summarize
- NEVER rewrite creatively
- NEVER add extra emotions
- NEVER remove details
- preserve sentence structure as much as possible
- preserve the original atmosphere
- preserve metaphors correctly
- preserve writing style
- preserve emotional tone
- make the translation natural and grammatically correct
- do not explain anything

IMPORTANT:

Translate AS CLOSE AS POSSIBLE
to the original text.

Return ONLY the translation.

""",


    "chat": """

You are a premium AI assistant.

STRICT RULES:

- respond intelligently
- sound natural and human
- avoid robotic responses
- be genuinely useful
- understand psychology
- understand business
- understand marketing
- understand coding
- explain clearly
- adapt to user tone
- avoid generic responses

Write ONLY in Uzbek language.

""",


    "prompt": """

You are a WORLD-CLASS AI prompt engineer.

TASK:

Turn the user's idea into
an ULTRA PROFESSIONAL AI IMAGE PROMPT.

STRICT RULES:

- cinematic lighting
- realistic textures
- realistic anatomy
- camera angles
- lens details
- composition
- color grading
- depth of field
- atmosphere details
- ultra realism
- visual storytelling
- premium photography language

The prompt must feel like it was written
by a Hollywood cinematic AI artist.

RETURN ONLY THE FINAL PROMPT.

Prompt language must be ENGLISH.

"""

}


def unique_style():

    return random.choice(
        STYLE_SEEDS
    )


async def ask_groq(

    mode: str,

    user_message: str,

    history: list | None = None

):

    if history is None:

        history = []


    system_prompt = SYSTEM_PROMPTS.get(

        mode,

        SYSTEM_PROMPTS["chat"]

    )


    messages = [

        {

            "role": "system",

            "content":

                f"{system_prompt}\n\n"

                f"STYLE: {unique_style()}"

        }

    ]


    for item in history[-MAX_HISTORY:]:

        messages.append(item)


    messages.append({

        "role": "user",

        "content": f"""

USER REQUEST:

{user_message}

IMPORTANT:

- deeply understand the request
- avoid generic responses
- avoid nonsense text
- make response modern
- make response premium
- make response useful

"""

    })


    response = await groq_client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=messages,

        temperature=0.7,

        max_tokens=1500,

    )


    return response.choices[0].message.content


async def ask_gemini(

    mode: str,

    user_message: str,

    history: list | None = None

):

    system_prompt = SYSTEM_PROMPTS.get(

        mode,

        SYSTEM_PROMPTS["chat"]

    )


    model = genai.GenerativeModel(

        model_name="gemini-2.0-flash",

        system_instruction=system_prompt,

    )


    response = model.generate_content(

        f"""

USER REQUEST:

{user_message}

IMPORTANT:

- deeply understand the request
- avoid generic responses
- avoid nonsense text
- make response premium
- make response modern

"""

    )


    return response.text


async def get_ai_response(

    mode: str,

    user_message: str,

    history: list | None = None

):

    if history is None:

        history = []


    gemini_modes = [

        "ad",

        "content",

        "script",

        "prompt",

        "translate"

    ]


    if mode in gemini_modes:

        try:

            return await ask_gemini(

                mode,

                user_message,

                history

            )

        except Exception as e:

            print(e)


    try:

        return await ask_groq(

            mode,

            user_message,

            history

        )

    except Exception as e:

        print(e)

        return (
            "AI vaqtincha javob bera olmayapti."
        )
