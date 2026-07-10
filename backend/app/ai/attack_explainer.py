from .groq_client import generate_response
from .prompt_builder import build_attack_explanation_prompt


async def explain_attack(attack_data: dict) -> str:
    prompt = build_attack_explanation_prompt(attack_data)
    return await generate_response(prompt)
