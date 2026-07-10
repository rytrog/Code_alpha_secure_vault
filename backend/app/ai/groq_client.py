import os
from groq import Groq
from ..config import settings
from ..utils.logger import ai_logger

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = settings.GROQ_API_KEY
        if not api_key or api_key == "your-groq-api-key-here" or api_key.startswith("your-"):
            ai_logger.warning("Groq API key not configured - AI features will use fallback responses")
            return None
        try:
            _client = Groq(api_key=api_key)
            ai_logger.info("Groq client initialized")
        except Exception as e:
            ai_logger.error(f"Failed to initialize Groq client: {e}")
            return None
    return _client


async def generate_response(prompt: str, max_tokens: int = 2048) -> str:
    """Generate a response from Groq using llama-3.3-70b-versatile."""
    client = get_client()
    if client is None:
        return _fallback_response(prompt)
    try:
        # Request completion from Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=0.7,
            timeout=15.0
        )
        ai_logger.info("AI response generated from Groq")
        return chat_completion.choices[0].message.content
    except Exception as e:
        ai_logger.error(f"Groq API error: {e}")
        err_msg = str(e).lower()
        if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
            return (
                "AI analysis is temporarily unavailable because your Groq API rate limit has been reached. "
                "Please try again in a few moments or upgrade your usage plan."
            )
        elif "api_key" in err_msg or "invalid" in err_msg or "authentication" in err_msg:
            return (
                "AI analysis is unavailable due to an invalid Groq API Key. "
                "Please verify that the GROQ_API_KEY in your backend/.env file is correct."
            )
        return f"AI Engine error: {e}"


def _fallback_response(prompt: str) -> str:
    """Fallback when Groq is not configured."""
    return (
        "AI analysis is currently unavailable. Please configure your Groq API key "
        "in the .env file to enable AI-powered security analysis features. "
        "Set GROQ_API_KEY=your-actual-key in backend/.env"
    )
