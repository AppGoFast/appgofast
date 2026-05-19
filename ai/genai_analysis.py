from google import genai


def analyze_with_gemini(prompt: str, api_key: str, model: str = "gemini-3.1-flash-lite-preview"):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model, contents=prompt
    )
    return response.text

def build_diagnostic_prompt(base_prompt: str, methods: list[dict], top_n: int, data_block: str, scenario: str = "unknown") -> str:
    prompt = base_prompt
    prompt = prompt.replace("{scenario}", scenario)
    prompt = prompt.replace("{total_methods}", str(len(methods)))
    prompt = prompt.replace("{top_n}", str(top_n))
    prompt = prompt.replace("{data_block}", data_block)
    return prompt

def build_investigation_prompt(base_prompt: str, bottlenecks: str, scenario: str = "unknown") -> str:
    prompt = base_prompt
    prompt = prompt.replace("{scenario}", scenario)
    prompt = prompt.replace("{bottlenecks}", bottlenecks)
    return prompt
