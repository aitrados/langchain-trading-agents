import json
from copy import deepcopy
from datetime import datetime
from typing import Optional, List

from aitrados_api.common_lib.tools.toml_manager import TomlManager
from fastmcp import Client
from finance_trading_ai_agents_mcp.assistive_tools.aitrados_mcp_client import AitradosMcpClient
from finance_trading_ai_agents_mcp.assistive_tools.assistive_tools_utils import get_basic_system_function_call_prompt
from finance_trading_ai_agents_mcp.assistive_tools.mcp_tools_converter import McpListToolsConverter
from finance_trading_ai_agents_mcp.parameter_validator.analysis_departments import analysis_department

from langchain.agents import create_agent
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, ListOutputParser, XMLOutputParser
from loguru import logger

from langchain_trading_agents.assistive_tools.assistive_tools_utils import auto_replace_string_placeholder, \
    get_all_traditional_indicator_names, get_analyst_prompt
from langchain_trading_agents.contant import LLM_CONVERSATION_SUB_TOPIC, ConversationData, ConvMessageType
from langchain_trading_agents.llm_model.ai_message_progress import AiMessageProcess
from langchain_trading_agents.llm_model.model_factory import get_llm_model

from aitrados_api.trade_middleware.publisher import async_publisher_instance

from langchain_trading_agents.utils.common_utils import auto_load_global_config, get_or_create_conversation_id


class BaseSubAgent:
    nickname = "anonymous"
    department = "unknown"



    def __init__(self, provider: str,
                 model_name: str,
                 role_prompt: str = None,
                 profile: str = None,
                 nickname: str = None,
                 system_prompt_lang:str=None,
                 role_prompt_file_or_url:str=None,
                 profile_file_or_url:str=None,
                 placeholder_map: dict = None,
                 custom_mcp_department:Optional[List[str]|str]=None,
                 output_parser:Optional[JsonOutputParser|StrOutputParser|ListOutputParser|XMLOutputParser]=None,
                 **kwargs):
        """
        Initialize the base sub-agent.

        Args:
            provider (str): LLM model provider, such as 'openai', 'ollama', 'gemini', etc.
            model_name (str): Specific model name, such as 'gpt-4', 'claude-3-opus', etc.
            role_prompt (str, optional): Role prompt that defines the agent's behavior and responsibilities.
                                       If not provided, will be retrieved from files or default configuration.
                                       Defaults to None.
                                       If both role_prompt and role_prompt_file_or_url are not provided,
                                       the system will retrieve from langchain_trading_agents/assistive_tools/*system_prompt_words folder.
            profile (str, optional): Agent's personal profile description. If not provided, will be retrieved
                                    from files or default configuration. Currently manager and decision maker require profile parameter.
                                    Defaults to None.
                                    If both profile and profile_file_or_url are not provided,
                                    the system will retrieve from langchain_trading_agents/assistive_tools/*system_prompt_words folder.
            nickname (str, optional): Agent's nickname. If not provided, will use the default nickname
                                     from class attributes. Defaults to None.
            system_prompt_lang (str, optional): Language of system prompts, such as 'en', 'fr', 'zh_cn', etc.
                                              If not provided, will read the default language from configuration file.
                                              Defaults to None.
                                              Detailed definitions are available in finance_trading_ai_agents_mcp/utils/contant.py SystemPromptLanguage.
            role_prompt_file_or_url (str, optional): File path or URL for role prompt.
                                                   Used to load prompts from external resources. Defaults to None.
                                                   If both role_prompt and role_prompt_file_or_url are not provided,
                                                   the system will retrieve from langchain_trading_agents/assistive_tools/*system_prompt_words folder.
            profile_file_or_url (str, optional): File path or URL for personal profile. Currently manager and decision maker require profile parameter.
                                               If both profile and profile_file_or_url are not provided,
                                               the system will retrieve from langchain_trading_agents/assistive_tools/*system_prompt_words folder.
            placeholder_map (dict, optional): Placeholder replacement mapping table for replacing specific placeholders in prompts.
                                            For example {'{symbol}': 'BTC', '{timeframe}': '1d'}. Defaults to None.
                                            Currently automatically replaceable placeholders are:
                                                    {basic_system_function_call_prompt}
                                                    {all_traditional_indicator_names}
                                                    {available_agent_profiles}
                                                    {current_datetime}
            custom_mcp_department:Optional[List[str]|str]:custom_mcp_department values are from http://127.0.0.1:11999/mcp_servers.json.
            example: Trading account information can be accessed by both decision-makers and managers. Therefore, custom_mcp_department="broker"

            **kwargs: Other parameters passed to the LLM model, such as temperature, max_tokens, etc.

        Raises:
            ValueError: Raised when required parameters are missing
            ImportError: Raised when related dependency packages are not installed

        Note:
            - If both role_prompt and role_prompt_file_or_url are not provided, will use department default prompts
            - If both profile and profile_file_or_url are not provided, will use department default profiles
            - Placeholders in placeholder_map will be replaced with actual content at runtime
            - Subclasses should set the department class attribute to determine the agent's department type
        """

        if not provider or not model_name:
            raise ValueError("Required parameters are missing: provider and model_name.please check config.toml")
        auto_load_global_config()
        self.provider=provider
        self.model_name=model_name
        self.system_prompt_lang = system_prompt_lang
        self.role_prompt = role_prompt
        self.model = get_llm_model(provider, model_name, **kwargs)
        self.profile = profile
        self.temperature=kwargs.get("temperature",0)
        self.placeholder_map = placeholder_map or {}
        self.custom_mcp_department=custom_mcp_department
        self.role_prompt_file_or_url = role_prompt_file_or_url
        self.profile_file_or_url = profile_file_or_url
        self.output_parse=output_parser

        self._agent = None
        self._bus_control = None
        self.conversation_id = None

        self.model_config = deepcopy(kwargs)

        self.__params = {
            "provider": provider,
            "model_name": model_name,
            "role_prompt": role_prompt,
            "profile": profile,
            "nickname": nickname,
            "system_prompt_lang": system_prompt_lang,
            "role_prompt_file_or_url": role_prompt_file_or_url,
            "profile_file_or_url": profile_file_or_url,
            "placeholder_map": placeholder_map,
            "kwargs": kwargs
        }

        self.__is_inited_data=False

    def init_data(self):
        if self.__is_inited_data:
            return
        self.__is_inited_data = True
        params=self.__params
        self.model_config["provider"] = params["provider"]
        self.model_config["model_name"] = params["model_name"]
        if "api_key" in self.model_config:
            self.model_config.pop("api_key")
        if "secret_key" in self.model_config:
            self.model_config.pop("secret_key")
        if "token" in self.model_config:
            self.model_config.pop("secret_key")

        if params["nickname"]:
            self.nickname = params["nickname"]
        if not params["system_prompt_lang"]:
            self.system_prompt_lang = TomlManager.get_value("default_system_prompt_lang", "en")

        if not params["role_prompt"]:
            self.role_prompt = get_analyst_prompt(self.department, lang=self.system_prompt_lang,
                                                  file_or_url=params["role_prompt_file_or_url"])
        self.role_prompt = self.get_replace_placeholder_prompt(self.role_prompt)
        if not params["profile"]:
            self.profile = get_analyst_prompt(self.department, lang=self.system_prompt_lang, is_profile=True,
                                              file_or_url=params["profile_file_or_url"])

        self.profile = self.get_replace_placeholder_prompt(self.profile)
        if self.department == analysis_department.TRADITIONAL_INDICATOR:

            pass


    def get_replace_placeholder_prompt(self, prompt: str):
        def _is_append(key):
            if key in self.placeholder_map:
                return False
            temp_key = '{' + str(key) + '}'

            if temp_key not in prompt:
                return False
            return True


        if _is_append("current_datetime"):
            self.placeholder_map["current_datetime"]=datetime.now().astimezone().isoformat()
        if _is_append("basic_system_function_call_prompt"):
            self.placeholder_map["basic_system_function_call_prompt"] = get_basic_system_function_call_prompt(
                self.system_prompt_lang)
        if _is_append("all_traditional_indicator_names"):
            self.placeholder_map["all_traditional_indicator_names"] = get_all_traditional_indicator_names()

        if _is_append("available_agent_profiles"):
            available_agent_profiles=""
            for agent in self._bus_control.sub_agent_registry.values():
                available_agent_profiles+=f"### {agent.department} department:\n {agent.profile}\n\n"

            self.placeholder_map["available_agent_profiles"] = available_agent_profiles
            pass

        if self.placeholder_map:
            prompt = auto_replace_string_placeholder(prompt, **self.placeholder_map)
        return prompt

    @classmethod
    def _get_role_kwargs(cls, default_params: dict, **kwargs):
        for key, value in default_params.items():
            if key not in kwargs:
                kwargs[key] = value
        return kwargs

    async def _send_pub(self, conv_message_type: str, content: str,usage_metadata=None):
        conv_data = ConversationData(
            conversation_id=self.conversation_id,
            department=self.department,
            nickname=self.nickname,
            conv_message_type=conv_message_type,
            content=content,
            llm_model_config=self.model_config,
            usage_metadata=usage_metadata
        ).model_dump_json()
        await async_publisher_instance.a_send_topic(LLM_CONVERSATION_SUB_TOPIC, conv_data)

    async def analyze_without_tools(self, user_query: str, conversation_id: str = None, ):
        self.conversation_id = get_or_create_conversation_id(conversation_id)

        self.init_data()


        await self._send_pub(ConvMessageType.SYSTEM_PROMPT, self.role_prompt)

        self._agent = create_agent(
            model=self.model.raw_model,
            system_prompt=self.role_prompt
        )
        op = AiMessageProcess(
            self,
            client=None,
        )
        result = await op.a_invoke(user_query, conversation_id=conversation_id)
        return result



    async def analyze(self, user_query: str, conversation_id: str = None, ):
        self.conversation_id = get_or_create_conversation_id(conversation_id)
        self.init_data()
        temp_department=self.department
        if self.custom_mcp_department:
            temp_department=self.custom_mcp_department




        async with AitradosMcpClient(departments=temp_department) as mcp_client:
            if not mcp_client.client:
                erro=f"""MCP server for department '{temp_department}' not found in MCP configuration.check them on http://127.0.0.1:11999/mcp_servers.json
                        Possible causes:
                        The local MCP server is not running. you can run 'finance-trading-ai-agents-mcp' command to start it with the most simple way.
                        If the department is broker, have you configured MCP to automatically start trading accounts? Check config.toml and the auto_run_brokers=['your-broker-key'] setting.Or remove 'custom_mcp_department' parameter on the {self.department} department.
                """

                logger.error(erro)
                return erro

            client: Client = mcp_client.client
            tools = await McpListToolsConverter(client).get_result(output_type="list")
            self._agent = create_agent(
                tools=tools,
                model=self.model.raw_model,
                system_prompt=self.role_prompt
            )

            op = AiMessageProcess(
                self,
                client=client,
            )
            await self._send_pub(ConvMessageType.SYSTEM_PROMPT, self.role_prompt)
            await self._send_pub(ConvMessageType.TOOLS, json.dumps(tools))

            result = await op.a_invoke(user_query, conversation_id=conversation_id)
            return result


