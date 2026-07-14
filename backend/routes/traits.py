from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserTrait
from schemas import TraitOut, TraitUpdate

router = APIRouter(prefix="/api/traits", tags=["traits"])

@router.get("", response_model=list[TraitOut])
def list_traits(character_id:str, db:Session=Depends(get_db)):
    return db.query(UserTrait).filter(UserTrait.character_id==character_id).order_by(UserTrait.created_at.desc()).all()

@router.put("/{trait_id}", response_model=TraitOut)
def update_trait(trait_id:str, data:TraitUpdate, db:Session=Depends(get_db)):
    t = db.query(UserTrait).filter(UserTrait.id==trait_id).first()
    if not t: raise HTTPException(404,"特征不存在")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(t,k,v)
    db.commit();db.refresh(t);return t

@router.delete("/{trait_id}")
def delete_trait(trait_id:str, db:Session=Depends(get_db)):
    t = db.query(UserTrait).filter(UserTrait.id==trait_id).first()
    if not t: raise HTTPException(404,"特征不存在")
    db.delete(t);db.commit();return {"ok":True}

@router.post("/manual", response_model=TraitOut)
def add_trait(character_id:str, trait_key:str, trait_value:str, db:Session=Depends(get_db)):
    t = UserTrait(character_id=character_id, trait_key=trait_key, trait_value=trait_value, source="manual", confirmed=True)
    db.add(t);db.commit();db.refresh(t);return t
