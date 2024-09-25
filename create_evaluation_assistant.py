import os

from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# create the OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# set the lecture number
lecture_no = int(input("Enter the lecture number: "))
print(f"The evaluation assistant will be created for lecture number {lecture_no}.")

# fetch the vector store id
vector_store_id = os.getenv("VECTOR_STORE_ID_PPL_LECTURE_{0}".format(lecture_no))

# set the prompt file
prompt_file = './prompts/evaluation_prompts/evaluation_prompt_lecture_{0}.txt'.format(lecture_no)
print(f"Name of prompt file: {prompt_file}")

# fetch the system prompt
instructions = Path(prompt_file).read_text()
assistant = client.beta.assistants.create(
    name=f"PPL Evaluation Bot for Lecture {lecture_no}",
    instructions=instructions,
    model="gpt-4o-mini",
    # model="gpt-4o",
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
)
# assistant = client.beta.assistants.update(
#     assistant_id=assistant.id,
#     tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
# )

print(f"Assistant ID for Evaluation Bot for Lecture no. {lecture_no}: {assistant.id}")