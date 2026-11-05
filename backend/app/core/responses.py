from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any = None


class ApiResponse[T](BaseModel):
    """Every JSON endpoint returns this shape, so the client handles one format."""

    success: bool = True
    data: T | None = None
    error: ErrorBody | None = None


def error_response(
    status_code: int, code: str, message: str, details: Any = None
) -> JSONResponse:
    body = ApiResponse[None](
        success=False,
        error=ErrorBody(code=code, message=message, details=details),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())
