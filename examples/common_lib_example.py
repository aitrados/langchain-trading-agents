from time import sleep

from aitrados_api.common_lib.tools.toml_manager import TomlManager

from examples.my_async_subscriber import MyAsyncSubscriber
from langchain_trading_agents.utils.common_utils import get_llm_model_config


from langchain_trading_agents.contant import ModelProvider, LLM_CONVERSATION_SUB_TOPIC
from langchain_trading_agents.llm_model.sub_agents import IndicatorAnalyst,PriceActionAnalyst,EventAnalyst,NewsAnalyst


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
