import io
import os
import torch
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from kokoro import KPipeline

app = FastAPI(title="KAII Thorsten TTS Server")

# Allow CORS so mobile app and web can request freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load German Kokoro Pipeline ('d' for German / de)
pipeline = None

@app.on_event("startup")
def load_model():
    global pipeline
    try:
        pipeline = KPipeline(lang_code='d')
        print("Kokoro German pipeline initialized successfully!")
    except Exception as e:
        print("Failed to init pipeline:", e)

class TTSRequest(BaseModel):
    text: str
    speed: float = 0.95

@app.get("/")
def home():
    return {"status": "ok", "service": "KAII Thorsten TTS Server"}

@app.get("/health")
@app.get("/api/tts/health")
def health():
    return {
        "status": "ok",
        "model": "Thorsten-Voice/Kokoro",
        "ready": pipeline is not None
    }

@app.post("/tts")
@app.post("/api/tts")
def generate_tts(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    
    global pipeline
    if pipeline is None:
        pipeline = KPipeline(lang_code='d')

    try:
        # Thorsten voice in Kokoro: dm_thorsten
        generator = pipeline(req.text.strip(), voice='dm_thorsten', speed=req.speed, split_pattern=r'\n+')
        all_audio = []
        for _, _, audio in generator:
            all_audio.append(audio)
            
        if not all_audio:
            raise HTTPException(status_code=500, detail="No audio generated")

        combined = torch.cat(all_audio, dim=0).cpu().numpy()
        
        # Write to WAV buffer in memory (24kHz)
        buffer = io.BytesIO()
        sf.write(buffer, combined, 24000, format='WAV')
        buffer.seek(0)
        
        return Response(content=buffer.read(), media_type="audio/wav")
    except Exception as e:
        print("TTS Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

