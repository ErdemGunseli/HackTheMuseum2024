from fastapi import APIRouter, File, UploadFile, status as st

from services import message_service as ms
from schemas import MessageResponse


router = APIRouter(prefix="/message", tags=["Message"])


@router.post("/", response_model=MessageResponse, status_code=st.HTTP_201_CREATED)
async def process_message(exhibit_info: str, audio: UploadFile = File(...)):
    return await ms.process_message(exhibit_info, audio)