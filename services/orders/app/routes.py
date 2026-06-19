import json
import os
import uuid
from datetime import datetime

import httpx
import redis
from fastapi import APIRouter, Depends, Header, HTTPException

from app.models import OrderCreate, OrderStatus, OrderUpdate

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
async def list_orders(user: dict = Depends(get_current_user)):
    keys = redis_client.keys(f"order:{user['username']}:*")
    orders = [json.loads(redis_client.get(k)) for k in keys if redis_client.get(k)]
    return {"orders": orders, "total": len(orders)}


@router.post("/", status_code=201)
async def create_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    order_id = str(uuid.uuid4())
    order_data = {
        "id": order_id,
        "username": user["username"],
        "product": order.product,
        "quantity": order.quantity,
        "price": order.price,
        "status": OrderStatus.pending,
        "created_at": datetime.utcnow().isoformat(),
    }
    redis_client.set(f"order:{user['username']}:{order_id}", json.dumps(order_data))

    redis_client.publish("order_events", json.dumps({
        "event": "order_created",
        "order_id": order_id,
        "username": user["username"],
        "product": order.product,
        "timestamp": datetime.utcnow().isoformat(),
    }))
    return order_data


@router.get("/{order_id}")
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    order_json = redis_client.get(f"order:{user['username']}:{order_id}")
    if not order_json:
        raise HTTPException(status_code=404, detail="Order not found")
    return json.loads(order_json)


@router.put("/{order_id}")
async def update_order(
    order_id: str, update: OrderUpdate, user: dict = Depends(get_current_user)
):
    order_json = redis_client.get(f"order:{user['username']}:{order_id}")
    if not order_json:
        raise HTTPException(status_code=404, detail="Order not found")

    order = json.loads(order_json)
    if update.status:
        order["status"] = update.status
    if update.product:
        order["product"] = update.product
    if update.quantity:
        order["quantity"] = update.quantity
    if update.price:
        order["price"] = update.price
    order["updated_at"] = datetime.utcnow().isoformat()

    redis_client.set(f"order:{user['username']}:{order_id}", json.dumps(order))

    redis_client.publish(
        "order_events",
        json.dumps({
            "event": "order_updated",
            "order_id": order_id,
            "username": user["username"],
            "status": order["status"],
            "timestamp": datetime.utcnow().isoformat(),
        }),
    )
    return order


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: str, user: dict = Depends(get_current_user)):
    if not redis_client.exists(f"order:{user['username']}:{order_id}"):
        raise HTTPException(status_code=404, detail="Order not found")
    redis_client.delete(f"order:{user['username']}:{order_id}")
