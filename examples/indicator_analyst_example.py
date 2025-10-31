from common_lib_example import *
model_config=get_llm_model_config(ModelProvider.OLLAMA)
async def main():

    history_conversation_id=None
    query="You only use 20-day and 60-day moving averages, with a daily timeframe. Tell me, what's the next move for Bitcoin? When answering, strive for conciseness; your buy and sell orders must include a closing price. Don't be vague, because your answer will influence my AI manager's decision-making."
    model_config.update(model_config_more_params)#custom prompt
    indicator_analyst_llm=IndicatorAnalyst(**model_config)
    result=await indicator_analyst_llm.analyze(query,conversation_id=history_conversation_id)
    print("Analysis results:\n",result)



if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)



