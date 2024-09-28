import os
from typing import Dict, Optional
import chainlit as cl
from langchain_core.messages import convert_to_messages
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from openai.lib.streaming import AsyncAssistantEventHandler
from chainlit.types import ThreadDict
import chainlit.data as cl_data
from chainlit.logger import logger

load_dotenv()
async_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

max_lecture_no = os.getenv("MAX_LECTURE_NUMBER")

class CustomDataLayer(cl_data.LiteralDataLayer):
    def __init__(self, api_key: str, server: Optional[str]):
        from literalai import AsyncLiteralClient

        self.client = AsyncLiteralClient(api_key=api_key, url=server)
        logger.info("Chainlit data layer initialized for instructor bot")


literal_api_key = os.getenv("LITERAL_API_KEY_INSTRUCTOR_BOT")
literal_api_url = None
cl_data._data_layer = CustomDataLayer(api_key=literal_api_key, server=literal_api_url)

class EventHandler(AsyncAssistantEventHandler):

    def __init__(self, assistant_name: str) -> None:
        super().__init__()
        self.current_message: cl.Message = None
        self.assistant_name = assistant_name

    async def on_text_created(self, text) -> None:
        self.current_message = await cl.Message(author=self.assistant_name, content="").send()

    async def on_text_delta(self, delta, snapshot):
        if delta.value:
            await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        await self.current_message.update()

    async def on_event(self, event):
        if event.event == "error":
            return cl.ErrorMessage(content=str(event.data.message)).send()

    async def on_exception(self, exception: Exception):
        return cl.ErrorMessage(content=str(exception)).send()

@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, str],
        default_user: cl.User,
) -> Optional[cl.User]:
    return default_user

@cl.on_chat_start
async def start_chat():
    introductory_message = f"""
## Welcome to the Principles of Programming Language Course

### **Please enter the lecture number you wish to learn about.**  
   For example, if you want to learn about lecture number 4, please enter: **`4`**.

### **Please note that currently the bot supports conversations for up to lecture number `{max_lecture_no}`.**

### **Whenever you want to end the conversation, please enter:** `END`.
### Once you end the conversation, you will be allowed to download a text file having your full conversation with the bot. This file can be directly uploaded to Nalanda.
    """
    await cl.Message(content=introductory_message).send()


async def save_conversation_history(message):
    messages = cl.chat_context.to_openai()
    messages = convert_to_messages(messages)
    dir_path = './.chat_history'
    os.makedirs(dir_path, exist_ok=True)
    file_name = "chat_session_{0}.txt".format(cl.user_session.get('id'))
    file_path = os.path.join(dir_path, file_name)

    # Write the strings to the file
    with open(file_path, 'w') as f:
        for message in messages:
            f.write(message.pretty_repr() + '\n')

    print(f"Chat history saved at: {file_path}")

    elements = [
        cl.File(
            name=file_name,
            path=file_path,
            display="inline",
        ),
    ]

    await cl.Message(
        content="Please download this file and upload it on Nalanda", elements=elements
    ).send()
    os.remove(file_path)



@cl.on_message
async def main(message: cl.Message):
    if cl.user_session.get("lecture_no") is None:
        await set_initial_user_session_keys(message)
    else:
        if message.content.strip() == "END":
            await save_conversation_history(message)
        else:
            await converse_with_llm(message)


async def set_initial_user_session_keys(message):
    lecture_no = message.content.strip()
    # Check if the string is a valid natural number
    if lecture_no.isdigit():
        number = int(lecture_no)
        if 0 < number <= int(max_lecture_no):
            cl.user_session.set("lecture_no", lecture_no)
            assistant = sync_openai_client.beta.assistants.retrieve(
                os.getenv(f"INSTRUCTOR_ASSISTANT_ID_LECTURE_{lecture_no}")
            )
            cl.user_session.set("assistant", assistant)
            cl.user_session.set("assistant_id", assistant.id)
            cl.user_session.set("assistant_name", assistant.name)

            # Create a Thread
            thread = await async_openai_client.beta.threads.create()

            # Store thread ID in user session for later use
            cl.user_session.set("thread_id", thread.id)
            await cl.Message(content=f"Thanks, we will now start going through the lecture "
                                     f"content for Lecture No. {lecture_no}. Are you ready?").send()
        else:
            await cl.Message(content="Invalid Lecture No. Please enter the correct lecture no.").send()
    else:
        # Raise an error if the string contains anything other than a valid natural number
        await cl.Message(content="Invalid Lecture No. Please enter the correct lecture no.").send()


async def converse_with_llm(message):
    assistant_id = cl.user_session.get("assistant_id")
    assistant_name = cl.user_session.get("assistant_name")
    thread_id = cl.user_session.get("thread_id")
    # Add a Message to the Thread
    oai_message = await async_openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.content,
    )
    # Create and Stream a Run
    async with async_openai_client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            event_handler=EventHandler(assistant_name=assistant_name),
    ) as stream:
        await stream.until_done()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    pass