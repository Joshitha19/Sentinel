"""
FastAPI Main Application Entry Point for SENTINEL.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes_domains import router as domains_router
from app.api.routes_train import router as train_router
from app.api.routes_candidates import router as candidates_router
from app.api.routes_eval import router as eval_router
from app.api.ws_stream import ws_manager

app = FastAPI(
    title="SENTINEL API",
    description="Self-Evolving Novelty and Rare-Event Intelligence through Learning",
    version="1.0.0"
)

# CORS configuration for local React + Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(domains_router)
app.include_router(train_router)
app.include_router(candidates_router)
app.include_router(eval_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SENTINEL Backend",
        "version": "1.0.0",
        "disclaimer": "PROPOSED research framework. Strictly synthetic/benchmark evaluations."
    }


@app.websocket("/ws/train")
async def websocket_training_stream(websocket: WebSocket):
    """Real-time bidirectional WebSocket stream for training telemetry."""
    await ws_manager.connect(websocket)
    try:
        # Keep connection open and accept optional client pings
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or client control
            if data == "ping":
                await websocket.send_text('{"event": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
