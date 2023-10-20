import os

import edge_tts
import uvicorn


import uuid

import aiofiles
import ffmpeg
from edge_tts import VoicesManager

from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

import schemas
from configs.base import settings, TEMP_FOLDER_PATH, BASE_DOMAIN
from svc_model_manager import hxq_svc_model
from utils import base64_decode, base64_encode

app = FastAPI(title="Voice Conversion", summary="Voice Conversion API")


origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


svc_model = hxq_svc_model

@app.post("/api/vc")
async def api_vc_base64(vc_req: schemas.VCRequest):
    resp = {
        "code": 0,
        "message": "操作成功！",
        "success": True,
        "data": {"base64": "", "format": "wav"},
    }

    audio_bytes = base64_decode(vc_req.audio_base64)
    audio_name = f"{uuid.uuid4().hex}.wav"
    audio_path = f"{TEMP_FOLDER_PATH}/{audio_name}"

    speaker_id, f_pitch_change, input_wav_path = 1, 2, audio_bytes
    out_audio, out_sr = svc_model.infer(speaker_id, tran, input_wav_path)



    b_wav_data = ""
    resp["data"] = {"base64": base64_encode(b_wav_data), "format": "wav"}
    return resp


if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host=settings.HOST, port=settings.PORT, reload=True)
