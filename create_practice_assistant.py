import os

from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# create the OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OOP_OPENAI_API_KEY"))

prompt_file = './courses/oop/prompts/practice_bot_quiz_1.txt'
print(f"Name of prompt file: {prompt_file}")
assistant_name = f"OOP Practice Assistant for Quiz-1"

instructions = Path(prompt_file).read_text()
assistant = client.beta.assistants.create(
    name=assistant_name,
    instructions=instructions,
    # model="gpt-4o-mini",
    model="gpt-4o",
)
print(f"Assistant ID for {assistant_name}: {assistant.id}")