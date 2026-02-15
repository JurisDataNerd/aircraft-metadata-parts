from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/test")
async def test_drawing():
    return {"message": "Drawing endpoint ready"}