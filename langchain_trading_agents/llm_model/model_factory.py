
"""
model_factory.py
Universal model adapter: supports OpenAI / Ollama / Gemini / Claude / Qwen / DeepSeek / HuggingFace / Grok and other platforms
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

from langchain_trading_agents.contant import ModelProvider



class BaseModelWrapper(ABC):
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs

    @abstractmethod
    async def invoke(self, messages: list[Dict[str, Any]]) -> str:
        pass

    @property
    @abstractmethod
    def raw_model(self):
        pass

    def supports_tools(self) -> bool:
        """Check if the underlying model supports tool binding"""
        return hasattr(self.raw_model, 'bind_tools')

    def bind_tools_if_supported(self, tools):
        """If tool binding is supported, bind it, otherwise return to the original model"""
        if self.supports_tools():
            try:
                return self.raw_model.bind_tools(tools=tools, tool_choice="auto")
            except Exception as e:
                print(f"Warning: Tool binding failed, using original model: {e}")
                return self.raw_model
        else:
            print(f"Model {self.model_name} does not support bind_tools, will rely on create_agent compatibility processing")
            return self.raw_model



class OpenAIModel(BaseModelWrapper):
    def __init__(self, model_name="gpt-4o-mini", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_openai` package. Please execute `pip install langchain-openai` and configure OPENAI_API_KEY."
            )
        self.model = ChatOpenAI(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class OllamaModel(BaseModelWrapper):
    def __init__(self, model_name="llama3", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_ollama` package. Please execute `pip install langchain-ollama`."
            )
        self.model = ChatOllama(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class GeminiModel(BaseModelWrapper):
    def __init__(self, model_name="gemini-pro", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_google_genai` package. Please execute `pip install langchain-google-genai` and configure GOOGLE_API_KEY."
            )
        self.model = ChatGoogleGenerativeAI(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class ClaudeModel(BaseModelWrapper):
    def __init__(self, model_name="claude-3-opus-20240229", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_anthropic` package. Please execute `pip install langchain-anthropic` and configure ANTHROPIC_API_KEY."
            )
        self.model = ChatAnthropic(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class QwenModel(BaseModelWrapper):
    def __init__(self, model_name="qwen-plus", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_community.chat_models import ChatTongyi
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_community` package. Please execute `pip install langchain-community` and configure DASHSCOPE_API_KEY."
            )
        self.model = ChatTongyi(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class DeepSeekModel(BaseModelWrapper):
    def __init__(self, model_name="deepseek-chat", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_deepseek import ChatDeepSeek
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_deepseek` package. Please execute `pip install langchain-deepseek` and configure DEEPSEEK_API_KEY."
            )
        self.model = ChatDeepSeek(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class HuggingfaceModel(BaseModelWrapper):
    def __init__(self, model_name="microsoft/DialoGPT-medium", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_huggingface import ChatHuggingFace
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_huggingface` package. Please execute `pip install langchain-huggingface` and configure HUGGINGFACE_API_KEY."
            )


        self.model = ChatHuggingFace(model=model_name, **kwargs)

    async def invoke(self, messages):
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


class GrokModel(BaseModelWrapper):
    def __init__(self, model_name: str = "grok-2", **kwargs):
        super().__init__(model_name, **kwargs)
        try:
            from langchain_xai import ChatXAI
        except ImportError:
            raise ImportError(
                "Unable to find `langchain_xai` package. Please execute `pip install langchain-xai` and configure XAI_API_KEY."
            )
        self.model = ChatXAI(model=model_name, **kwargs)

    async def invoke(self, messages: list[Dict[str, Any]]) -> str:
        response = await self.model.ainvoke({"messages": messages})
        return response["output"]

    @property
    def raw_model(self):
        return self.model


# === Factory Method ===

def get_llm_model(provider: str, model_name: str, **kwargs) -> BaseModelWrapper:
    """
    Factory method that returns a model wrapper corresponding to a provider.

    Args:
    provider: Model provider name
    model_name: Model name
    **kwargs: Additional parameters for the model

    Returns:
    BaseModelWrapper: The corresponding model wrapper instance

    Raises:
    ValueError: Raised when the provider is unsupported
    ImportError: Raised when the required package is not installed
    """
    provider = provider.lower()

    try:
        if provider == ModelProvider.OPENAI:
            return OpenAIModel(model_name, **kwargs)
        elif provider == ModelProvider.OLLAMA:
            return OllamaModel(model_name, **kwargs)
        elif provider == ModelProvider.GEMINI:
            return GeminiModel(model_name, **kwargs)
        elif provider == ModelProvider.ANTHROPIC:
            return ClaudeModel(model_name, **kwargs)
        elif provider == ModelProvider.QWEN:
            return QwenModel(model_name, **kwargs)
        elif provider == ModelProvider.DEEPSEEK:
            return DeepSeekModel(model_name, **kwargs)
        elif provider == ModelProvider.HUGGINGFACE:
            return HuggingfaceModel(model_name, **kwargs)
        elif provider == ModelProvider.XAI:
            return GrokModel(model_name, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {ModelProvider.get_array()}")
    except ImportError as e:

        raise ImportError(f"Failed to initialize {provider} model: {str(e)}")