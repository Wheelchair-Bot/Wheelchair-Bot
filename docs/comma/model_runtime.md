# Model runtime (G-26)

Phase 4d — load an openpilot-style ONNX model into the supervised
process, with the wheelchair use-case constraints:

- **No road operation.** Operational design domain is indoor + sidewalk only.
- **Path-following only, no decision-making.** The model proposes a
  short-horizon trajectory; the operator's tele-op input is the
  authoritative source. Path proposals modulate speed limits and
  obstacle warnings, never override deadman or e-stop.
- **Comma DSP / GPU for inference**; do not run on Pi-class compute.

## File layout

```
src/wheelchair/perception/
    __init__.py
    model_loader.py     # ONNX loader; warms compute on supervisor start
    inference.py        # runs at 20 Hz against roadCameraState
    obstacle_map.py     # turns model output into a depth grid
    policy.py           # speed-limit + warning logic (no actuation)
```

Lands in a follow-up to the Phase 4 PR once the bench bring-up is solid.
