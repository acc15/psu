import typing
import struct
import enum
import logging

def generic_to_bytes(v: typing.Any | None) -> bytes:
    if isinstance(v, bytes):
        return v
    if v is None:
        return b""
    if hasattr(v, "to_bytes") and callable(v.to_bytes):
        return v.to_bytes()
    if isinstance(v, float):
        return struct.pack("<f", v)
    raise RuntimeError(f"Unsupported payload type: {type(v)}, {v}")

class IntEnumWithHexStr(enum.IntEnum):
    def __str__(self):
        return f"{self.name}({self.value},0x{self.value:02X})>"
    

logging.basicConfig(
    format='[%(asctime)s][%(levelname)-5s] %(message)s',
    level=logging.INFO)