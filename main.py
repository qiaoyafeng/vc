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
from service import wav2wav
from svc_model_manager import hxq_svc_model
from utils import base64_decode, base64_encode, get_resp

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


@app.get("/get_file/{file_name}")
def read_item(file_name: str):
    file_path = os.path.isfile(os.path.join(TEMP_FOLDER_PATH, file_name))
    if file_path:
        return FileResponse(os.path.join(TEMP_FOLDER_PATH, file_name))
    else:
        return {"code": 404, "message": "file does not exist."}


@app.post("/api/wav2wav")
async def api_wav2wav(audio: UploadFile = File(..., description="audio file"),):
    resp = get_resp()
    suffix = audio.filename.split(".")[-1]
    in_audio_path = f"{TEMP_FOLDER_PATH}/{str(uuid.uuid1())}.{suffix}"
    async with aiofiles.open(in_audio_path, "wb") as in_file:
        content = await audio.read()
        await in_file.write(content)
    tran = 0  # 音调
    spk = 0  # 说话人(id或者name都可以,具体看你的config)
    wav_format = "wav"  # 范围文件格式
    out_wav_io = wav2wav(svc_model, in_audio_path, tran, spk, wav_format)

    out_audio_name = f"{str(uuid.uuid1())}.{suffix}"
    out_audio_path = f"{TEMP_FOLDER_PATH}/{out_audio_name}"
    async with aiofiles.open(out_audio_path, "wb") as out_file:
        out_wav_data = out_wav_io.read()
        await out_file.write(out_wav_data)
    out_audio_url = f"{BASE_DOMAIN}/get_file/{out_audio_name}"
    resp["data"] = {"url": out_audio_url}
    return resp


@app.post("/api/vc")
async def api_vc_base64(vc_req: schemas.VCRequest):
    resp = get_resp()

    in_audio_bytes = base64_decode(vc_req.audio_base64)
    in_audio_name = f"{uuid.uuid4().hex}.wav"
    in_audio_path = f"{TEMP_FOLDER_PATH}/{in_audio_name}"

    async with aiofiles.open(in_audio_path, "wb") as in_file:
        await in_file.write(in_audio_bytes)
    tran = 0  # 音调
    spk = 0  # 说话人(id或者name都可以,具体看你的config)
    wav_format = "wav"  # 范围文件格式
    out_wav_io = wav2wav(svc_model, in_audio_path, tran, spk, wav_format)

    out_wav_data = out_wav_io.read()

    resp["data"] = {"base64": base64_encode(out_wav_data), "format": "wav"}
    return resp


if __name__ == "__main__":
    uvicorn.run(app="__main__:app", host=settings.HOST, port=settings.PORT, reload=True)
