"""Common types and models for Wheelchair Bot."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Direction(str, Enum):
    """Movement directions."""

    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"


class BotStatus(BaseModel):
    """Status of the wheelchair bot."""

    battery_level: int = Field(ge=0, le=100, description="Battery level percentage")
    is_moving: bool = Field(default=False, description="Whether the bot is currently moving")
    speed: int = Field(ge=0, le=100, description="Current speed percentage")
    direction: Optional[Direction] = Field(default=None, description="Current movement direction")


class MoveCommand(BaseModel):
    """Command to move the wheelchair bot."""

    direction: Direction = Field(description="Direction to move")
    speed: int = Field(ge=0, le=100, default=50, description="Speed percentage")


class CommandResponse(BaseModel):
    """Response to a command."""

    status: str = Field(description="Status of the command (success, error)")
    message: Optional[str] = Field(default=None, description="Optional message")
