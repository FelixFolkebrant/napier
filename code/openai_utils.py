from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=openai_api_key)


def custom_response(mail_body, instructions):
    prompt = f"""
    {instructions}

    Aggera som kundsupport och skriv ett mejl som svarar på följande kundmejl:
    {mail_body}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "write a short story about a unicorn"},
        ],
    )

    print(response.choices[0].message.content)
