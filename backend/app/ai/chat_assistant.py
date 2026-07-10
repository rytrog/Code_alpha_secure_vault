from .groq_client import generate_response
from .prompt_builder import build_chat_prompt


async def chat_with_assistant(user_message: str, context: str, chat_history: str = "") -> str:
    prompt = build_chat_prompt(user_message, context, chat_history)
    return await generate_response(prompt)
