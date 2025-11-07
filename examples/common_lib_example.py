from time import sleep

from aitrados_api.common_lib.tools.toml_manager import TomlManager

from examples.my_async_subscriber import MyAsyncSubscriber
from langchain_trading_agents.utils.common_utils import get_llm_model_config


from langchain_trading_agents.contant import ModelProvider, LLM_CONVERSATION_SUB_TOPIC
from langchain_trading_agents.llm_model.sub_agents import IndicatorAnalyst,PriceActionAnalyst,EventAnalyst,NewsAnalyst
#TomlManager.load_toml_file(file=None)

from finance_trading_ai_agents_mcp.parameter_validator.analysis_departments import analysis_department
def run_MyAsyncSubscribe():
    #get help https://docs.aitrados.com/en/docs/api/trade_middleware/rpc_sub_client/
    subscriber = MyAsyncSubscriber()
    subscriber.run(is_thread=True)
    #To ensure that complete chat content can be collected, first ensure the subscription is fully activated.
    print("running AsyncSubscribe.you can find reports in ./conversation_record/**.md")
    sleep(0.1)
    subscriber.subscribe_topics(LLM_CONVERSATION_SUB_TOPIC)
    from aitrados_api.trade_middleware_service.trade_middleware_identity import aitrados_api_identity
    #subscriber.subscribe_topics(*aitrados_api_identity.channel.get_array())  # subscribe all channels

model_config_more_params={
    "role_prompt": None,#Custom system prompt
    "profile": None,#Custom Self-introduction.The manager needs to know my skills and then assign me tasks.
    "nickname": None,#Custom name
    "system_prompt_lang": None,#Language of system prompt.Specify langchain_trading_agents/assistive_tools/*system_prompt_words folder
    "role_prompt_file_or_url": None,#you can Custom system prompt from a file or url.
    "profile_file_or_url": None,#  Custom Self-introduction from a file or url.
    "placeholder_map": None,#Automatic replace role_prompt and profile {placeholder}
    #"custom_mcp_department":None,#get custom_mcp_department name from http://127.0.0.1:11999/mcp_servers.json .example: Decision Maker maybe need broker trading account information
    "output_parser":None #parser instance.auto parse JSON,STR,XML,LIST class name.Optional[JsonOutputParser|StrOutputParser|ListOutputParser|XMLOutputParser].only use for sub agent.
}
"""
If the role_prompt or profile contains any of the following placeholders, they will be automatically replaced:
- {basic_system_function_call_prompt}
- {all_traditional_indicator_names}
- {available_agent_profiles}
- {current_datetime}
"""