import os

from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# create the OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# set the lecture number
lecture_no = int(input("Enter the lecture number: "))
print(f"The vector store will be created for lecture number {lecture_no}.")

# create the vector store
vector_store = client.beta.vector_stores.create(name="PPL Book Chapter {0}".format(lecture_no))

# Ready the files for upload to OpenAI
file_paths = ["./book_chapters/lecture_{0}.pdf".format(lecture_no)]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

print(f"Vector Store created with id: {vector_store.id}")