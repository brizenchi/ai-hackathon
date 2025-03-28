from fastapi import APIRouter, Request
import logging
from pkg.core.result.result import success_result
from pkg.service.chat_service import ChatService
logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

@router.post("/")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    response = await ChatService().chat(messages)
    return success_result(data={"response": response})
