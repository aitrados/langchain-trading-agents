from common_lib_example import *
model_config=get_llm_model_config(ModelProvider.OLLAMA)

async def main():
    query="Please provide me with the daily and hourly charts for Bitcoin. Find the recent candlestick chart's resistance and support levels, and tell me the highest or lowest price at each level. I need your entry and exit points on these smaller timeframes. When answering, please be concise and provide specific prices for buy and sell orders. Avoid vague answers, as they will influence my AI's decision-making process."
    indicator_analyst_llm=PriceActionAnalyst(**model_config)
    result=await indicator_analyst_llm.analyze(query)
    print("Analysis results:\n",result)
if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)



