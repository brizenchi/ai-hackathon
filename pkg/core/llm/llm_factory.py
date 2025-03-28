from typing import Dict
from pkg.core.llm.llm_store import LLMStore
from app.config.settings import settings

class LLMFactory:
    _instances: Dict[str, LLMStore] = {}
    
    @classmethod
    def get_instance(cls, model: str = "gpt-4") -> LLMStore:
        """获取指定数据源的实例"""
        if model not in cls._instances:
            api_key = settings.LLM_MODEL[model]["api_key"]
            base_url = settings.LLM_MODEL[model]["base_url"]
            cls._instances[model] = LLMStore(model=model, api_key=api_key, base_url=base_url)
        return cls._instances[model]