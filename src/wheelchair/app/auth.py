"""Bearer-token auth for the tele-op WS endpoint (G-23).

Phase 2 uses a paired-device model:
- Pi prints a QR with `{base_url, token}` at first boot.
- Android scans → stores token in keystore.
- Every WS frame is opened with `Authorization: Bearer <token>` header
  or `?token=<token>` query string fallback for browsers that can't set
  headers on WS.

Tokens are 32 random bytes, base64 URL-safe. Stored hashed (sha256) on
the Pi. One token per paired device.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from typing import Iterable


def new_token() -> str:
    return secrets.token_urlsafe(32)


def _hash(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()


@dataclass
class TokenStore:
    """Constant-time bearer-token verifier.

    Args:
        hashed_tokens: iterable of sha256(token) bytes (32 bytes each).
            Stored hashed so a memory disclosure does not leak credentials.
    """

    hashed_tokens: list[bytes] = field(default_factory=list)

    def add(self, token: str) -> None:
        self.hashed_tokens.append(_hash(token))

    def verify(self, token: str | None) -> bool:
        if not token:
            return False
        candidate = _hash(token)
        # constant-time over all stored tokens
        ok = False
        for h in self.hashed_tokens:
            if hmac.compare_digest(candidate, h):
                ok = True
        return ok

    @classmethod
    def from_hex(cls, hex_lines: Iterable[str]) -> "TokenStore":
        return cls(hashed_tokens=[bytes.fromhex(h.strip()) for h in hex_lines if h.strip()])
