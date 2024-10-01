import asyncio

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn

from app.db.database import init_models
from app.endpoints.breeds import breedrouter
from app.endpoints.kittens import kittenrouter
from app.endpoints.login import loginrouter
from config import API_URL


app = FastAPI()


app.include_router(breedrouter, prefix=f'{API_URL}/breeds')
app.include_router(kittenrouter, prefix=f'{API_URL}/kittens')
app.include_router(loginrouter, prefix=f'{API_URL}/auth')


@app.exception_handler(ValidationError)
async def custom_pydantic_validation_error_handler(
    request: Request, exc: ValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


@app.exception_handler(ValidationException)
async def custom_fastapi_validation_error_handler(
    request: Request, exc: ValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


@app.exception_handler(RequestValidationError)
async def custom_fastapi_request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


if __name__ == '__main__':
    asyncio.run(init_models())
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True)
