#!/usr/bin/env python3
"""HIL smoke runner (placeholder until the bench rig exists).

Today: dry-run prints the test plan and exits 0.
Real implementation lands when the rig described in
docs/hardware/hil_bench_rig.md is built (issue #35).
"""

from __future__ import annotations

import argparse
import sys


HIL_TESTS = [
    ("test_estop_drop_time", "G-04", "MOTOR_CTRL_ENABLE low within 50 ms of engage()"),
    ("test_watchdog_drop_after_kill_9", "G-01", "PWM zero within 100 ms of SIGKILL"),
    (
        "test_deadman_release_drives_pwm_to_zero_at_gpio_level",
        "G-03",
        "PWM zero within 50 ms of operator release",
    ),
    ("test_overcurrent_trip_within_one_pwm_cycle", "G-02", "TRIP_N low within 10 ms of >Imax"),
    ("test_tilt_cutoff_sustains_under_vibration", "G-05", "engage at 25° held 200 ms"),
    ("test_battery_lvc_cuts_at_22_5V", "G-06", "cutoff at 22.5V sustained 1 s"),
    ("test_can_bus_fault_reverts_to_local_safe_state", "G-10", "stop on CAN silence"),
    ("test_wifi_loss_engages_deadman_within_500ms", "G-07", "control WS loss = deadman release"),
]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", help="ssh target (user@host) of the HIL rig", default=None)
    p.add_argument("--dry-run", action="store_true", default=True)
    args = p.parse_args()

    print(f"HIL test plan ({len(HIL_TESTS)} tests)")
    print("-" * 60)
    for name, gap, contract in HIL_TESTS:
        print(f"  {name}")
        print(f"    gap: {gap}")
        print(f"    contract: {contract}")

    if args.target is None or args.dry_run:
        print("\n(dry run — no rig configured; exiting 0)")
        return 0

    # Real impl: rsync repo to target; pytest -m hil over ssh; pull artefacts.
    print(f"\nWould ssh to {args.target} and run: pytest -m hil")
    return 0


if __name__ == "__main__":
    sys.exit(main())
