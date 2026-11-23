#!/usr/bin/env python3
"""World news poster for Monday 23 November 2026.

This program writes one image to the grader's output directory:
``$MAKEFUN_OUTPUT_DIR/entry.png`` (falling back to ``/output``).

The image itself is shipped in this repository as ``poster.png.b64`` — a
single-line base64 encoding of a 1024x1024 PNG front page that sums up the
day's world news (Iran war, COP31 collapse, Ukraine, Gaza, the US House,
and the Chapo Isidro capture). Nothing is fetched from the network and
nothing is drawn at run time: the program only decodes the bundled asset
and copies it to the output directory, so two runs always write the
identical bytes.

Pure Python standard library. No writes into the repository.
"""

import base64
import hashlib
import os
import struct
import sys

ASSET_NAME = "poster.png.b64"
OUTPUT_NAME = "entry.png"

# The poster bytes this program expects. The hash is checked before
# anything is written, so a damaged or swapped asset fails loudly
# instead of producing a wrong image.
EXPECTED_SHA256 = "5641e5ecd950db2c5c50dcb3593a11b595dc350c2a06763f2ca2523ad72d22b3"
EXPECTED_SIZE = 615544
MAX_OUTPUT_BYTES = 1_048_576


def _repo_dir():
    """Directory holding this script (read-only at grade time)."""
    return os.path.dirname(os.path.abspath(__file__))


def _check_png(raw):
    """Refuse anything that is not a 1024x1024 PNG before writing it out."""
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("poster is not a PNG file")
    if len(raw) < 33 or raw[12:16] != b"IHDR":
        raise SystemExit("poster has no IHDR chunk")
    width, height = struct.unpack(">II", raw[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit(
            "poster is %dx%d, expected 1024x1024" % (width, height)
        )


def _load_poster_bytes():
    """Decode the bundled poster and verify it byte for byte."""
    asset_path = os.path.join(_repo_dir(), ASSET_NAME)
    with open(asset_path, "r", encoding="ascii") as handle:
        encoded = handle.read()
    raw = base64.b64decode("".join(encoded.split()), validate=True)
    if len(raw) != EXPECTED_SIZE:
        raise SystemExit(
            "poster size mismatch: got %d bytes, expected %d"
            % (len(raw), EXPECTED_SIZE)
        )
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("poster sha256 mismatch: got %s" % digest)
    _check_png(raw)
    return raw


def _output_path():
    """Destination inside the writable output directory only."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    repo = os.path.realpath(_repo_dir())
    target = os.path.realpath(out_dir)
    if target == repo or target.startswith(repo + os.sep):
        raise SystemExit("refusing to write into the repository")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, OUTPUT_NAME)


def main():
    raw = _load_poster_bytes()
    if len(raw) > MAX_OUTPUT_BYTES:
        raise SystemExit("poster exceeds the 1 MiB limit")
    dest = _output_path()
    with open(dest, "wb") as handle:
        handle.write(raw)
    print(
        "wrote %s (%d bytes, sha256 %s)"
        % (dest, len(raw), hashlib.sha256(raw).hexdigest())
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
