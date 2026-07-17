from fastapi import FastAPI, Request, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from src.api.userRoutes import userRouter
from src.api.courseRoutes import courseRouter
from src.core.exceptions import ApplicationError,NotFoundError,ConflictError,PermissionDeniedError 
app = FastAPI()

STATUS_MAP = {
	NotFoundError:status.HTTP_404_NOT_FOUND,
	ConflictError:status.HTTP_409_CONFLICT,
	PermissionDeniedError: status.HTTP_403_FORBIDDEN,
}

@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
	return JSONResponse(
		status_code=500,
		content={
			"detail": "The server returned an invalid response.",
			"errors": exc.errors(),
		},
	)

@app.exception_handler(ApplicationError)
async def application_exception_handler(request: Request, exc: ApplicationError):
	status_code = STATUS_MAP.get(type(exc))
	return JSONResponse(
		status_code=status_code,
		content={"detail": exc.message, "error_code": type(exc).__name__}
	)

app.include_router(userRouter)
app.include_router(courseRouter)