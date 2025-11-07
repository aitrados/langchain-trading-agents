
from common_lib_example import *
from langchain_trading_agents.bus_controls.ai_bus_control import AiBusControl, GraphState
from langchain_trading_agents.llm_model.sub_agents import ManagerAnalyst, DecisionMakerAnalyst
model_config=get_llm_model_config(ModelProvider.OLLAMA)
model_config.update(model_config_more_params)#custom prompt
async def main():
    manager_ai=AiBusControl(ManagerAnalyst(**model_config),DecisionMakerAnalyst(**model_config,custom_mcp_department=analysis_department.BROKER))
    manager_ai.add_sub_agent(IndicatorAnalyst(**model_config),
                             PriceActionAnalyst(**model_config),
                             NewsAnalyst(**model_config),
                             EventAnalyst(**model_config),
                             )
    ask="Please help me analyze how I should trade Bitcoin over the next few days, using daily and hourly charts, traditional indicators, and support and resistance levels. I'm looking at larger timeframes to trade smaller ones. Also, could you please analyze the news and financial events and advise me on how to trade over the next 2-3 days?."
    result:GraphState=await manager_ai.a_analyze(ask)

    print("Analysis results:\n")
    print(result)

if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    #Waiting for asynchronous writing of the conversation record to finish
    sleep(0.8)