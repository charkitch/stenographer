import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

app = FastAPI()

MODEL_NAME = os.getenv("WHISPER_MODEL", "medium")
MODEL_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

model: WhisperModel | None = None


@app.on_event("startup")
def load_model():
    global model
    # Docker on macOS = CPU-only, so we stick to device="cpu"
    app.logger if hasattr(app, "logger") else None
    print(f"Loading Whisper model '{MODEL_NAME}' with compute_type='{MODEL_COMPUTE_TYPE}'")
    try:
        # this will download the model once into the HF cache volume
        model = WhisperModel(MODEL_NAME, device="cpu", compute_type=MODEL_COMPUTE_TYPE)
    except Exception as e:
        print(f"Error loading model: {e}")
        raise


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Save upload to a temp file so faster-whisper can read it
    suffix = os.path.splitext(file.filename or "")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        contents = await file.read()
        tmp.write(contents)

    try:
        segments, info = model.transcribe(tmp_path)
        full_text_parts: List[str] = []
        segments_out = []
        for seg in segments:
            txt = seg.text or ""
            full_text_parts.append(txt)
            segments_out.append(
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": txt.strip(),
                }
            )
        full_text = "".join(full_text_parts).strip()

    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return JSONResponse(
        {
            "language": info.language,
            "language_probability": info.language_probability,
            "text": full_text,
            "segments": segments_out,
        }
    )
