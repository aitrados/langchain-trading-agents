import uuid
from copy import deepcopy

from aitrados_api.common_lib.tools.toml_manager import TomlManager
from aitrados_api.common_lib.utils import get_value_by_dict_path
from loguru import logger

from langchain_trading_agents.contant import ModelProvider

import os
from aitrados_api.common_lib.common import load_env_file, is_debug
from aitrados_api.common_lib.tools.toml_manager import TomlManager

def auto_load_global_config():
    if not os.getenv('AITRADOS_SECRET_KEY'):
        load_env_file(override=True)
    if not TomlManager.c:
        TomlManager.load_toml_file()
def get_llm_model_config(provider=ModelProvider.OPENAI,default=None):
    auto_load_global_config()
    path=f"llm_models..{provider}"
    data=deepcopy(get_value_by_dict_path(TomlManager.c, path, default, split_str=".."))
    if not data:
        raise Exception(f"llm model provider {provider} not found in config.toml")

    return data

def get_or_create_conversation_id(conversation_id:str=None):
    if not conversation_id:
        conversation_id =  f"conv_{uuid.uuid4().hex[:8]}"
        if is_debug():
            logger.debug(f"Generated new conversation_id: {conversation_id}")
    return conversation_id
