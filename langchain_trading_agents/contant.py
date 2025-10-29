from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelProvider:
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    HUGGINGFACE = "huggingface"
    XAI = "xai"
    #OTHER="other"
    @classmethod
    def get_array(cls):
        return [cls.OPENAI, cls.OLLAMA, cls.GEMINI, cls.ANTHROPIC, cls.QWEN, cls.DEEPSEEK, cls.HUGGINGFACE, cls.XAI]


class ConvMessageType:
    AI="ai"
    HUMAN="human"
    SYSTEM_PROMPT="system_prompt"
    CALL_TOOL="call_tool"
    TOOLS="tools"
    OTHER="other"
    ERROR = "error"


class ConversationData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    department: str = Field(description="Department or agent responsible for this message")
    conv_message_type: str = Field(
        description="LangChain message type, such as system_prompt, ai, human, tool,call_tool, etc.")
    conversation_id: str = Field(description="Unique identifier for the conversation")

    nickname: str = Field(description="Nickname or display name of the agent/user")

    content: str = Field(description="Content of the message")
    llm_model_config:Optional[dict]=Field(default=None,description="llm model config")

    usage_metadata:Optional[dict]=Field(default=None,description="llm usage")
    timestamp: str = Field(default_factory=lambda: datetime.now().astimezone().isoformat(), description="ISO format timestamp when the message was created")




LLM_CONVERSATION_SUB_TOPIC="on_llm_conversation"