from fastapi import APIRouter, File, Form, UploadFile, status as st

from services import message_service as ms
from schemas import MessageResponse


router = APIRouter(prefix="/message", tags=["Message"])


@router.post("/", response_model=MessageResponse, status_code=st.HTTP_201_CREATED)
async def process_message(exhibit_info: str = Form(...), audio: UploadFile = File(...)):
    return await ms.process_message(exhibit_info, audio)


# Creating a modified endpoint since there were no microphone or speaker modules 
# for the Particle board, so the computer must be used for those:
@router.post("/modified", response_model=MessageResponse, status_code=st.HTTP_201_CREATED)
async def modified_process_message(exhibit_info: str = Form(...)):
    input_audio_path = ms.record_audio()
    response = await ms.process_message(exhibit_info, audio_path=input_audio_path)
    encoded_audio = response.get("audio")
    ms.play_audio(encoded_audio) 

    return response