import openai

def customer_service_chat(prompt):
    openai.api_key = current_app.config['OPENAI_API_KEY']
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
