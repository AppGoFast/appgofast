from google import genai

PROMPT ='''
You are a senior .NET performance engineer.

Framework: DevExpress.

You will receive profiling data from a .NET profiler.
The data contains the top functions by execution time.

Your task:
1. Identify the performance bottleneck
2. Explain why it might be happening
3. Suggest concrete optimizations
4. Mention DevExpress-specific improvements if relevant

Profiling data:
'''

def analyze_with_gemini(profiler_output_string: str, api_key: str):
    client = genai.Client(api_key=api_key)
    prompt = PROMPT + profiler_output_string
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview", contents=prompt
    )
    return response.text
