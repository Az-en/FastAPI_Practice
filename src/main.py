from fastapi import FastAPI
from src.api.userRoutes import userRouter
from src.api.courseRoutes import courseRouter
app = FastAPI()

app.include_router(userRouter)
app.include_router(courseRouter)