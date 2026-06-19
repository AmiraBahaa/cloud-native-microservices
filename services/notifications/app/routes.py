import json
import os

import httpx
import redis
from fastapi import APIRouter, Depends, Header, HTTPException

router = APIRouter()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8000")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


async def get_current_user(authorization: str = Header(...)) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{AUTH_SERVICE_URL}/auth/verify/",
                headers={"authorization": authorization},
                timeout=5.0,
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Unauthorized")
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")


@router.get("/")
async def get_notifications(user: dict = Depends(get_current_user)):
    raw = redis_client.lrange(f"notifications:{user['username']}", 0, -1)
    notifications = [json.loads(n) for n in raw]
    return {"notifications": notifications, "total": len(notifications)}


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str, user: dict = Depends(get_current_user)):
    key = f"notifications:{user['username']}"
    raw = redis_client.lrange(key, 0, -1)
    for i, n in enumerate(raw):
        notification = json.loads(n)
        if notification["id"] == notification_id:
            notification["read"] = True
            redis_client.lset(key, i, json.dumps(notification))
            return {"message": "Notification marked as read"}
    raise HTTPException(status_code=404, detail="Notification not found")
