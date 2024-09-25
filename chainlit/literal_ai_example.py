import os
from literalai import LiteralClient
from dotenv import load_dotenv

load_dotenv()

# Not compatible with gunicorn's --preload flag
literal_client = LiteralClient(api_key=os.getenv("LITERAL_API_KEY"))

literal_client.instrument_openai()

# Run a regular OpenAI chat completion
from openai import OpenAI

oai = OpenAI()
# oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(user_input: str):
    oai.chat.completions.create(
        model="gpt-4o",
        messages=[{ "role": "user", "content": user_input }]
    )

call_openai("Hello world")