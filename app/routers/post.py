from random import randrange
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2, database
from .. database import get_db

router = APIRouter(
    prefix="/posts",   # -> Every where we have "/posts" can be replaced to "/" only
    tags=["Posts"]     # -> For documentation organization
)

############################################### USING SQLALCHEMY ################################

#--READ
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
     
    print("\nLimit: ", limit)

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # In case we only want to show posts of user logged in:
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()


    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts

## READ by id 
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
     
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    # In case we only want to show posts of user logged in:
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
    #                         detail=f"Not authorize to perform requested action")
    return post


 #--CREATE
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
     
    print("\nCURRENT USER email: ", current_user.email)
    print("\nCURRENT USER id: ", current_user.id)

    # new_post = models.Post(title = post.title, content = post.content, published = post.published)
    # instead we can do the following \/ so we dont need to specify all the columns :
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    # ** post.dict() --> ** unpacks the dictionary 


    db.add(new_post)
    db.commit()
    db.refresh(new_post) # -> retreives the new post created and stores it back to variable new_post

    return new_post


#DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
     
    print(current_user.email)

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"Not authorize to perform requested action")
    
    post_query.delete(synchronize_session = False)
    
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)



#UPDATE
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db : Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
     
    print(current_user.email)

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"Not authorize to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session = False)

    db.commit()

    return post # returns the post we updated

############################################### END REGION - USING SQLALCHEMY ###################



################################################ WITH DB ################################################

connection = database.connection
cursor = database.cursor

#--READ
@router.get("/posts")
def get_posts():
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data": posts}

## READ by id 
@router.get("/posts/{id}")
def get_post(id: int):
     
     cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id)))
     post = cursor.fetchone()
     if not post:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
     return {"post detail": post}

 #--CREATE
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.Post):
     cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
                     (post.title, post.content, post.published))
     
     new_post = cursor.fetchone()
     connection.commit()
     
     return {"data": new_post}

#DELETE
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
     
     cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))  
     deleted_post = cursor.fetchone()
     if deleted_post == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
      
     connection.commit()
     return Response(status_code=status.HTTP_204_NO_CONTENT)


#UPDATE
@router.put("/posts/{id}")
def update_post(id: int, post: schemas.Post):
     cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s 
                    WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))  
     updated_post = cursor.fetchone()

     if updated_post == None:
         raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    
     connection.commit()
     return {"data": updated_post}

################ END REGION - WITH DB ################

################ WITHOUT DB ################

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods ", "content": "I like pizza", "id": 2 }]


#--CREATE
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.Post):
    post_dict=post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": my_posts}

#--READ
@router.get("/posts")
def get_posts():
    return {"data": my_posts}

@router.get("/posts/latest")
def get_post():
    post = my_posts[len(my_posts)-1]
    return {"post detail": post}

@router.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"post with id: {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post detail": post}

#DELETE
@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index=find_index_post(id)
    if index == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    my_posts.pop(index)
    #return {"message": f"post with id:{id} was sucessfully deleted"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#UPDATE
@router.put("/posts/{id}")
def update_post(id: int, post: schemas.Post):
    index=find_index_post(id)
    if index == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exist")
    
    post_dict=post.dict()
    post_dict["id"]=id
    my_posts[index] = post_dict
    return {"data": post_dict}


####### END REGION - WITHOUT DB  ################

####### REGION - HELPER METHODS
def find_post(id):
     for p in my_posts:
         if p['id']==id:
             return p       

def find_index_post(id):
     for i, p in enumerate(my_posts):
         if p['id'] == id:
             return i

########## END REGION