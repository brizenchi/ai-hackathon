from openai import AsyncOpenAI
import logging
import asyncio
from typing import List, Dict, Any
from pkg.core.llm.llm_factory import LLMFactory
from app.config.settings import settings
logger = logging.getLogger(__name__)

class LLMAggrator:
    def __init__(self, models: List[str] = None):
        """初始化多个LLM客户端
        :param models: 模型列表，如果为None则使用settings中的所有模型
        """
        if models is None:
            # 默认使用配置中的所有模型
            models = list(settings.LLM_MODEL.keys())
        
        self.models = models
        self.clients = {}
        
        # 初始化所有模型的客户端
        for model in models:
            try:
                self.clients[model] = LLMFactory.get_instance(model=model)
                logger.info(f"Successfully initialized model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize model {model}: {e}")
    
    async def generate_response(self, messages: List[Dict[str, str]], max_retries: int = 3) -> str:
        """尝试使用所有可用模型生成响应，直到成功或全部失败
        :param messages: 消息列表
        :param max_retries: 每个模型的最大重试次数
        :return: 生成的响应
        :raises RuntimeError: 如果所有模型都失败
        """
        last_error = None
        
        for model in self.models:
            if model not in self.clients:
                logger.warning(f"Model {model} not initialized, skipping")
                continue
                
            client = self.clients[model]
            retries = 0
            
            while retries < max_retries:
                try:
                    logger.info(f"Attempting to generate response using {model}")
                    response = await client.generate_response(messages)
                    logger.info(f"Successfully generated response using {model}")
                    return response
                    
                except Exception as e:
                    last_error = e
                    retries += 1
                    logger.warning(
                        f"Attempt {retries}/{max_retries} failed for {model}: {e}"
                    )
                    
                    if retries == max_retries:
                        logger.error(f"All retries failed for {model}, trying next model")
                        break
                    
                    # 在重试之前稍微等待一下
                    await asyncio.sleep(1)
        
        error_msg = f"All models failed to generate response. Last error: {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    async def generate_summary(self, passage: Dict[str, Any], count: int) -> str:
        """生成文章摘要
        :param passage: 文章内容
        :param count: 摘要字数限制
        :return: 生成的摘要
        """
        system_prompt = f"You are a keyword extraction expert, skilled at distilling article key points. Please keep the summary within {count} characters."
        user_prompt = f"""
        Summarize the article in one word within {count} characters. Extract only facts and data, remove redundant words, and try to explain clearly in one sentence if possible.

        Article Title: {passage['title']}
        Content: {passage['description']}. {passage['content']}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.generate_response(messages)

# 示例用法
async def main():
    llm_aggrator = LLMAggrator()  # 实例化 OpenAIAPI
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "who are you."}
    ]
    response = await llm_aggrator.generate_response(messages)
    print(response)

if __name__ == '__main__':
    asyncio.run(main())