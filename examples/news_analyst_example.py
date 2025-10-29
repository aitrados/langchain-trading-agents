from common_lib_example import *


model_config=get_llm_model_config(ModelProvider.OLLAMA)

async def main():
    query="Could you check out the latest news about Bitcoin and analyze it for me?"
    indicator_analyst_llm=NewsAnalyst(**model_config)
    result=await indicator_analyst_llm.analyze(query)
    print("Analysis results:\n",result)
if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)



