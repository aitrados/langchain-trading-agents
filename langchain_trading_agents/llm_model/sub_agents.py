"""
sub_agents.py
Defines sub-agents, including: Technical Indicator Analyst, Price Behavior Analyst, News Analyst, Event Analyst, and Fundamental Analyst.
"""
from finance_trading_ai_agents_mcp.parameter_validator.analysis_departments import analysis_department

from langchain_trading_agents.llm_model.base_sub_agent import BaseSubAgent

class IndicatorAnalyst(BaseSubAgent):
    nickname="Alexander III"
    department=analysis_department.TRADITIONAL_INDICATOR
class PriceActionAnalyst(BaseSubAgent):
    nickname="Edward Sterling"
    department=analysis_department.PRICE_ACTION

class NewsAnalyst(BaseSubAgent):
    nickname="QIANG WANG"
    department=analysis_department.NEWS

class EventAnalyst(BaseSubAgent):
    nickname="Harrison Black"
    department=analysis_department.ECONOMIC_CALENDAR



class ManagerAnalyst(BaseSubAgent):
    nickname="Benjamin Frost"
    department=analysis_department.MANAGER
class DecisionMakerAnalyst(BaseSubAgent):
    nickname="MR. Nightingale"
    department=analysis_department.DECISION_MAKER