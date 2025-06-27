# core/model_loader.py
import logging
import json
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, BaseMessage
from langchain_core.outputs import ChatResult
from typing import List, Any

from .config import settings

logger = logging.getLogger(__name__)


class GeminiSanitizer(ChatGoogleGenerativeAI):
    """
    A custom wrapper for ChatGoogleGenerativeAI that sanitizes ToolMessages
    to prevent the 'contents.parts must not be empty' error.
    This is the correct way to handle complex tool outputs for the Gemini API.
    """

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        """
        Intercepts messages, cleans them, and then calls the parent method.
        """
        sanitized_messages = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                # The Gemini API can fail if the content of a ToolMessage
                # is not a simple string. We ensure it is by JSON-dumping it.
                if not isinstance(msg.content, str):
                    msg.content = json.dumps(msg.content, indent=2)
            sanitized_messages.append(msg)

        # Call the original _generate method with the cleaned messages
        return super()._generate(sanitized_messages, **kwargs)


def get_llm():
    """
    Load and return the LLM model instance based on the configuration.
    """
    provider = settings.MODEL_PROVIDER.lower()

    if provider == "google":
        model_name = settings.GOOGLE_MODEL_NAME
        llm = GeminiSanitizer(model=model_name, google_api_key=settings.GOOGLE_API_KEY)
    elif provider == "openai":
        model_name = settings.OPENAI_MODEL_NAME
        llm = ChatOpenAI(model_name=model_name, api_key=settings.OPENAI_API_KEY)
    elif provider == "groq":
        model_name = settings.GROQ_MODEL_NAME
        llm = ChatGroq(model=model_name, api_key=settings.GROQ_API_KEY)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")

    logger.info(f"Loaded {provider.upper()} model: {model_name}")
    return llm
