import config
import openai

# Reference: https://platform.openai.com/docs/guides/chat

# Define a function to generate a response using ChatGPT
def generate_response(prompt):
    # stop response if Chinese characters are detected
    if any(u'\u4e00' <= c <= u'\u9fff' for c in prompt):
        return "An error occurred while generating the response."
    else:
    # try:
        openai.api_key = config.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            engine=config.OPENAI_ENGINE,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    # except:
    #     return "An error occurred while generating the response."
