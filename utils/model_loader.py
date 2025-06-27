import os
import logging
from dotenv import load_dotenv
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field

from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ConfigLoader:
    def __init__(self):
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel):
    model_provider: Literal["groq", "openai", "google"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()

    class Config:
        arbitrary_types_allowed = True

    def load_llm(self):
        """
        Load and return the LLM model instance.
        """
        provider = self.model_provider
        cfg = self.config["llm"][provider]
        model_name = cfg["model_name"]

        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise EnvironmentError("Missing GROQ_API_KEY in environment variables")
            llm = ChatGroq(model=model_name, api_key=api_key)

        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "Missing OPENAI_API_KEY in environment variables"
                )
            llm = ChatOpenAI(model_name=model_name, api_key=api_key)

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "Missing GOOGLE_API_KEY in environment variables"
                )
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)

        else:
            raise ValueError(f"Unsupported model provider: {provider}")

        logger.info(f"Loaded {provider.upper()} model: {model_name}")
        return llm
