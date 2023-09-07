from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware


# This is not necessary anymore since we are using alembic
# models.Base.metadata.create_all(bind=engine)
app=FastAPI()

origins = ["https://www.google.com", "https://www.youtube.com"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, # Domains allowed to talk to our API
    allow_credentials=True, 
    allow_methods=["*"], # http methods allowed (get/post/put/delete)
    allow_headers=["*"], # heades allowed
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

