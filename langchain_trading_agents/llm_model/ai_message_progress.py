import json
import os
import uuid
from typing import Dict, Any, List, Optional


from aitrados_api.common_lib.common import is_debug

from fastmcp import Client
from finance_trading_ai_agents_mcp.assistive_tools.mcp_tools_converter import LlmCallToolConverter
from loguru import logger

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from langchain_trading_agents.contant import  ConvMessageType

try:
    if os.getenv("LANGFUSE_SECRET_KEY", None) and os.getenv("LANGFUSE_PUBLIC_KEY", None) and os.getenv(
            "LANGFUSE_BASE_URL", None):
        from langchain_trading_agents.llm_model.langfuse_instance import langfuse_handler
    else:
        langfuse_handler = None

except:
    langfuse_handler = None


class AiMessageProcess:
    def __init__(self, sub_agent, client: Client = None):
        self.sub_agent = sub_agent
        self.client = client
        self.fun_call_count = 0
        self.conversation_id: str = None

    async def __a_invoke(self, messages: list):
        if langfuse_handler:
            result = await self.sub_agent._agent.ainvoke({"messages": messages},
                                                         config={"callbacks": [langfuse_handler]})
        else:
            result = await self.sub_agent._agent.ainvoke({"messages": messages})
        return result

    async def a_invoke(self, user_query, conversation_id: str = None):
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        self.conversation_id = conversation_id
        if is_debug():
            logger.debug(f"AI -> {self.sub_agent.department}:{self.sub_agent.nickname} ask:{user_query}")

        await self.sub_agent._send_pub(ConvMessageType.HUMAN, user_query)

        messages = [HumanMessage(content=user_query)]

        while True:
            result = await self.__a_invoke(messages)
            res_messages = result.get("messages", [])
            last_message = res_messages[-1]
            tool_calls = getattr(last_message, 'tool_calls', [])
            if not tool_calls:
                break

            if not await self.append_tool_messages(tool_calls, messages):
                break

        return await self._extract_final_answer(res_messages, user_query)

    async def _extract_final_answer(self, messages: List[Any], user_query) -> str:

        final_answer = "AI did not return any content.Please check your LLM configuration..."
        usage_metadata=None
        is_correct = False
        if messages:
            for message in reversed(messages):
                if hasattr(message, 'content') and message.content and message.content.strip():
                    if user_query != message.content:
                        is_correct = True
                        final_answer = message.content
                        if hasattr(message, 'usage_metadata'):
                            usage_metadata=message.usage_metadata

                        break

        await self.sub_agent._send_pub(ConvMessageType.AI if is_correct else ConvMessageType.ERROR, final_answer,usage_metadata=usage_metadata)
        return final_answer

    async def append_tool_messages(self, tool_calls: list, messages: list):
        is_appended = False
        if self.client is None:
            return is_appended
        tool_responses = await LlmCallToolConverter(self.client).execute_langchain_tool_call(tool_calls)

        tool_messages = []

        for i, tool_call in enumerate(tool_calls):
            tool_message = ToolMessage(
                name=tool_call["name"],
                content=json.dumps(tool_responses[i], ensure_ascii=False),
                tool_call_id=tool_call["id"]
            )

            self.fun_call_count += 1
            tool_name = tool_call.get('name', 'unknown')
            tool_args = tool_call.get('args', {})
            conv_content = f"NO.{self.fun_call_count}. {tool_name} - {tool_args}\n\n{tool_message.content}"
            await self.sub_agent._send_pub(ConvMessageType.CALL_TOOL, conv_content)

            if is_debug():
                logger.debug(
                    f"AI -> {self.sub_agent.department}:{self.sub_agent.nickname} deep thinking call : {self.fun_call_count}. {tool_name} - {tool_args}")

            tool_messages.append(tool_message)

        if tool_messages:
            is_appended = True
        messages.extend(tool_messages)
        return is_appended
