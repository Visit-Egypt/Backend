from typing import List
from fastapi import HTTPException
from pydantic import errors
from pydantic.main import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse


class HTTPErrorModel(BaseModel):
    errors: List[str]
    status_code: str


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        {"errors": [exc.detail], "status_code": str(exc.status_code)},
        status_code=exc.status_code,
    )
