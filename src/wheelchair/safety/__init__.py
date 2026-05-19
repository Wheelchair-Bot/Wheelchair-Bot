"""Safety subsystem.

Phase 0 / Phase 1 of the audit roadmap (docs/AUDIT_planning.md).
Closes G-01 (command watchdog) at the software layer; G-03/G-04 will add
GPIO-level enforcement and a hardware e-stop relay in Phase 1.
"""

from .watchdog import CommandWatchdog, WatchdogExpired

__all__ = ["CommandWatchdog", "WatchdogExpired"]
