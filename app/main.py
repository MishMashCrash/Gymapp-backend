from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, auth, exercise, split,   workout

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(exercise.router)
app.include_router(split.router)
app.include_router(workout.router)

@app.get("/")
async def root():
    return {"message": "Lets Get Jacked"}