from fastapi import APIRouter, Request
import logging
from pkg.core.result.result import success_result
from pkg.service.llm_service import LlmService
logger = logging.getLogger(__name__)

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
