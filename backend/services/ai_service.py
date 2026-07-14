import os, json, re, base64

AI_PROVIDER = os.getenv("AI_PROVIDER","deepseek").lower()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY","")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL","deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL","https://api.deepseek.com/v1")

def _get_client():
    from openai import OpenAI
    if AI_PROVIDER=="deepseek" and DEEPSEEK_API_KEY:
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL), DEEPSEEK_MODEL
    elif os.getenv("OPENAI_API_KEY"):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), os.getenv("OPENAI_MODEL","gpt-4o-mini")
    elif DEEPSEEK_API_KEY:
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL), DEEPSEEK_MODEL
    else:
        raise RuntimeError("未配置 API Key！请设置 DEEPSEEK_API_KEY")

def _call(messages, temperature=0.8):
    client, model = _get_client()
    resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature, max_tokens=4096)
    return resp.choices[0].message.content

def chat_completion(messages, temperature=0.8, images=None):
    if images:
        for i in range(len(messages)-1, -1, -1):
            if messages[i]["role"]=="user":
                content = messages[i]["content"]
                parts = [{"type":"text","text":content}] if isinstance(content,str) else list(content)
                for b64 in images:
                    parts.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}})
                messages[i] = {"role":"user","content":parts}
                break
    return _call(messages, temperature)

EXTRACT_TRAITS_PROMPT="""你是一个用户画像分析师。分析以下对话历史，提取出关于用户的重要特征或偏好。
请以 JSON 数组格式返回，每个元素包含 trait_key 和 trait_value。
只提取明确可以推断出的特征，不要编造。如果没有足够信息，返回空数组 []。
不要输出任何其他内容，只输出 JSON 数组。"""

def extract_traits_from_conversation(messages):
    text="\n".join([f"{m['role']}: {str(m['content'])}" for m in messages[-20:] if m['role']!='system'])
    try:
        r=_call([{"role":"system","content":EXTRACT_TRAITS_PROMPT},{"role":"user","content":"对话历史：\n"+text}],0.3)
        r=re.sub(r"```(?:json)?\s*","",r).strip()
        return json.loads(r) if isinstance(json.loads(r),list) else []
    except: return []
