from copy import deepcopy

from aitrados_api.common_lib.tools.toml_manager import TomlManager
from aitrados_api.common_lib.utils import get_value_by_dict_path

from langchain_trading_agents.contant import ModelProvider


def get_llm_model_config(provider=ModelProvider.OPENAI,default=None):
    path=f"llm_models..{provider}"
    return deepcopy(get_value_by_dict_path(TomlManager.c,path,default,split_str=".."))