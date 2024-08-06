import os

from openai import OpenAI
from pathlib import Path
from typing_extensions import override
from openai import AssistantEventHandler
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create a vector store for book chapter
vector_store = client.beta.vector_stores.create(name="PPL Book Chapter 1")

# Ready the files for upload to OpenAI
file_paths = ["book_chapters/chapter_1.pdf"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

teaching_instructions = Path('teaching_prompt_lecture_1.txt').read_text()
assistant = client.beta.assistants.create(
    name="PPL Instructor",
    instructions=teaching_instructions,
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))



# Create a thread
thread = client.beta.threads.create()

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content=user_input
    )
    with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="",
            event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

# We use the `stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.



