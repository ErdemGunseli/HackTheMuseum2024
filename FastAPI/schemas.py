from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    exhibit_info: str = Field(max_length=10000)
    

class MessageResponse(BaseModel):
    text: str
    # base64 encoded audio:
    audio: str

    