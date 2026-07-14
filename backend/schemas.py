from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CharacterCreate(BaseModel):
    name:str="AI助手";avatar:str="";system_prompt:str="你是一个友善的AI助手。"
    greeting:str="你好！";temperature:float=0.8

class CharacterUpdate(BaseModel):
    name:Optional[str]=None;avatar:Optional[str]=None;system_prompt:Optional[str]=None
    greeting:Optional[str]=None;temperature:Optional[float]=None;is_active:Optional[bool]=None

class CharacterOut(BaseModel):
    id:str;name:str;avatar:str;system_prompt:str;greeting:str;temperature:str;is_active:bool
    created_at:datetime;updated_at:datetime
    model_config={"from_attributes":True}

class MessageOut(BaseModel):
    id:str;role:str;content:str;created_at:datetime
    model_config={"from_attributes":True}

class ChatResponse(BaseModel):
    conversation_id:str;reply:str;traits:list=[]

class ConversationOut(BaseModel):
    id:str;character_id:str;title:str;messages:list[MessageOut]=[];created_at:datetime;updated_at:datetime
    model_config={"from_attributes":True}

class ConversationListItem(BaseModel):
    id:str;character_id:str;title:str;message_count:int;created_at:datetime;updated_at:datetime
    model_config={"from_attributes":True}

class TraitOut(BaseModel):
    id:str;character_id:str;trait_key:str;trait_value:str;source:str;confirmed:bool;created_at:datetime
    model_config={"from_attributes":True}

class TraitUpdate(BaseModel):
    trait_key:Optional[str]=None;trait_value:Optional[str]=None;confirmed:Optional[bool]=None
