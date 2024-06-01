from pydantic import BaseModel

# Message request just contains audio file

class MessageResponse(BaseModel):
    text: str
    # base64 encoded audio:
    audio: str

    