# Docker images

Phase 0 / Phase 1 of the audit roadmap. Closes [G-21](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/39).

The single Docker image that came with this project stripped `RPi.GPIO`
entirely — so the "production" container could not drive a motor. That
broke the implicit contract of the image name. Phase 0 splits the build
into two clearly-named images.

## Two images

| Image | Dockerfile | Arch | GPIO | Use case |
|-------|------------|------|------|----------|
| `wheelchair-bot:sim` | [Dockerfile.sim](../Dockerfile.sim) | any | none | CI, dev laptops, emulator demos, cloud sim |
| `wheelchair-bot:pi`  | [Dockerfile.pi](../Dockerfile.pi)   | linux/arm64 | RPi.GPIO + lgpio + libcamera | runs on real Pi hardware |

The two images do not share runtime artefacts. `:sim` ships
`requirements/sim.lock`; `:pi` requires `requirements/pi.lock` (which is
linux/arm64-only and is generated out-of-band; see
[../requirements/README.md](../requirements/README.md)).

## Local dev

```bash
docker compose up --build dev    # interactive shell (Dockerfile.sim, target=development)
docker compose run --rm test     # pytest                (Dockerfile.sim, target=testing)
docker compose up --build sim    # tele-op server on 8080 (Dockerfile.sim, target=production-sim)
```

`docker-compose.yml` deliberately never references `Dockerfile.pi` —
running the Pi image on a non-Pi host would silently fail to find
`/dev/gpiomem`.

## Production Pi build

On a build host with `docker buildx`:

```bash
# 1. Generate the arm64 lock file (one-off; recommit when deps change).
docker run --rm --platform linux/arm64 -v $PWD:/wcbot -w /wcbot \
    python:3.11-slim-bookworm \
    sh -c "pip install pip-tools && pip-compile --strip-extras \
           --output-file=requirements/pi.lock requirements/pi.in"

# 2. Build the Pi image.
docker buildx build --platform linux/arm64 \
    -f Dockerfile.pi -t wheelchair-bot:pi --load .
```

## Running on a real Pi

```bash
# The runtime container MUST get access to the host's GPIO + I²C nodes.
docker run --rm \
    --device /dev/gpiomem \
    --device /dev/i2c-1 \
    -p 8000:8000 -p 8080:8080 \
    wheelchair-bot:pi
```

If `/dev/gpiomem` is missing the container will fail on startup rather
than silently mocking the GPIO — this is intentional after the Phase 0
audit (no more "production runs in mock mode").

## Why not one image?

- A single image needs to either ship `RPi.GPIO` everywhere (fails to
  install on x86_64 dev machines) or skip it (the previous footgun:
  prod image couldn't drive motors).
- A single image plus a runtime flag (`--mock`) hides the failure mode
  one CLI option deep; the audit found teams running the Docker image
  thinking it was driving hardware when it wasn't.
- Splitting the image makes the failure mode obvious: if you want
  hardware control, you have to pull the `:pi` image. If you pulled
  `:sim` you cannot accidentally drive a real chair.
