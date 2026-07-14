from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/generate", tags=["generate"])

SYSTEM = """你是一个角色设定专家。用户会描述他想要的角色，你需要帮他优化成一段完整的系统提示词。
要求：
- 包含角色的性格、说话风格、背景等关键信息
- 用第二人称"你"来描述角色
- 简洁清晰，100-200字
- 直接输出提示词，不要任何解释和前缀"""

class Req(BaseModel):
    idea: str

@router.post("/prompt")
def gen_prompt(req: Req):
    if not req.idea.strip():
        raise HTTPException(400, "描述不能为空")
    try:
        from openai import OpenAI
        key = os.getenv("DEEPSEEK_API_KEY", "")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com/v1")
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role":"system","content":SYSTEM},{"role":"user","content":"我想要这样的角色："+req.idea}],
            temperature=0.7,
            max_tokens=1024
        )
        return {"prompt": r.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(500, f"生成失败: {str(e)}")
