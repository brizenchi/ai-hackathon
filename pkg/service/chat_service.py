import logging
import json
from pkg.core.llm.llm_aggrator import LLMAggrator
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.llm_aggrator = LLMAggrator()
        
    async def chat(self,messages: str):
        try:
            prompt = [
                {"role": "system", "content": f""},
                {"role": "user", "content": f"""{messages}"""}
            ]

            # 获取响应并验证JSON格式
            response = await self.llm_aggrator.generate_response(prompt)
            
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
