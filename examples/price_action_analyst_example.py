from common_lib_example import *
model_config=get_llm_model_config(ModelProvider.OLLAMA)
async def main():
    query="Please analyze the daily and hourly charts for Bitcoin for the next few days. Identify the recent resistance and support levels on the candlestick charts, and tell me the corresponding high and low prices for each level, along with specific buy and sell prices. Please provide a concise and clear answer."
    model_config.update(model_config_more_params)  # custom prompt
    indicator_analyst_llm=PriceActionAnalyst(**model_config)
    result=await indicator_analyst_llm.analyze(query)
    print("Analysis results:\n",result)
if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)



