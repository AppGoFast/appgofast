from google import genai


def analyze_with_gemini(prompt: str, api_key: str, model: str = "gemini-3.1-flash-lite-preview"):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model, contents=prompt
    )
    return response.text
