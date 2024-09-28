# instructor_bot

1. Ensure that `pip`, `python3` is already installed.
2. Preferably, create a new virtual environment for running the code in this repository.
3. You will also need an OpenAI API key for running the code in this repository.
5. Within the virtual environment:
    1. install all the dependencies using `pip install -r requirements.txt`
    2. Once you have the OpenAI API key, copy it to `~/.streamlit/secrets.toml` as `OPENAI_API_KEY = "YOUR_API_KEY_GOES_HERE"`
    3. Run the instructor bot using `streamlit run instructor_bot_streamlit.py`
         1. The above command will open a browser window with the following url: `http://localhost:8502/` and it will also show an error.
         2. Get rid of the error by modifying the url as `http://localhost:8502/?lecture_no=2` where `2` is the lecture number. You can replace it with any lecture you want to study.
    4. Run the evaluation bot using `streamlit run instructor_bot_streamlit.py`
         1. The above command will open a browser window with the following url: `http://localhost:8502/` and it will also show an error.
         2. Get rid of the error by modifying the url as `http://localhost:8502/?lecture_no=2` where `2` is the lecture number. You can replace it with any lecture on which you want to take the evaluation.


# Chainlit specific instructions

1. As of now, all the changes related to `chainlit` are in `chainlit` branch. Please keep it that way only.
2. For every new lecture:
   1. First add the book chapter for this lecture in `book_chapters` directory.
   2. Add the prompts for `instructor_bot` and `evaluation_bot` in `prompts` folder. 
   2. Run `python3 create_vector_store.py` to create the vector store for that lecture.
   2. Add `VECTOR_STORE_ID_PPL_LECTURE_<lecture_no>="<vector_store_id>"` to the `.env` 
      file. Replace `<lecture_no>` by the actual lecture no. and `<vector_store_id>` by the vector store id 
      receieved in step 1.
   3. Run `python3 create_instructor_assistant.py` to create the instructor_bot_assistant for this lecture.
   4. Add `INSTRUCTOR_ASSISTANT_ID_LECTURE_<lecture_no>="<assistant_id>"` to the `.env` 
      file. Replace `<lecture_no>` by the actual lecture no. and `<assistant_id>` by the assistant id 
      recieved in step 3.
   5. Run `python3 create_evaluation_assistant.py` to create the evaluation_bot_assistant for this lecture.
   6. Add `EVALUATION_ASSISTANT_ID_LECTURE_<lecture_no>="<assistant_id>"` to the `.env` 
      file. Replace `<lecture_no>` by the actual lecture no. and `<assistant_id>` by the assistant id 
      recieved in step 3.
   7. To test the `instructor_bot`, run `chainlit run chainlit/instructor_bot.py --host=localhost --port=8000 --headless`
   8. To test the `evaluation_bot`, run `chainlit run chainlit/evaluation_bot.py --host=localhost --port=8000 --headless`