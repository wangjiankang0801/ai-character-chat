import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from routes import characters, chat, traits, upload

app = FastAPI(title="AI 角色聊天", version="2.0.0")

@app.on_event("startup")
def startup(): init_db()

app.include_router(characters.router)
app.include_router(chat.router)
app.include_router(traits.router)
app.include_router(upload.router)

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def index():
    idx = static_dir / "index.html"
    if idx.exists(): return FileResponse(str(idx))
    return {"message":"Frontend not ready"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT","8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
