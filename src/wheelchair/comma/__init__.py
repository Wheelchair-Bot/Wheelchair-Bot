"""comma.ai integration (Phase 4).

Brings up the comma three / 3X (and, when its SDK lands, comma four)
as the compute + sensor + CAN-bridge platform. Reuses cereal IPC,
panda safety modes, openpilot's process-supervisor pattern.

See ``docs/comma/`` for setup, cereal topic mapping, and the safety
model the panda enforces independently of Linux.

Issues closed by this package's PRs:
- #42 G-24 comma three / 3X / four hardware support
- #43 G-25 camera / IMU / GPS fusion via cereal
- #44 G-26 openpilot-style supervisor + model runtime
"""

from .panda import PandaBridge
from .supervisor import Supervisor
from .topics import Topic

__all__ = ["PandaBridge", "Supervisor", "Topic"]
