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

    async def image_recognition(self, question: str, image_url: str):
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
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
    
    async def image_recognition_base64(self, question: str, image_base64: str):
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"你是一位给视障人士提供视觉信息的视觉助理。回答视障人士的问题时，尽可能考虑问题的意图和视障人士可能遇到的困难来回答。如果你认为问题不够清晰，图片不够清晰，或图片中没有足够的信息来回答问题，请向视障人士礼貌提问以获取更多信息。{question}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }]  # 确保这是一个列表，而不是元组
        
        response = await self.llm_store.generate_image_response(
            model="gpt-4o-mini",
            messages=messages
        )
        return response
