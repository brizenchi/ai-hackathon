from openai import AsyncOpenAI
import logging
import asyncio
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LLMStore:
    def __init__(self, model: str = "gpt-4", api_key: str = None, base_url: str = None):
        """初始化 OpenAI API 异步客户端"""
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    async def generate_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """异步生成 OpenAI 的响应"""
        try:
            print(f"messages: {messages}")
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            # 直接返回文本内容
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise RuntimeError(f"Error generating response: {str(e)}")
        
    async def generate_image_response(self,model: str, messages: List[Dict[str, str]]) -> str:
        """异步生成 OpenAI 的响应"""
        try:
            print(f"messages: {messages}")
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            # 直接返回文本内容
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise RuntimeError(f"Error generating response: {str(e)}")
        
    async def generate_language_response(self,model: str, messages: List[Dict[str, str]]) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content
