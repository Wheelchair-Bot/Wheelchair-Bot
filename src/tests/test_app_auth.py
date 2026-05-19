"""Auth tests (G-23)."""

from __future__ import annotations

from wheelchair.app.auth import TokenStore, new_token


def test_unknown_token_rejected() -> None:
    store = TokenStore()
    store.add(new_token())
    assert store.verify("not-the-token") is False
    assert store.verify(None) is False
    assert store.verify("") is False


def test_known_token_accepted() -> None:
    store = TokenStore()
    t = new_token()
    store.add(t)
    assert store.verify(t) is True


def test_multiple_tokens_one_per_device() -> None:
    store = TokenStore()
    a, b = new_token(), new_token()
    store.add(a)
    store.add(b)
    assert store.verify(a)
    assert store.verify(b)
    assert not store.verify(new_token())


def test_token_uniqueness() -> None:
    seen = {new_token() for _ in range(1000)}
    assert len(seen) == 1000
