# import os

# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI


# load_dotenv()


# def get_model():
#     api_key = os.getenv("GOOGLE_API_KEY")
#     model_name = os.getenv(
#         "GEMINI_MODEL",
#         "gemini-2.5-flash"
#     )

#     if not api_key:
#         raise ValueError(
#             "GOOGLE_API_KEY is missing. Check your .env file."
#         )

#     return ChatGoogleGenerativeAI(
#         model=model_name,
#         google_api_key=api_key,
#         temperature=0,
#     )




import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_model():
    api_key = os.getenv("GROQ_API_KEY")

    model_name = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Check your .env file."
        )

    return ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=0,
        max_retries=2,
    )
