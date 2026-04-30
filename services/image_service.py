import requests
import urllib.parse


async def generate_image(prompt):

    enhanced_prompt = f"""
    
    unique composition,
    
    different angle,
    
    ultra realistic,

    cinematic lighting,

    realistic skin texture,

    professional photography,

    4k quality,

    highly detailed,

    realistic shadows,

    premium quality,

    {prompt}

    """

    encoded = urllib.parse.quote(
        enhanced_prompt
    )

    import random

    seed = random.randint(
    1,
    999999999
    )

    url = (

    "https://image.pollinations.ai/prompt/"

    f"{encoded}"

    f"?seed={seed}"

    )

    response = requests.get(url)

    return response.content
