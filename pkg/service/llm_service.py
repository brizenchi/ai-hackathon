import logging
import json
from pkg.core.llm.llm_store import LLMStore
logger = logging.getLogger(__name__)

class LlmService:
    def __init__(self):
        self.llm_store = LLMStore()
        
    async def chat(self,messages: str):
        try:
            prompt = [
                {"role": "system", "content": f""},
                {"role": "user", "content": f"""{messages}"""}
            ]

            # 获取响应并验证JSON格式
            response = await self.llm_store.generate_chat_response(prompt)
            
            # 验证JSON格式
            try:
                return response
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format in response: {e}")
                raise
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Error in process_newsletter: {e}")
            raise
        finally:
            # 确保关闭连接
            try:
                await self.email_client.close()
            except Exception as e:
                logger.error(f"Error closing email client: {e}")

    async def image_recognition(self, image_url: str):
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }]  # 确保这是一个列表，而不是元组
        
        response = await self.llm_store.generate_image_response(
            model="gpt-4o-mini",
            messages=messages
        )
        return response
