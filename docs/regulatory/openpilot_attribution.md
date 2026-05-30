# Licence inventory & attribution

Wheelchair-Bot is MIT-licensed (see [LICENSE](../../LICENSE)).

## Reused / borrowed code & ideas

| Component | Upstream | Licence | How we use it |
|-----------|----------|---------|---------------|
| openpilot manager pattern | github.com/commaai/openpilot | MIT | inspiration for `wheelchair.comma.supervisor` (no code copy) |
| cereal IPC | github.com/commaai/cereal | MIT | runtime dependency on comma device; not bundled |
| panda firmware + python | github.com/commaai/panda | MIT | runtime dependency on comma device; not bundled |
| cabana capture format | github.com/commaai/openpilot | MIT | file format only; our `replay.py` parses CSV |
| FastAPI | github.com/tiangolo/fastapi | MIT | direct dep |
| Pydantic | github.com/pydantic/pydantic | MIT | direct dep |
| Three.js (simulator UI) | github.com/mrdoob/three.js | MIT | direct dep |
| markdown-it (site) | github.com/markdown-it/markdown-it | MIT | direct dep |

No GPL / AGPL code in the runtime tree. Regulatory submissions get a
fresh SBOM (cyclonedx) from `scripts/lock_deps.sh` outputs.
