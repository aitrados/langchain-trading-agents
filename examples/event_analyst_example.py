from common_lib_example import *


model_config=get_llm_model_config(ModelProvider.OLLAMA)

async def main():
    query="Take a look at recent events related to Apple, mainly US economic events such as unemployment rate, CPI, and PPI. Then you can draw your conclusions directly."
    model_config.update(model_config_more_params)  # custom prompt
    indicator_analyst_llm=EventAnalyst(**model_config)
    result=await indicator_analyst_llm.analyze(query)
    print("Analysis results:\n",result)
if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)



