from typing import List, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_cashflow_agent
from database.db import get_db


router = APIRouter(prefix="/agent", tags=["agent"])


class EvaluateRequest(BaseModel):
    merchant_id: str = "merchant-demo"
    language: Optional[str] = None
    execute_actions: bool = False


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict) -> None:
        stale_connections = []
        for websocket in self.connections:
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale_connections.append(websocket)
        for websocket in stale_connections:
            self.disconnect(websocket)


manager = ConnectionManager()


@router.post("/evaluate")
async def evaluate_agent(
    payload: EvaluateRequest,
    db: Session = Depends(get_db),
    cashflow_agent=Depends(get_cashflow_agent),
):
    evaluation = cashflow_agent.evaluate(
        db,
        payload.merchant_id,
        payload.language,
        execute_actions=payload.execute_actions,
    )
    await manager.broadcast({"type": "agent_update", "merchant_id": payload.merchant_id, "payload": evaluation})
    return evaluation


@router.websocket("/stream")
async def stream_updates(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
