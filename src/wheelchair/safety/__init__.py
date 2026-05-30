"""Safety subsystem.

Phase 0 landed CommandWatchdog (G-01 software half).
Phase 1 adds DeadmanSwitch, TiltMonitor, LowVoltageCutoff,
OvercurrentMonitor, and the EmergencyStop coordinator (G-02..G-06
software halves). Hardware halves — INA226 board, e-stop relay PCB,
GPIO-level deadman wiring — are tracked in issues #20, #21, #22.
"""

from .current_limit import MotorCurrent, OvercurrentMonitor
from .deadman import DeadmanSwitch
from .estop import EmergencyStop, EStopEvent, EStopReason
from .lvc import LowVoltageCutoff, LVCState
from .tilt import TiltMonitor
from .watchdog import CommandWatchdog, WatchdogExpired

__all__ = [
    "CommandWatchdog",
    "WatchdogExpired",
    "DeadmanSwitch",
    "TiltMonitor",
    "LowVoltageCutoff",
    "LVCState",
    "OvercurrentMonitor",
    "MotorCurrent",
    "EmergencyStop",
    "EStopReason",
    "EStopEvent",
]
