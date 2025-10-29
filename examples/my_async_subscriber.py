# Example: async subscriber skeleton
# filepath: example_subscriber.py
import json
import time
from loguru import logger
from aitrados_api.common_lib.any_list_data_to_format_data import AnyListDataToFormatData, deserialize_multi_symbol_multi_timeframe_data
from aitrados_api.trade_middleware.request import AsyncFrontendRequest, FrontendRequest
from aitrados_api.trade_middleware.subscriber import AsyncSubscriber
from aitrados_api.trade_middleware_service.trade_middleware_identity import aitrados_api_identity as idt

from langchain_trading_agents.utils.conversation_operation import LangchainConversationOperation

conversation_record_fold_path=None

# help https://github.com/aitrados/aitrados-api/blob/main/aitrados_api/trade_middleware/subscriber.py

class MyAsyncSubscriber(AsyncSubscriber):
    async def on_ohlc(self, msg):
        # stream of OHLC messages
        pass

    async def on_ohlc_chart_flow_streaming(self, msg):
        full_symbol = msg["full_symbol"]
        interval = msg["interval"]
        df = AnyListDataToFormatData(msg["data"]).get_polars()
        print("on_ohlc_chart_flow_streaming", full_symbol, interval)

    async def on_multi_symbol_multi_timeframe(self, msg):
        name = msg["name"]
        data = deserialize_multi_symbol_multi_timeframe_data(msg["data"], to_format="pandas")

    async def on_news(self, msg):
        print("on_news", msg)

    async def on_event(self, msg):
        print("on_event", AnyListDataToFormatData(msg).get_csv())

    async def on_show_subscribe(self, msg):
        all_subscribed_topics = await AsyncFrontendRequest.call_sync(idt.backend_identity, idt.fun.ALL_SUBSCRIBED_TOPICS)
        print("all_subscribed_topics", all_subscribed_topics)

    async def on_llm_conversation(self, msg):
        if isinstance(msg,dict) and "conversation_id" in msg and "department" in msg and "usage_metadata" in msg:
            await LangchainConversationOperation().a_save(msg,fold_path=conversation_record_fold_path)

        #print("on_llm_conversation",json.dumps(msg))



'''
if __name__ == "__main__":
    subscriber = MyAsyncSubscriber()
    subscriber.run()  # starts the async loop and connects to middleware
    # subscribe to topics (examples)
    subscriber.subscribe_topics("on_llm_conversation")
    subscriber.subscribe_topics(*idt.channel.get_array())  # subscribe common channels

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("close...")
'''