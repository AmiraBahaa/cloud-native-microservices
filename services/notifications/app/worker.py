import json
import os
import uuid
from datetime import datetime

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


def build_message(event: dict) -> str:
    event_type = event.get("event", "")
    if event_type == "order_created":
        return f"Your order for '{event.get('product')}' has been placed successfully."
    if event_type == "order_updated":
        return f"Order {event.get('order_id', '')[:8]} status updated to '{event.get('status')}'."
    return "You have a new notification."


def start_worker():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("order_events")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            event = json.loads(message["data"])
            notification = {
                "id": str(uuid.uuid4()),
                "username": event.get("username"),
                "event": event.get("event"),
                "message": build_message(event),
                "order_id": event.get("order_id"),
                "created_at": datetime.utcnow().isoformat(),
                "read": False,
            }
            key = f"notifications:{event.get('username')}"
            redis_client.lpush(key, json.dumps(notification))
            redis_client.ltrim(key, 0, 49)
        except Exception:
            pass
