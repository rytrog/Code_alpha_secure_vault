from .groq_client import generate_response
from .prompt_builder import build_daily_report_prompt


async def generate_daily_report(stats: dict) -> str:
    prompt = build_daily_report_prompt(stats)
    return await generate_response(prompt, max_tokens=4096)
