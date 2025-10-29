from finance_trading_ai_agents_mcp.mcp_services.traditional_indicator_operations.traditional_indicator_ops import \
    TraditionalIndicatorOps
from finance_trading_ai_agents_mcp.parameter_validator.analysis_departments import analysis_department
from finance_trading_ai_agents_mcp.utils.common_utils import get_content_from_file_or_url
from finance_trading_ai_agents_mcp.utils.contant import SystemPromptLanguage
from pathlib import Path

def auto_replace_string_placeholder(string:str,**kwargs):
    for key, value in kwargs.items():
        placeholder = f"{{{key}}}"
        string = string.replace(placeholder, str(value))
    return string



def get_all_traditional_indicator_names(*more_indicator:str):
    indicators=TraditionalIndicatorOps.valid_indicators
    for indicator in more_indicator:
        if indicator not in indicators:
            indicators.add(indicators)
    return list(indicators)

def get_analyst_prompt(department:str,lang='en',file_or_url:str=None,header=None,is_profile=False):
    fold_name_data={
        analysis_department.TRADITIONAL_INDICATOR:"traditional_indicator_system_prompt_words",
        analysis_department.PRICE_ACTION: "price_action_system_prompt_words",
        analysis_department.ECONOMIC_CALENDAR: "economic_calendar_system_prompt_words",
        analysis_department.NEWS: "news_system_prompt_words",
        analysis_department.MANAGER: "manager_system_prompt_words",
        analysis_department.DECISION_MAKER: "decision_maker_system_prompt_words",

    }

    if lang not in SystemPromptLanguage.get_array():
        lang = "en"
    if not file_or_url:
        base_dir = Path(__file__).parent / fold_name_data[department]
        if is_profile:
            file_or_url = base_dir / f"profile_{lang}.md"
        else:
            file_or_url = base_dir / f"{lang}.md"
    return get_content_from_file_or_url(file_or_url, header)
'''
def get_basic_manager_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.MANAGER,lang,file_or_url,header)
def get_basic_decision_maker_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.DECISION_MAKER,lang,file_or_url,header)

def get_basic_traditional_indicator_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.TRADITIONAL_INDICATOR,lang,file_or_url,header)

def get_basic_price_action_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.PRICE_ACTION,lang,file_or_url,header)

def get_basic_economic_calendar_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.ECONOMIC_CALENDAR,lang,file_or_url,header)

def get_basic_news_prompt(lang='en',file_or_url:str=None,header=None):
    return get_analyst_prompt(analysis_department.NEWS,lang,file_or_url,header)
'''
