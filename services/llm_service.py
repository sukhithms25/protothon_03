from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_llm(prompt, image_b64=None):
    try:
        if image_b64:
            # Multi-modal request
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    {"inline_data": {"mime_type": "image/webp", "data": image_b64}},
                    prompt
                ]
            )
        else:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
        return response.text
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sorry, I encountered an error processing your request."