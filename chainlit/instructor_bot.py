import os
from typing import Dict, Optional

import chainlit as cl
from chainlit.config import config
from openai import OpenAI, AsyncOpenAI
from pathlib import Path
from dotenv import load_dotenv
from openai.lib.streaming import AsyncAssistantEventHandler
from openai.types.beta.threads.runs import RunStep

load_dotenv()
async_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant = sync_openai_client.beta.assistants.retrieve(
    os.getenv("INSTRUCTOR_ASSISTANT_ID_LECTURE_5")
)

# async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# sync_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# assistant = sync_openai_client.beta.assistants.retrieve(
#     os.environ.get("INSTRUCTOR_ASSISTANT_ID_LECTURE_5")
# )

# config.ui.name = assistant.name



class EventHandler(AsyncAssistantEventHandler):

    def __init__(self, assistant_name: str) -> None:
        super().__init__()
        self.current_message: cl.Message = None
        self.current_step: cl.Step = None
        # self.current_tool_call = None
        self.assistant_name = assistant_name

    # async def on_run_step_created(self, run_step: RunStep) -> None:
    #     cl.user_session.set("run_step", run_step)

    async def on_text_created(self, text) -> None:
        self.current_message = await cl.Message(author=self.assistant_name, content="").send()

    async def on_text_delta(self, delta, snapshot):
        if delta.value:
            await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        await self.current_message.update()
    #     if text.annotations:
    #         print(text.annotations)
    #         for annotation in text.annotations:
    #             if annotation.type == "file_path":
    #                 response = await async_openai_client.files.with_raw_response.content(annotation.file_path.file_id)
    #                 file_name = annotation.text.split("/")[-1]
    #                 try:
    #                     fig = plotly.io.from_json(response.content)
    #                     element = cl.Plotly(name=file_name, figure=fig)
    #                     await cl.Message(
    #                         content="",
    #                         elements=[element]).send()
    #                 except Exception as e:
    #                     element = cl.File(content=response.content, name=file_name)
    #                     await cl.Message(
    #                         content="",
    #                         elements=[element]).send()
    #                 # Hack to fix links
    #                 if annotation.text in self.current_message.content and element.chainlit_key:
    #                     self.current_message.content = self.current_message.content.replace(annotation.text, f"/project/file/{element.chainlit_key}?session_id={cl.context.session.id}")
    #                     await self.current_message.update()

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
    # app_user = cl.user_session.get("user")
    # Create a Thread
    thread = await async_openai_client.beta.threads.create()
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", thread.id)
    # introductory_message = (f"Hello {app_user.identifier},  Are you ready to start learning about the "
    #                         f"Principles of Programming "
    #                         f"Languages?")
    introductory_message = (f"Hello,  Are you ready to start learning about the "
                            f"Principles of Programming "
                            f"Languages?")
    await cl.Message(content=introductory_message).send()
@cl.on_stop
# async def stop_chat():
#     current_run_step: RunStep = cl.user_session.get("run_step")
#     if current_run_step:
#         await async_openai_client.beta.threads.runs.cancel(thread_id=current_run_step.thread_id, run_id=current_run_step.run_id)


@cl.on_message
async def main(message: cl.Message):
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
        assistant_id=assistant.id,
        event_handler=EventHandler(assistant_name=assistant.name),
    ) as stream:
        await stream.until_done()