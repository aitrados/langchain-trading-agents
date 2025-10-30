

from common_lib_example import *
from langchain_trading_agents.bus_controls.ai_bus_control import AiBusControl, GraphState
from langchain_trading_agents.llm_model.sub_agents import ManagerAnalyst, DecisionMakerAnalyst
model_config=get_llm_model_config(ModelProvider.OLLAMA)
async def main():
    manager_ai=AiBusControl(ManagerAnalyst(**model_config),DecisionMakerAnalyst(**model_config))



    manager_ai.add_sub_agent(IndicatorAnalyst(**model_config),
                             PriceActionAnalyst(**model_config),
                             NewsAnalyst(**model_config),
                             EventAnalyst(**model_config),
                             )
    ask="Please analyze for me how I should trade Bitcoin in the next few days."
    result:GraphState=await manager_ai.a_analyze(ask)

    print("Analysis results:\n")
    print(result)



if __name__ == "__main__":
    run_MyAsyncSubscribe()

    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)