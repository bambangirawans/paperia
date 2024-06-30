import openai

# Initialize OpenAI API client
openai.api_key = "YOUR_OPENAI_API_KEY"

def generate_response(user_message):
    try:
        # Call the OpenAI API to generate a response
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can use "gpt-3.5-turbo" or other available engines
            prompt=user_message,
            max_tokens=150,  # Adjust the response length as needed
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Extract the generated response from the API response
        generated_message = response.choices[0].text.strip()

        return {
            'status': 'success',
            'message': generated_message
        }

    except openai.OpenAIError as e:
        return {
            'status': 'error',
            'message': str(e)
        }

