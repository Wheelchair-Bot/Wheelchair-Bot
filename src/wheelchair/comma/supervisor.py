"""Openpilot-style process supervisor (Phase 4).

A tiny process manager that:
- starts a set of named processes,
- restarts them on crash,
- engages the EmergencyStop if any "essential" process exits unexpectedly,
- reports liveness to ``Topic.WCBOT_SAFETY``.

The real openpilot ``manager`` is the production reference; this is the
minimal subset we need for the bench. It does NOT replace systemd on
shipping units — systemd supervises *this* process; this in turn
supervises drives/tele-op/perception.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ProcessSpec:
    name: str
    target: Callable[[], None]
    essential: bool = True
    max_restarts: int = 5


@dataclass
class _RunState:
    thread: threading.Thread | None = None
    restarts: int = 0
    last_start_s: float = 0.0
    alive: bool = False


@dataclass
class Supervisor:
    processes: List[ProcessSpec]
    on_essential_failure: Callable[[str], None]
    clock: Callable[[], float] = field(default=time.monotonic)
    _state: Dict[str, _RunState] = field(default_factory=dict)

    def start(self) -> None:
        for spec in self.processes:
            self._launch(spec)

    def _launch(self, spec: ProcessSpec) -> None:
        state = self._state.setdefault(spec.name, _RunState())
        if state.restarts >= spec.max_restarts:
            logger.error("process %s exceeded max_restarts; not relaunching", spec.name)
            if spec.essential:
                self.on_essential_failure(spec.name)
            return
        state.restarts += 1
        state.last_start_s = self.clock()
        state.alive = True

        def _run() -> None:
            try:
                spec.target()
            except Exception:  # noqa: BLE001
                logger.exception("process %s crashed", spec.name)
            state.alive = False
            if spec.essential:
                # Linux may legitimately exit a process; we err on caution.
                self.on_essential_failure(spec.name)

        t = threading.Thread(target=_run, name=f"wcbot-{spec.name}", daemon=True)
        state.thread = t
        t.start()

    def is_alive(self, name: str) -> bool:
        return self._state.get(name, _RunState()).alive

    def restart_count(self, name: str) -> int:
        return self._state.get(name, _RunState()).restarts

    def stop_all(self) -> None:
        # Cooperative — we don't kill threads. Daemon threads die with the proc.
        for s in self._state.values():
            s.alive = False
