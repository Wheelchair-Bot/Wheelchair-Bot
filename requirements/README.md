# Pinned dependencies

Source-of-truth `.in` files + `pip-compile`-generated `.lock` files.

Audit gap [G-19](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/37).

## Layout

| File | Target | Includes |
|------|--------|----------|
| `base.in` | shared runtime | pydantic, pyyaml, websockets, fastapi |
| `sim.in` | CI / dev laptop / sim container | base |
| `pi.in` | Raspberry Pi production | base + RPi.GPIO + lgpio |
| `dev.in` | dev + CI test runners | sim + pytest + ruff + black + mypy + httpx + pip-tools |
| `*.lock` | machine-pinned outputs | regenerate with `scripts/lock_deps.sh` |

## Regeneration

```bash
# In a venv with pip-tools installed:
scripts/lock_deps.sh
```

`pi.lock` is **not** generated on dev machines because it pins
`linux_aarch64` wheels that don't resolve on macOS / x86_64 Linux.
Generate it on a Pi or via a multiarch Docker buildx:

```bash
docker run --rm --platform linux/arm64 -v $PWD:/wcbot -w /wcbot python:3.11-slim-bookworm \
    sh -c "pip install pip-tools && pip-compile --strip-extras --output-file=requirements/pi.lock requirements/pi.in"
```

## Why platform-specific?

`RPi.GPIO` does not have macOS wheels — generating `pi.lock` from a Mac
would either fail or pull in pure-Python fallbacks that don't actually
talk to GPIO at runtime. Splitting the lock files by target avoids the
trap of "it locks fine on my laptop, then fails to install on the Pi".

## Legacy `requirements*.txt` at repo root

Phase 0 deprecation. They re-export the corresponding `.in` files via
`-r requirements/<name>.in` so existing `pip install -r requirements.txt`
incantations keep working. They will be deleted at the end of Phase 0.
