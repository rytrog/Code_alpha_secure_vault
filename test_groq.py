#!/usr/bin/env python3
"""
SentinelX - Groq Cloud API connectivity verification script.
Tests environment configuration and performs a test query to check Groq API keys.
"""

import os
import sys

def parse_env_file(env_path):
    """Fallback manual parser for .env if python-dotenv is not available."""
    config = {}
    if not os.path.exists(env_path):
        return config
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    return config

def main():
    print("=" * 60)
    print("           SentinelX - Groq API Connection Test")
    print("=" * 60)

    # 1. Locate and load .env file
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", ".env")
    print(f"[*] Reading configuration from: {env_path}")
    
    # Parse .env file directly to avoid crossing with PC's local environment variables
    config = parse_env_file(env_path)
    api_key = config.get("GROQ_API_KEY")
    print("[+] Loaded API Key directly from backend/.env (bypassed PC system env)")

    # 2. Validate API Key configuration
    if not api_key:
        print("[X] Error: GROQ_API_KEY variable is missing or empty in .env")
        sys.exit(1)
        
    if api_key == "your-groq-api-key-here" or api_key.startswith("your-"):
        print("[X] Error: GROQ_API_KEY is still using the default placeholder value.")
        print("    Please replace the placeholder with your actual Groq Cloud API key in backend/.env")
        sys.exit(1)

    print(f"[*] API Key found: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}")

    # 3. Import groq package
    try:
        from groq import Groq
        print("[+] groq module imported successfully")
    except ImportError:
        print("[X] Error: groq package is not installed.")
        print("    Please run: pip install groq")
        sys.exit(1)

    # 4. Attempt API call
    print("[*] Initiating connection to Groq API (llama-3.3-70b-versatile)...")
    try:
        client = Groq(api_key=api_key)
        
        test_prompt = "Perform a quick system health check. Reply in one short sentence starting with 'Groq API is fully operational' and briefly state that Llama 3 is ready."
        print(f"[*] Sending test prompt: '{test_prompt}'")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": test_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=100,
            timeout=15.0
        )
        
        print("\n" + "=" * 60)
        print("                         TEST SUCCESSFUL")
        print("=" * 60)
        print(f"Response from Groq:\n{chat_completion.choices[0].message.content.strip()}")
        print("=" * 60)
        print("[+] Your Groq API key is configured correctly and works perfectly!")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("                           TEST FAILED")
        print("=" * 60)
        print(f"[X] Error communicating with Groq API: {str(e)}")
        print("=" * 60)
        print("Troubleshooting steps:")
        
        err_msg = str(e).lower()
        if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
            print(">>> RATE LIMIT / QUOTA EXCEEDED")
            print("Your Groq API Key is valid, but you have hit a rate limit or exhausted your plan's request quota.")
            print("Please retry in a few moments, or check your usage metrics on the Groq Console.")
        elif "api_key" in err_msg or "invalid" in err_msg or "auth" in err_msg:
            print(">>> AUTHENTICATION ERROR")
            print("Please check that the GROQ_API_KEY in backend/.env is valid and active.")
        else:
            print("1. Double check that your API key in backend/.env is correct.")
            print("2. Ensure your machine has active internet access.")
            print("3. Check for firewalls or proxy configurations blocking the api.groq.com endpoint.")
        sys.exit(1)

if __name__ == "__main__":
    main()
