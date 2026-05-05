"""Small grayscale PNG writer used for CodaBench ZIPs."""

from __future__ import annotations

import struct
import zlib

import numpy as np


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(payload, checksum)
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", checksum & 0xFFFFFFFF)


def grayscale_png(width: int, height: int, values) -> bytes:
    array = np.asarray(values, dtype="uint8")
    if array.shape != (height, width):
        raise ValueError(f"expected mask shape {(height, width)}, got {array.shape}")
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    rows = [bytes([0]) + array[row].tobytes() for row in range(height)]
    raw = b"".join(rows)
    return signature + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, level=9)) + png_chunk(b"IEND", b"")
