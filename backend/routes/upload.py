import os, uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/upload", tags=["upload"])
UPLOAD_DIR = Path("/tmp/chat-uploads"); UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED = {"image/jpeg","image/png","image/gif","image/webp"}

@router.post("/image")
async def upload_image(file:UploadFile=File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400,"不支持的文件类型")
    content = await file.read()
    if len(content) > 20*1024*1024:
        raise HTTPException(400,"图片太大")
    ext = file.filename.rsplit(".",1)[-1] if "." in file.filename else "jpg"
    tmp = UPLOAD_DIR / f"{uuid.uuid4()}.{ext}"
    with open(tmp,"wb") as f: f.write(content)
    import base64
    with open(tmp,"rb") as f: b64 = base64.b64encode(f.read()).decode()
    os.unlink(str(tmp))
    return JSONResponse({"base64":b64,"mime":file.content_type,"filename":file.filename})
