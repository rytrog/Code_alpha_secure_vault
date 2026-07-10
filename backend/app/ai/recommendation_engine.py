from .groq_client import generate_response
from .prompt_builder import build_recommendation_prompt


async def get_recommendations(stats: dict) -> str:
    prompt = build_recommendation_prompt(stats)
    return await generate_response(prompt)
