from pydantic import BaseModel


class VCRequest(BaseModel):
    audio_base64: str
