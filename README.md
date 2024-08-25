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
