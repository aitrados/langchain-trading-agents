# 🚀 LangChain Trading Agents — Simulating Real Financial Departmental Roles — AI Trading Agents Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/langchain-trading-agents.svg)](https://badge.fury.io/py/langchain-trading-agents)

An AI trading agents platform built on LangChain that provides free real-time and historical market data, supports multi-role collaboration and auditable conversation records. Quick to get started, suitable for quantitative learning, strategy development, and validation.

`langchain-trading-agents` is an entry-level toolkit that helps newcomers quickly learn how multi-agent collaboration works in financial scenarios. It uses intuitive API names and integrates free real-time data features from `finance-trading-ai-agents-mcp` and `aitrados-api`.

## 💬 Community & Support

[![WeChat Group](https://img.shields.io/badge/💬_微信讨论群-07C160?style=for-the-badge&logo=wechat&logoColor=white)](https://docs.aitrados.com/wechat_group.png)
[![Discord](https://img.shields.io/badge/🎮_Discord_Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/aNjVgzZQqe)

Join our community for discussions, support, and updates!
## ✨ Key Features

### 🎯 Free Real-time Financial Data
- FREE real-time and historical market data
- Supports multiple timeframes and multiple instruments fetched in parallel
- Streamed OHLC data via HTTP and WebSocket APIs
- Covers major financial markets: stocks, crypto, forex, commodities, etc.

### 🤖 Multi-Agent Collaboration System
Simulates a professional departmental structure of a real financial firm:

- 🎩 Manager Analyst (Benjamin Frost) — overall coordination and strategic planning
- 📊 Technical Indicator Analyst (Alexander III) — traditional technical indicator analysis
- 📈 Price Action Analyst (Edward Sterling) — price movement and pattern analysis
- 📰 News Analyst (QIANG WANG) — market news and sentiment analysis
- 📅 Event Analyst (Harrison Black) — economic calendar and event impact analysis
- 🎯 Decision Maker (MR. Nightingale) — final trading decision maker
- 🎯 Custom Analysts — add more specialized roles as needed

### Detailed reporting
Detailed reports are generated in the `run_project_path/conversation_record` folder, recording the AI's chain-of-thought and MCP call details step-by-step for review and verification. You can adjust system prompts and user prompts as needed.

ai_report_screenshot.png

![ai_report_screenshot.png](assets/ai_report_screenshot.png)

### 🔧 Highly Customizable
- Supports many LLM providers (OpenAI, Ollama, Deepseek, Gemini, Anthropic, Qwen, HuggingFace, XAI, etc.). Note: the model you choose must support the `call tools` capability.
- Flexible agent configuration and composition — you can set different LLM models for different departments
- Extensible analysis departments and specialist roles
- Customizable system prompts for optimization

## 🚀 Quick Start

### Install
```bash
pip install -U langchain-trading-agents 
```
#### From source
```bash
git clone https://github.com/aitrados/langchain-trading-agents.git
cd langchain-trading-agents
pip install -r requirements.txt
#pip install -e .
```

### Save your `.env` to the project root
```shell
##Free Register at AiTrados website https://www.aitrados.com/ to get your API secret key (Free).
AITRADOS_SECRET_KEY=YOUR_SECRET_KEY
DEBUG=true
```
More environment variables:
[.env_example](https://github.com/aitrados/langchain-trading-agents/blob/main/env_example)

### Save `config.toml` to the project root
```shell
default_system_prompt_lang="en"
[llm_models]
    [llm_models.ollama]
    provider = "ollama"
    base_url = "http://127.0.0.1:11434"
    model_name = "gpt-oss:20b" #Required support call tools
    temperature = 0

    
    #more providers below
    #also, you can add IBKR,COINBASE,CHINA STOCK/FUTURES CTP,Binance,etc brokers here
# add broker account to mcp,get example config_example.toml]
# Prefer using demo accounts for trading and optimize prompt words
```
More toml configurations:
[config_example.toml](https://github.com/aitrados/langchain-trading-agents/blob/main/config_example.toml)


### Run finance-trading-ai-agents-mcp



```bash
# Auto-detect .env file
finance-trading-ai-agents-mcp

# Specify .env file path
finance-trading-ai-agents-mcp --env-file .env
```
See https://github.com/aitrados/finance-trading-ai-agents-mcp for many advanced uses.

### Example: Ask a single analyst (agent)
```python
from common_lib_example import *
model_config = get_llm_model_config(ModelProvider.OLLAMA)

async def main():
    query = (
        "Please analyze the daily and hourly charts for Bitcoin for the next few days. Identify the recent resistance and support levels on the candlestick charts, and tell me the corresponding high and low prices for each level, along with specific buy and sell prices. Please provide a concise and clear answer."
    )
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
    #model_config.update(model_config_more_params)
    indicator_analyst_llm = PriceActionAnalyst(**model_config)
    result = await indicator_analyst_llm.analyze(query)
    print("Analysis results:\n", result)

if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    # Wait briefly for asynchronous conversation-record writing to finish
    sleep(0.8)
```




### Example: Multi-agent (AI BUS) collaborative analysis

```python
from common_lib_example import *
from langchain_trading_agents.bus_controls.ai_bus_control import AiBusControl, GraphState
from langchain_trading_agents.llm_model.sub_agents import ManagerAnalyst, DecisionMakerAnalyst

model_config = get_llm_model_config(ModelProvider.OLLAMA)

async def main():
    manager_ai = AiBusControl(ManagerAnalyst(**model_config), DecisionMakerAnalyst(**model_config))
    manager_ai.add_sub_agent(
        IndicatorAnalyst(**model_config),
        PriceActionAnalyst(**model_config),
        NewsAnalyst(**model_config),
        EventAnalyst(**model_config),
    )
    ask = "Please analyze for me how I should trade Bitcoin in the next few days."
    result: GraphState = await manager_ai.a_analyze(ask)

    print("Analysis results:\n")
    print(result)

if __name__ == "__main__":
    run_MyAsyncSubscribe()
    import asyncio
    asyncio.run(main())
    # Wait briefly for asynchronous conversation-record writing to finish
    sleep(0.8)
```

### Analyst Custom parameters

Parameters:
- role_prompt (str | None) — Default: None
  - Description: Custom system prompt guiding the model's overall behavior. May include placeholders (see above).
  - Example: "You are a trading assistant specialized in technical analysis."

- profile (str | None) — Default: None
  - Description: Sub-agent self-introduction / capability description for task assignment. May include placeholders.
  - Example: "I am an Experienced indicator analyst, familiar with MACD and RSI."

- nickname (str | None) — Default: None
  - Description: Display name used in sessions/logs.
  - Example: "IndicatorBot-v1"

- system_prompt_lang (str | None) — Default: None
  - Description: Language code  to select prompts from langchain_trading_agents/assistive_tools/*system_prompt_words.
  - Example: "en" or "zh-cn"

- role_prompt_file_or_url (str | None) — Default: None
  - Description: Path or URL to load role_prompt from (overrides role_prompt if provided).
  - Example: "/path/to/role_prompt.md" or "https://example.com/role_prompt.txt"

- profile_file_or_url (str | None) — Default: None
  - Description: Path or URL to load profile from (overrides profile if provided).
  - Example: "/path/to/profile.md" or "https://example.com/profile.txt"

- placeholder_map (dict | None) — Default: None
  - Description: Mapping for placeholder replacement (keys without braces, values are replacement strings or callables).
    - Example: \{"current_datetime": "2025-10-31 12:00:00", "available_agent_profiles": "- Analyst\n- Trader"\}
    - If the role_prompt or profile contains any of the following placeholders, they will be automatically replaced:
      - {basic_system_function_call_prompt}
      - {all_traditional_indicator_names}
      - {available_agent_profiles}
      - {current_datetime}

- custom_mcp_department (Optional[List[str] | str]) — Default: None
  - Description: Specify one or more MCP department names that the agent can access. Values should match entries from `http://127.0.0.1:11999/mcp_servers.json`.
  - Example: Trading account information can be accessed by both decision-makers and managers. Therefore, custom_mcp_department="broker"

- output_parser (instance | str | None) — Default: None
  - Description: Parser instance or class name for parsing sub-agent output (e.g., JsonOutputParser, StrOutputParser). Only used for sub-agents.
  - Example: JsonOutputParser(),StrOutputParser()

### 📐 Built-in prompts
- [Decision maker system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/decision_maker_system_prompt_words)
- [Manager system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/manager_system_prompt_words)
- [Price action analyst system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/price_action_system_prompt_words)
- [Traditional indicator analyst system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/traditional_indicator_system_prompt_words)
- [Economic calendar analyst system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/economic_calendar_system_prompt_words)
- [News analyst system prompt words Deutsch,English,Français,日本語,한국어,Español,Русский,简体中文,繁体中文](https://github.com/aitrados/langchain-trading-agents/blob/main/langchain_trading_agents/assistive_tools/news_system_prompt_words)

## 🏗️ Architecture Benefits
### Multi-Agent Collaboration
Each agent has a unique expertise and personality:
- 🧠 Specialized roles — each agent focuses on a particular analysis area
- 🔄 Collaborative decisions — reach optimal trading strategies through multiple discussion rounds
- 📝 Complete records — all conversations and analysis steps are fully saved

### Data Advantages
- ⚡ Real-time updates — market data pushed at ~10ms latency
- 🌍 Global coverage — covers major international markets
- 📊 Multi-dimensional data — OHLCV, technical indicators, news, economic events
- 💰 Completely free — no API fees at present

## 📊 Supported Analysis Types

- 📈 Technical Analysis: moving averages, RSI, MACD, Bollinger Bands, etc.
- 📰 Fundamental Analysis: news sentiment, financial data, macroeconomics
- 📅 Event-driven Analysis: economic calendar, earnings, central bank decisions
- 🎯 Price Action Analysis: support/resistance, pattern recognition, trend analysis

## 🛠️ Advanced Configuration

### Custom Analyst
```python
class CustomAnalyst(BaseSubAgent):
    nickname = "Your Custom Analyst"
    department = analysis_department.CUSTOM
```

### Asynchronous conversation stream (save to file or network)
The platform can asynchronously publish detailed chat records while sharing live market data. This enables richer strategy development.

```python
from examples.my_async_subscriber import MyAsyncSubscriber

subscriber = MyAsyncSubscriber()
subscriber.run(is_thread=True)
subscriber.subscribe_topics(LLM_CONVERSATION_SUB_TOPIC)
```

## 📚 Project Structure

```
langchain_trading_agents/
├── bus_controls/          # Agent control bus
├── llm_model/             # LLM models and agent definitions
├── utils/                 # Utility functions
├── assistive_tools/       # Helper tools
└── contant.py             # Constant definitions
```

## 🔗 Related Links

- 📖 [API Documentation](https://docs.aitrados.com/)
- 🐛 [Report Issues](https://github.com/aitrados/langchain-trading-agents/issues)
- 💬 [Community Discussions](https://github.com/aitrados/langchain-trading-agents/discussions)

## 🤝 Contributing

Contributions are welcome — please open issues and pull requests!

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

⭐ If you find this project helpful, please give it a star! ⭐

**Start your AI trading journey today — free real-time market data awaits!** 🚀

