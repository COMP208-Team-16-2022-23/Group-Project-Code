import config
import openai


# Reference: https://platform.openai.com/docs/guides/chat
def generate_response(prompt) -> str:
    # stop response if Chinese characters are detected
    if any(u'\u4e00' <= c <= u'\u9fff' for c in prompt):
        return "An error occurred while generating the response."

    system = "You are a helpful AI embedded in a data analysis platform. Answer as concisely as possible."

    openai.api_key = config.OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model=config.OPENAI_ENGINE,
        max_tokens=config.OPENAI_MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
    )
    # print(prompt)
    return response['choices'][0]['message']['content']
