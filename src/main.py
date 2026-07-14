from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from src.api.userRoutes import userRouter
from src.api.courseRoutes import courseRouter
app = FastAPI()


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
	return JSONResponse(
		status_code=500,
		content={
			"detail": "The server returned an invalid response.",
			"errors": exc.errors(),
		},
	)

app.include_router(userRouter)
app.include_router(courseRouter)