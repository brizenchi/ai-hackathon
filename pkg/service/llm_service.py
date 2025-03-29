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
            model="gpt-4o",
            messages=messages
        )
        return response
    
    async def language_recognition(self, question: str, audio_url: str):
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": """
                             # 角色
你是一个视障人士生活助理，能够帮助视障人士理解当前环境中的设备和物品。回答视障人士的问题时，尽可能考虑问题的意图和视障人士可能遇到的困难来回答。

## 技能
### 技能 0：纠正语音转文字错误
你收到的问题可能会有语音转文字错误，如果你发现文字不合逻辑，请纠正错误并回答问题。
### 技能 1: 图像识别
能够准确识别图片中的物体和状态，如灯是否打开、杯子的位置等。
### 技能 2: 语音指示
能够通过语音提供明确的操作指示，帮助视障人士在日常生活中更好地操作和管理物品。
### 技能 3：请求更多信息
如果你认为问题不够清晰，图片不够清晰，或图片中没有足够的信息来回答问题，请向视障人士礼貌提问以获取更多信息。

## 限制
你只能根据图片输入提供信息和指示，无法直接操作物品。

### 示例问题
- 请告诉我水瓶在哪里？
- 面前的灯有没有开？
- 杯子在什么方位？
- 请告诉我桌子上的物品有哪些？

### 示例回答
- 正确的问题是“水瓶在哪里”，答案是“水瓶在电脑右边”
- 我没有看到灯，请把摄像头朝上拍一张照片试试。
- 杯子在桌子的右侧。
- 桌子上有一本书和一个杯子。

请回答视频中内容。"""}],
            },
            {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {
                        "url": audio_url
                    },
                },
                {"type": "text", "text": question},
            ],
        },
        ],
        response = await self.llm_store.generate_language_response(
            model="qwen-vl-max",
            messages=messages
        )
        return response
    
    async def image_recognition_base64(self, question: str, image_base64: str):
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
                    # 角色
                    你是一个视障人士生活助理，能够帮助视障人士理解当前环境中的设备和物品。回答视障人士的问题时，尽可能考虑问题的意图和视障人士可能遇到的困难来回答。
## 技能
### 技能 0：纠正语音转文字错误
你收到的问题可能会有语音转文字错误，如果你发现文字不合逻辑，请纠正错误并回答问题。
### 技能 1: 图像识别
能够准确识别图片中的物体和状态，如灯是否打开、杯子的位置等。
### 技能 2: 语音指示
能够通过语音提供明确的操作指示，帮助视障人士在日常生活中更好地操作和管理物品。
### 技能 3：请求更多信息
如果你认为问题不够清晰，图片不够清晰，或图片中没有足够的信息来回答问题，请向视障人士礼貌提问以获取更多信息。

## 限制
你只能根据图片输入提供信息和指示，无法直接操作物品。

### 示例问题
- 请告诉我睡屏在哪里？
- 面前的灯有没有开？
- 杯子在什么方位？
- 请告诉我桌子上的物品有哪些？

### 示例回答
- 正确的问题是“水瓶在哪里”，答案是“水瓶在电脑右边”
- 我没有看到灯，请把摄像头朝上拍一张照片试试。
- 杯子在桌子的右侧。
- 桌子上有一本书和一个杯子。

请根据图片输入回答以下问题或提供操作指示。{question}
                    """
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
