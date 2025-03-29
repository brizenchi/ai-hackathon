from fastapi import APIRouter, Request, HTTPException
import logging
from pkg.core.result.result import success_result, error_result
from pkg.service.llm_service import LlmService
from fastapi.responses import JSONResponse
from pkg.core.qiniu.qiniu_factory import QiniuFactory
from pydantic import BaseModel
import aiofiles
import os
import whisper
import base64
logger = logging.getLogger(__name__)
model = whisper.load_model("base")
router = APIRouter(tags=["llm"])

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    response = await LlmService().chat(messages)
    return success_result(data={"response": response})

@router.post("/image")
async def image_recognition(request: Request):
    data = await request.json()
    image_url = data.get("image_url", "")
    response = await LlmService().image_recognition(image_url)
    return success_result(data={"response": response})

class MediaData(BaseModel):
    image: str
    audio: str
    timestamp: str
@router.post("/upload")
async def upload(data: MediaData):
    try:
        # 验证数据
        if not data.image or not data.audio:
            raise HTTPException(status_code=400, detail="Missing media data")

        # 创建保存目录
        save_dir = "uploads"
        os.makedirs(save_dir, exist_ok=True)

        # 生成文件名
        timestamp_clean = data.timestamp.replace(":", "-")  # 清理时间戳中的非法字符
        image_path = os.path.join(save_dir, f"image_{timestamp_clean}.jpg")
        audio_path = os.path.join(save_dir, f"audio_{timestamp_clean}.webm")
        transcript_path = os.path.join(save_dir, f"transcript_{timestamp_clean}.txt")
        # 异步保存图片
        image_binary = base64.b64decode(data.image.split(',')[1])
        async with aiofiles.open(image_path, 'wb') as f:
            await f.write(image_binary)

        # 异步保存音频
        audio_binary = base64.b64decode(data.audio)
        async with aiofiles.open(audio_path, 'wb') as f:
            await f.write(audio_binary)

        # 使用 Whisper 转录
        result = model.transcribe(audio_path)
        transcript = result["text"]
        async with aiofiles.open(transcript_path, 'w') as f:
            await f.write(transcript)
        qiniu_factory = QiniuFactory()
        qiniu_store = qiniu_factory.get_qiniu_store()
        image_url = qiniu_store.upload_file(image_path)
        audio_url = qiniu_store.upload_file(audio_path)
        # response = await LlmService().image_recognition(transcript, image_url[1], audio_url[1])
        response = await LlmService().language_recognition(transcript, audio_url[1])
        return success_result(data={"response": response})
        
    except Exception as e:
        return error_result(msg=str(e) , code=500)