import os
import ast
import sys
from pathlib import Path
import streamlit as st
from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override
from openai.types.beta.threads import Text, TextDelta

class EventHandler(AssistantEventHandler):
    """
    Event handler for the assistant stream
    """
    @override
    def on_text_created(self, text: Text) -> None:
        """
        Handler for when a text is created
        """
        # Create a new text box
        st.session_state.text_boxes.append(st.empty())
        # Display the text in the newly created text box
        st.session_state.text_boxes[-1].info("".join(st.session_state["assistant_text"][-1]))

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        """
        Handler for when a text delta is created
        """
        # Clear the latest text box
        st.session_state.text_boxes[-1].empty()
        # If there is text written, add it to latest element in the assistant text list
        if delta.value:
            st.session_state.assistant_text[-1] += delta.value
        # Re-display the full text in the latest text box
        st.session_state.text_boxes[-1].info("".join(st.session_state["assistant_text"][-1]))

    def on_text_done(self, text: Text):
        """
        Handler for when text is done
        """
        # Create new text box and element in the assistant text list
        st.session_state.text_boxes.append(st.empty())
        st.session_state.assistant_text.append("")
        st.session_state.chat_history.append(("assistant", text.value))

# load_dotenv()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if 'lecture_no' not in st.session_state:
    lecture_no = st.query_params["lecture_no"]
    st.session_state.lecture_no = lecture_no
    st.session_state.prompt_file = 'prompts/evaluation_prompts/evaluation_prompt_lecture_{0}.txt'.format(
        st.session_state.lecture_no)
    print("\nName of prompt file: ", st.session_state.prompt_file)
    print("\n")

if 'vector_store_id' not in st.session_state:
    # Create a vector store for book chapter
    vector_store = client.beta.vector_stores.create(name="PPL Book Chapter {0}".format(st.session_state.lecture_no))

    # Ready the files for upload to OpenAI
    file_paths = ["book_chapters/lecture_{0}.pdf".format(st.session_state.lecture_no)]
    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # You can print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)
    st.session_state.vector_store_id = vector_store.id

teaching_instructions = Path(st.session_state.prompt_file).read_text()
assistant = client.beta.assistants.create(
    name="PPL Evaluator",
    instructions=teaching_instructions,
    model="gpt-4o-mini",
    # model="gpt-4o",
    tools=[{"type": "file_search"}],
)
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [st.session_state.vector_store_id]}},
)

# Initialize the OpenAI client
# client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))
#
# assistant = client.beta.assistants.create(
#     name="Assistant",
#     instructions="",
#     # tools=function_tools,
#     model="gpt-4o",
# )

st.title("💬 Evaluation Bot for PPL Lecture {0}".format(st.session_state.lecture_no))
"""
Please start interaction with the Evaluation Bot by typing in 'Hi', 'Hello' etc. 
"""

text_box = st.empty()


# Initialize chat history in session state if not already done
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = [""]

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

if "text_boxes" not in st.session_state:
    st.session_state.text_boxes = []

def display_chat_history():
    for role, content in st.session_state.chat_history:
        if role == "user":
            st.chat_message("User").write(content)
        else:
            st.chat_message("Assistant").write(content)

display_chat_history()

if prompt := st.chat_input("Enter your message"):
    st.session_state.chat_history.append(("user", prompt))

    # Assuming the user input is related to calculating tax
    # if "tax" in prompt.lower():  # You can adjust this condition based on your actual use case
    #     try:
    #         tax_result = calculate_tax(prompt)  # Assuming prompt contains revenue
    #         st.session_state.chat_history.append(
    #             ("assistant", f"Tax for revenue {tax_result['revenue']}: {tax_result['tax']}"))
    #     except ValueError as e:
    #         st.session_state.chat_history.append(("assistant", str(e)))

    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

    st.session_state.text_boxes.append(st.empty())
    st.session_state.text_boxes[-1].success(f" {prompt}")

    with client.beta.threads.runs.stream(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()