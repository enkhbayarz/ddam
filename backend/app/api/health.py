from fastapi import APIRouter

from app.core.responses import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> ApiResponse[dict[str, str]]:
    return ApiResponse(data={"status": "ok"})
