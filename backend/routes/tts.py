import io, json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/tts", tags=["tts"])

class TTSRequest(BaseModel):
    text: str
    rate: float = 1.0
    pitch: float = 1.0

# Voices: https://speech.platform.bing.com/consumer/speech/synthesize/voicelist
ZH_VOICES = [
    "zh-CN-XiaoxiaoNeural",   # 晓晓 (女, 自然)
    "zh-CN-XiaoyiNeural",     # 晓伊 (女)
    "zh-CN-YunjianNeural",    # 云健 (男)
    "zh-CN-YunxiNeural",      # 云希 (男)
    "zh-CN-YunxiaNeural",     # 云夏 (男)
    "zh-CN-XiaochenNeural",   # 晓辰 (女)
]

@router.post("")
async def text_to_speech(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(400, "文本不能为空")

    try:
        import edge_tts
        import asyncio

        # Pick voice - use the first one (Xiaoxiao, best quality)
        voice = ZH_VOICES[0]

        # Build SSML with rate/pitch control
        rate_str = f"+{int((req.rate-1)*100)}%" if req.rate >= 1 else f"{int(req.rate*100)}%"
        pitch_str = f"+{int((req.pitch-1)*50)}Hz" if req.pitch >= 1 else f"-{int((1-req.pitch)*50)}Hz"

        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
            <voice name="{voice}">
                <prosody rate="{rate_str}" pitch="{pitch_str}">
                    {req.text[:1000]}
                </prosody>
            </voice>
        </speak>"""

        communicate = edge_tts.Communicate(ssml, voice, rate=rate_str, pitch=pitch_str)
        audio_bytes = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.write(chunk["data"])

        audio_bytes.seek(0)
        return StreamingResponse(audio_bytes, media_type="audio/mpeg")

    except ImportError:
        raise HTTPException(500, "edge-tts 未安装")
    except Exception as e:
        raise HTTPException(500, f"TTS 生成失败: {str(e)}")
