from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Character, Conversation, Message, UserTrait
from schemas import ChatResponse, ConversationOut, ConversationListItem
from services.ai_service import chat_completion, extract_traits_from_conversation

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatReq(BaseModel):
    conversation_id: str | None = None
    character_id: str
    message: str = ""
    images: list[str] = []

def _build_prompt(char, traits, history):
    mem = [f"{t.trait_key}: {t.trait_value}" for t in traits]
    ms = "你已了解的用户信息：\n"+"\n".join(mem) if mem else "你还没有了解关于用户的特别信息。"
    return [{"role":"system","content":f"{char.system_prompt}\n\n{ms}\n\n请根据以上对用户的了解自然地交流。"}] + history

@router.post("", response_model=ChatResponse)
def chat(req: ChatReq, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.id==req.character_id).first()
    if not char: raise HTTPException(404,"角色不存在")

    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id==req.conversation_id).first()
        if not conv: raise HTTPException(404,"对话不存在")
    else:
        conv = Conversation(character_id=char.id)
        db.add(conv); db.flush()
        if char.greeting:
            db.add(Message(conversation_id=conv.id, role="assistant", content=char.greeting))

    display = req.message or "[发送了一张图片]"
    db.add(Message(conversation_id=conv.id, role="user", content=display))
    db.flush()

    msgs = db.query(Message).filter(Message.conversation_id==conv.id).order_by(Message.created_at).all()
    history = [{"role":m.role,"content":m.content} for m in msgs]
    traits = db.query(UserTrait).filter(UserTrait.character_id==char.id, UserTrait.confirmed==True).all()

    reply = chat_completion(_build_prompt(char, traits, history), temperature=float(char.temperature or 0.8), images=req.images or None)
    db.add(Message(conversation_id=conv.id, role="assistant", content=reply))

    if conv.title=="新对话":
        conv.title = (req.message or "图片消息")[:30] + ("..." if len(req.message or "")>30 else "")

    user_msgs = [m for m in msgs if m.role=="user"]
    if len(user_msgs)>0 and len(user_msgs)%3==0:
        try:
            for t in extract_traits_from_conversation(history):
                k,v = t.get("trait_key","").strip(), t.get("trait_value","").strip()
                if k and v and k not in {t.trait_key for t in traits}:
                    db.add(UserTrait(character_id=char.id, trait_key=k, trait_value=v, source="ai_extracted", confirmed=True))
        except: pass

    db.commit(); db.refresh(conv)
    all_t = db.query(UserTrait).filter(UserTrait.character_id==char.id, UserTrait.confirmed==True).all()
    return ChatResponse(conversation_id=conv.id, reply=reply, traits=[{"key":t.trait_key,"value":t.trait_value} for t in all_t])

@router.get("/conversations", response_model=list[ConversationListItem])
def list_convs(character_id:str=None, db:Session=Depends(get_db)):
    q = db.query(Conversation)
    if character_id: q = q.filter(Conversation.character_id==character_id)
    result = []
    for c in q.order_by(Conversation.updated_at.desc()).limit(50).all():
        cnt = db.query(Message).filter(Message.conversation_id==c.id).count()
        result.append(ConversationListItem(id=c.id,character_id=c.character_id,title=c.title,message_count=cnt,created_at=c.created_at,updated_at=c.updated_at))
    return result

@router.get("/conversations/{conv_id}", response_model=ConversationOut)
def get_conv(conv_id:str, db:Session=Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id==conv_id).first()
    if not conv: raise HTTPException(404,"对话不存在")
    return conv

@router.delete("/conversations/{conv_id}")
def delete_conv(conv_id:str, db:Session=Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id==conv_id).first()
    if not conv: raise HTTPException(404,"对话不存在")
    db.delete(conv); db.commit(); return {"ok":True}
