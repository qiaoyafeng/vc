import io

import numpy as np
import soundfile

from inference import infer_tool, slicer
from inference.infer_tool import Svc


def wav2wav(svc_model: Svc, audio_path, tran, spk, wav_format):
    """
    wav2wav 声音推理克隆
    :param svc_model:
    :param audio_path:
    :param tran:
    :param spk:
    :param wav_format:
    :return:
    """
    infer_tool.format_wav(audio_path)
    chunks = slicer.cut(audio_path, db_thresh=-40)
    audio_data, audio_sr = slicer.chunks2audio(audio_path, chunks)

    audio = []
    for (slice_tag, data) in audio_data:
        print(f'#=====segment start, {round(len(data) / audio_sr, 3)}s======')

        length = int(np.ceil(len(data) / audio_sr * svc_model.target_sample))
        if slice_tag:
            print('jump empty segment')
            _audio = np.zeros(length)
        else:
            # padd
            pad_len = int(audio_sr * 0.5)
            data = np.concatenate([np.zeros([pad_len]), data, np.zeros([pad_len])])
            raw_path = io.BytesIO()
            soundfile.write(raw_path, data, audio_sr, format="wav")
            raw_path.seek(0)
            out_audio, out_sr, _ = svc_model.infer(spk, tran, raw_path)
            svc_model.clear_empty()
            _audio = out_audio.cpu().numpy()
            pad_len = int(svc_model.target_sample * 0.5)
            _audio = _audio[pad_len:-pad_len]

        audio.extend(list(infer_tool.pad_array(_audio, length)))
    out_wav_path = io.BytesIO()
    soundfile.write(out_wav_path, audio, svc_model.target_sample, format=wav_format)
    out_wav_path.seek(0)
    return out_wav_path
