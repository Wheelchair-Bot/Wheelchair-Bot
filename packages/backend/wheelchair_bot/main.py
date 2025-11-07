"""Main FastAPI application for Wheelchair Bot backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wheelchair_bot import __version__

app = FastAPI(
    title="Wheelchair Bot API",
    description="API for controlling and monitoring a wheelchair bot",
    version=__version__,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Wheelchair Bot API",
        "version": __version__,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/status")
async def get_status():
    """Get the current status of the wheelchair bot."""
    return {
        "battery_level": 85,
        "is_moving": False,
        "speed": 0,
        "direction": None,
    }


@app.post("/api/move")
async def move(direction: str, speed: int = 50):
    """
    Send a movement command to the wheelchair bot.

    Args:
        direction: Direction to move (forward, backward, left, right, stop)
        speed: Speed percentage (0-100)
    """
    if direction not in ["forward", "backward", "left", "right", "stop"]:
        return {"error": "Invalid direction"}

    if not 0 <= speed <= 100:
        return {"error": "Speed must be between 0 and 100"}

    return {
        "status": "success",
        "command": direction,
        "speed": speed,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
