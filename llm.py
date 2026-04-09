# llm.py
# llm.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=api_key)

# Better config (important for interview quality)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={
        "temperature": 0.3,   # less randomness → better technical questions
        "max_output_tokens": 500
    }
)


def ask_llm(prompt, history=None):
    """
    Sends prompt + history to Gemini and returns response.
    Handles errors safely.
    """

    try:
        messages = []

        # Convert history to Gemini format
        if history:
            for h in history:
                role = "user" if h["role"] == "user" else "model"
                messages.append({
                    "role": role,
                    "parts": [h["content"]]
                })

        # Add current prompt
        messages.append({
            "role": "user",
            "parts": [prompt]
        })

        response = model.generate_content(messages)

        # Safe extraction
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        # Fallback if structure differs
        return str(response)

    except Exception as e:
        return f"⚠️ Error communicating with AI: {str(e)}"