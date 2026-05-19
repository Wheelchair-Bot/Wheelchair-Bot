"""Unit tests for the comma.ai integration scaffolding (Phase 4)."""

from __future__ import annotations

import pytest

from wheelchair.adapters import RNetAdapter
from wheelchair.comma.cereal_client import cereal_present, publish, recv, subscribe
from wheelchair.comma.panda import FakePanda, PandaBridge, SafetyMode
from wheelchair.comma.supervisor import ProcessSpec, Supervisor
from wheelchair.comma.topics import Topic
from wheelchair.drives.comma_panda import CommaPandaDrive


# -------- cereal_client (fallback bus path) --------


def test_cereal_client_fallback_round_trip() -> None:
    # On a dev machine cereal isn't installed; we use the in-process bus.
    if cereal_present():
        pytest.skip("real cereal present; in-process fallback not exercised")
    publish(Topic.WCBOT_STATE, {"linear_velocity": 0.5})
    msg = recv(Topic.WCBOT_STATE)
    assert msg == {"linear_velocity": 0.5}


def test_cereal_client_subscribe_callback() -> None:
    if cereal_present():
        pytest.skip("subscribe() is fallback-only by design")
    got: list = []
    subscribe(Topic.WCBOT_TELEMETRY, lambda m: got.append(m))
    publish(Topic.WCBOT_TELEMETRY, {"v": 1})
    publish(Topic.WCBOT_TELEMETRY, {"v": 2})
    assert got == [{"v": 1}, {"v": 2}]


# -------- panda safety modes --------


def test_panda_blocks_send_in_nooutput() -> None:
    panda = FakePanda()
    bridge = PandaBridge(panda=panda)
    with pytest.raises(PermissionError):
        bridge.send(0x100, b"\x00\x01", bus=0)


def test_panda_sends_when_enabled() -> None:
    panda = FakePanda()
    bridge = PandaBridge(panda=panda)
    bridge.enable_output()
    bridge.send(0x100, b"\xaa\xbb")
    assert panda.sent[0][0] == 0x100
    assert panda.sent[0][2] == b"\xaa\xbb"


def test_panda_heartbeat_counts() -> None:
    panda = FakePanda()
    bridge = PandaBridge(panda=panda)
    bridge.heartbeat()
    bridge.heartbeat()
    assert panda.heartbeats == 2


# -------- CommaPandaDrive end-to-end --------


def test_comma_panda_drive_routes_through_adapter_and_panda() -> None:
    panda = FakePanda(safety_mode=SafetyMode.ALLOUTPUT)
    bridge = PandaBridge(panda=panda)
    drive = CommaPandaDrive(adapter=RNetAdapter(), bridge=bridge)
    drive.attach_deadman(True)
    drive.set_motor_speeds(0.5, 0.5)
    assert panda.sent, "expected at least one panda send"
    addr, _, data, bus = panda.sent[0]
    assert bus == 0
    # The R-Net codec encodes joystick; centre stick = ~zero bytes.
    assert addr != 0


def test_comma_panda_drive_emergency_stop_disables_output() -> None:
    panda = FakePanda(safety_mode=SafetyMode.ALLOUTPUT)
    bridge = PandaBridge(panda=panda)
    drive = CommaPandaDrive(adapter=RNetAdapter(), bridge=bridge)
    drive.emergency_stop()
    assert panda.safety_mode is SafetyMode.NOOUTPUT


def test_comma_panda_drive_without_deadman_emits_safe_idle() -> None:
    panda = FakePanda(safety_mode=SafetyMode.ALLOUTPUT)
    bridge = PandaBridge(panda=panda)
    drive = CommaPandaDrive(adapter=RNetAdapter(), bridge=bridge)
    drive.attach_deadman(False)
    drive.set_motor_speeds(1.0, 1.0)  # user wants full speed
    addr, _, data, _ = panda.sent[0]
    # Safe-idle: first two bytes (x, y) are zero.
    assert data[0] == 0 and data[1] == 0


# -------- supervisor --------


def test_supervisor_runs_processes() -> None:
    ran: list[str] = []
    sup = Supervisor(
        processes=[
            ProcessSpec(name="a", target=lambda: ran.append("a"), essential=False),
            ProcessSpec(name="b", target=lambda: ran.append("b"), essential=False),
        ],
        on_essential_failure=lambda _n: None,
    )
    sup.start()
    import time as _t

    _t.sleep(0.05)
    assert set(ran) == {"a", "b"}


def test_supervisor_essential_failure_triggers_callback() -> None:
    fails: list[str] = []
    sup = Supervisor(
        processes=[
            ProcessSpec(name="essential", target=lambda: None, essential=True),
        ],
        on_essential_failure=lambda name: fails.append(name),
    )
    sup.start()
    import time as _t

    _t.sleep(0.05)
    assert fails == ["essential"]
