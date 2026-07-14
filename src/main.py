from fastapi import FastAPI
from src.api.userRoutes import userRouter

app = FastAPI()

app.include_router(userRouter)