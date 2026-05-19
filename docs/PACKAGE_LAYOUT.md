# Package Layout — canonical vs. legacy

This file is the rule that resolves the four overlapping Python layouts
documented in [AUDIT_architecture.md §3](AUDIT_architecture.md). It is the
contract Phase 0 of the roadmap enforces.

## Canonical: `src/wheelchair/`

All new code goes here. It is the most mature layer: rich interfaces
(`interfaces.py`), real controller-family signal models
(`controller_families.py`), realistic emulator (`emulator/`), and now the
safety subsystem (`safety/`) introduced for audit gap G-01.

The Python package is imported as `wheelchair` (pyproject pythonpath maps
`src/` onto sys.path).

## Legacy — being phased out

| Package | Status | Replacement | Deadline |
|---------|--------|-------------|----------|
| `wheelchair_controller/` | **DEPRECATED** | `wheelchair.drives.hardware.l298n` (Phase 0/1) | Phase 1 end |
| `wheelchair_bot/` (root pkg) | partially folded in | safety + wheelchairs models migrate into `wheelchair.*` | Phase 0 end |
| `packages/backend/` | **DEPRECATED** | `wheelchair.app.server` (FastAPI + WS, Phase 2) | Phase 2 end |
| `packages/shared/` | **DEPRECATED** | `wheelchair.interfaces` covers this | Phase 0 end |
| `packages/frontend/` | retained as `web/` | rename in Phase 2 | Phase 2 |

## Enforcement

`scripts/check_deprecated_imports.py` (added in Phase 0) fails CI if a
non-test file imports any deprecated package after the deadline for that
package has passed. Until the deadline, it only warns.

## Contributor rule

> If you are adding a feature and find yourself opening a file in a
> deprecated package, **stop**. Move the file (or your new code) into
> `src/wheelchair/` first. Open a separate PR for the move if it's large.
