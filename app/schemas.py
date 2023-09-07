from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional

# schema / pydantic model - specify define structure that we expect on a request
#                        - ensures that body of a request match up to what we want 

class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime


##################   POST  ########################################################################

class Post(BaseModel):  # This means it will extent the BaseModel
    title: str
    content: str
    published: bool = True
    #rating: Optional[int] = None


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase): 
    # it inherit the other columns from the PostBase class, i only specify the new columns
    id: int 
    created_at: datetime
    owner_id: int
    owner : UserResponse


    class Config:   # --> Added to fix error at 5:44 but i didnt got the error
        orm_mode = True


class PostOut(BaseModel): 
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True




##########################################################################################

##################   USER  ###############################################################

class UserCreate(BaseModel):
    email : EmailStr
    password: str


    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email : EmailStr
    password : str


class Token (BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id: Optional[str] = None


    
class Vote(BaseModel):
    post_id: int
    dir: conint(ge=0, le=1)  # only allow numbers greater or equal to 0 and less or equal to 1 (in our case we want 0 or 1) 

