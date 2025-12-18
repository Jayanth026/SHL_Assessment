import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel("gemini-1.5-flash")

PROMPT_TEMPLATE = """
You are extracting structured fields from webpage text.

RULES:
- Extract ONLY information explicitly present in the text
- Do NOT infer or guess
- If information is missing, return empty string or 0
- Return STRICT JSON ONLY

Extract:
- description (string)
- duration_minutes (integer)

TEXT:
\"\"\"
{page_text}
\"\"\"
"""

def extract_with_gemini(page_text: str) -> dict:
    response = MODEL.generate_content(
        PROMPT_TEMPLATE.format(page_text=page_text),
        generation_config={
            "temperature": 0,
            "top_p": 1
        }
    )

    try:
        return json.loads(response.text)
    except Exception:
        return {
            "description": "",
            "duration_minutes": 0
        }
