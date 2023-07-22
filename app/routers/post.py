from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

#@app.get("/posts")
#def get_posts():
    #cursor.execute("""SELECT * from posts""")
    #posts = cursor.fetchall()
    #return {"data": posts}


#@router.get("/all", response_model=List[schemas.Post])
@router.get("/all", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str]=""):

    #posts = db.query(models.Post)
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(
        models.Post.id).all()
    
    return posts


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str]=""):

    posts = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.owner_id == current_user.id).order_by(models.Post.id).all()
    
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = 
                 Depends(oauth2.get_current_user)):
    #print(post.model_dump)
    print(current_user.id)
    new_post = models.Post(**post.dict())
    new_post.owner_id = current_user.id
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    
    db.add(new_post)
    db.commit()
    db.refresh (new_post)
   
    #cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) 
                   #Returning * """, (post.title, post.content, post.published)) 
    #new_post = cursor.fetchone()
    #conn.commit()
    #post_dict = post.model_dump()
    #post_dict['id'] = randrange(0, 10000000)
    #my_posts.append(post_dict)
    return new_post


#@router.get("/posts/latest")
#def get_latest_post():
#    post = my_posts[len(my_posts)-1]
#    return post

#@app.get("/posts/{id}")
#def get_post(id: int): #response: Response):
    #cursor.execute(""" SELECT * from posts WHERE id = %s """, (str(id)))
    #post = cursor.fetchone()
    #print(post)
    #print(id)
    #test_post = find_post(id)
    #if not post:
        #raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            #detail=f"post with id: {id} was not found" )

        ##response.status_code = status.HTTP_404_NOT_FOUND
        ##return{'message': f"post with id: {id} was not found"}
    #return{"post_detail": post}


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    #, func.count(models.Vote.post_id).label("votes")).join(
    #    models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)

    single_post = db.query(models.Post).filter(models.Post.id == id).first()
    
    #single_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
    #    models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
    #    models.Post.id).filter(models.Post.id == id).first()

    #query_result = single_post.first()

    if not single_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    if single_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Cannot view post")

    return single_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = 
                 Depends(oauth2.get_current_user)):
    #index = find_index_post(id)
    #cursor.execute(""" DELETE from posts WHERE id = %s """, (str(id),)) 
    ##deleted_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    query_result = post_query.first()

    print(current_user.id)

    if query_result == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    
    if query_result.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to delete the post")
    
    #my_posts.pop(index)
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response (status_code=status.HTTP_204_NO_CONTENT) 
    #{'message': f'Your post index {id} was deleted'}



@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = 
                 Depends(oauth2.get_current_user)):
    #print(post)
    #index = find_index_post(id)
    #cursor.execute(""" Update posts set title = %s, content = %s,  published = %s 
                   #WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    #conn.commit()
    #updated_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    query_result = post_query.first()

    if query_result == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    
    if query_result.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to change the post")

    #post_dict = post.model_dump()
    #post_dict['id'] = str(id)

    post_query.update(post.dict(), synchronize_session=False)
    #post_query['id'] = str(id)
    db.commit()
    #db.refresh(post_query)

    #my_posts[index] = post_dict
    return post_query.first()