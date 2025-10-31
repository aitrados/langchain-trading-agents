from langfuse import get_client
from langfuse.langchain import CallbackHandler
langfuse = get_client()


langfuse_handler = CallbackHandler()