"""Bounded probes executed inside a Docker ``--network none`` container."""

from __future__ import annotations

import json
import socket
import urllib.request
from typing import Callable


def _denied(operation: Callable[[], object]) -> str:
    try:
        operation()
    except Exception:  # The artifact records only denied/succeeded, never secrets.
        return "denied"
    return "succeeded"


def probe_network_denial() -> dict[str, str]:
    return {
        "schema_version": "no-egress-probe/1.0.0",
        "dns": _denied(lambda: socket.getaddrinfo("example.com", 443)),
        "literal_ip_socket": _denied(
            lambda: socket.create_connection(("1.1.1.1", 443), timeout=1)
        ),
        "http": _denied(
            lambda: urllib.request.urlopen("http://example.com/", timeout=1).read(1)
        ),
    }


def main() -> int:
    payload = probe_network_denial()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if set(payload.values()) == {"no-egress-probe/1.0.0", "denied"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

