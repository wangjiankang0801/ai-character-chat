from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Character
from schemas import CharacterCreate, CharacterUpdate, CharacterOut

router = APIRouter(prefix="/api/characters", tags=["characters"])

@router.get("", response_model=list[CharacterOut])
def list_characters(db:Session=Depends(get_db)):
    return db.query(Character).order_by(Character.created_at.desc()).all()

@router.post("", response_model=CharacterOut)
def create_character(data:CharacterCreate, db:Session=Depends(get_db)):
    c=Character(**data.model_dump());db.add(c);db.commit();db.refresh(c);return c

@router.get("/{char_id}", response_model=CharacterOut)
def get_character(char_id:str, db:Session=Depends(get_db)):
    c=db.query(Character).filter(Character.id==char_id).first()
    if not c: raise HTTPException(404,"角色不存在")
    return c

@router.put("/{char_id}", response_model=CharacterOut)
def update_character(char_id:str, data:CharacterUpdate, db:Session=Depends(get_db)):
    c=db.query(Character).filter(Character.id==char_id).first()
    if not c: raise HTTPException(404,"角色不存在")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(c,k,v)
    db.commit();db.refresh(c);return c

@router.delete("/{char_id}")
def delete_character(char_id:str, db:Session=Depends(get_db)):
    c=db.query(Character).filter(Character.id==char_id).first()
    if not c: raise HTTPException(404,"角色不存在")
    db.delete(c);db.commit();return {"ok":True}
