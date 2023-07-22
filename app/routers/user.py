from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):

    users = db.query(models.User).order_by(models.User.id).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    #hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_users(id: int, db: Session = Depends(get_db)):
    
    user_query = db.query(models.User).filter(models.User.id == id).first()
    if not user_query:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")

    return user_query

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if user.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail=f"user with id: {id} was not found")
    
    user.delete(synchronize_session=False)
    db.commit()
    return Response (status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    user_update = db.query(models.User).filter(models.User.id == id)
    if user_update.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail=f"user with id: {id} does not exist")
    
    user_update.update(user.dict(), synchronize_session=False)
    db.commit()

    return user_update.first()