"""V3DPBD (pack-bit differential) image loader."""

from __future__ import annotations

import os
import struct
from pathlib import Path

import numpy as np

_PBD_FORMAT_KEY = "v3d_volume_pkbitdf_encod"


class PBD:
    """Loader for V3DPBD compressed image format."""

    def __init__(self) -> None:
        self.total_read_bytes = 0
        self.max_decompression_size = 0
        self.channel_len = 0
        self.compression_buffer = bytearray()
        self.decompression_buffer = bytearray()
        self.compression_pos = 0
        self.decompression_pos = 0
        self.decompression_prior = 0
        self.endian = "<"

    def _decompress_pbd8(self, compression_len: int) -> int:
        cp = 0
        dp = 0
        mask = 3
        while cp < compression_len:
            value = self.compression_buffer[self.compression_pos + cp]
            if value < 33:
                count = value + 1
                self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + count] = (
                    self.compression_buffer[
                        self.compression_pos + cp + 1 : self.compression_pos + cp + 1 + count
                    ]
                )
                cp += count + 1
                dp += count
                self.decompression_prior = self.decompression_buffer[self.decompression_pos + dp - 1]
            elif value < 128:
                left_to_fill = value - 32
                while left_to_fill > 0:
                    fill_num = min(left_to_fill, 4)
                    cp += 1
                    src = self.compression_buffer[self.compression_pos + cp]
                    to_fill = self.decompression_pos + dp
                    p0 = src & mask
                    src >>= 2
                    p1 = src & mask
                    src >>= 2
                    p2 = src & mask
                    src >>= 2
                    p3 = src & mask
                    pva = self.decompression_prior + (-1 if p0 == 3 else p0)
                    self.decompression_buffer[to_fill] = pva
                    if fill_num > 1:
                        to_fill += 1
                        pvb = pva + (-1 if p1 == 3 else p1)
                        self.decompression_buffer[to_fill] = pvb
                        if fill_num > 2:
                            to_fill += 1
                            pva = pvb + (-1 if p2 == 3 else p2)
                            self.decompression_buffer[to_fill] = pva
                            if fill_num > 3:
                                to_fill += 1
                                self.decompression_buffer[to_fill] = pva + (-1 if p3 == 3 else p3)
                    self.decompression_prior = self.decompression_buffer[to_fill]
                    dp += fill_num
                    left_to_fill -= fill_num
                cp += 1
            else:
                repeat_count = value - 127
                cp += 1
                repeat_value = self.compression_buffer[self.compression_pos + cp : self.compression_pos + cp + 1]
                self.decompression_buffer[
                    self.decompression_pos + dp : self.decompression_pos + dp + repeat_count
                ] = repeat_value * repeat_count
                dp += repeat_count
                self.decompression_prior = struct.unpack("B", repeat_value)[0]
                cp += 1
        return dp

    def _decompress_pbd16(self, compression_len: int) -> int:
        cp = 0
        dp = 0

        def get_pre() -> int:
            return struct.unpack(
                self.endian + "H",
                bytes(
                    self.decompression_buffer[
                        self.decompression_pos + dp - 2 : self.decompression_pos + dp
                    ]
                ),
            )[0]

        while cp < compression_len:
            code = self.compression_buffer[self.compression_pos + cp]
            if code < 32:
                count = code + 1
                self.decompression_buffer[
                    self.decompression_pos + dp : self.decompression_pos + dp + count * 2
                ] = self.compression_buffer[
                    self.compression_pos + cp + 1 : self.compression_pos + cp + 1 + count * 2
                ]
                cp += count * 2 + 1
                dp += count * 2
                self.decompression_prior = get_pre()
            elif code < 80:
                left_to_fill = code - 31
                while left_to_fill > 0:
                    cp += 1
                    src = self.compression_buffer[self.compression_pos + cp]
                    d0 = src >> 5
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", self.decompression_prior + (d0 if d0 < 5 else 4 - d0))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d1 = (src >> 2) & 7
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d1 if d1 < 5 else 4 - d1))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d2 = src & 3
                    carry = d2

                    cp += 1
                    src = self.compression_buffer[self.compression_pos + cp]
                    d0 = (src >> 7) | (carry << 1)
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d0 if d0 < 5 else 4 - d0))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d1 = (src >> 4) & 7
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d1 if d1 < 5 else 4 - d1))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d2 = (src >> 1) & 7
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d2 if d2 < 5 else 4 - d2))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d3 = src & 1
                    carry = d3

                    cp += 1
                    src = self.compression_buffer[self.compression_pos + cp]
                    d0 = (src >> 6) | (carry << 2)
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d0 if d0 < 5 else 4 - d0))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d1 = (src >> 3) & 7
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d1 if d1 < 5 else 4 - d1))
                    )
                    dp += 2
                    left_to_fill -= 1
                    if left_to_fill == 0:
                        break
                    d2 = src & 7
                    self.decompression_buffer[self.decompression_pos + dp : self.decompression_pos + dp + 2] = (
                        struct.pack(self.endian + "H", get_pre() + (d2 if d2 < 5 else 4 - d2))
                    )
                    dp += 2
                    left_to_fill -= 1
                self.decompression_prior = get_pre()
                cp += 1
            elif code < 223:
                raise ValueError("Unsupported mid-range PBD16 code")
            else:
                repeat_count = code - 222
                cp += 1
                repeat_value = self.compression_buffer[self.compression_pos + cp : self.compression_pos + cp + 2]
                self.decompression_buffer[
                    self.decompression_pos + dp : self.decompression_pos + dp + repeat_count * 2
                ] = repeat_value * repeat_count
                dp += repeat_count * 2
                cp += 2
                self.decompression_prior = struct.unpack(self.endian + "H", repeat_value)[0]
        return dp

    def _update_buffer8(self) -> None:
        look_ahead = self.compression_pos
        while look_ahead < self.total_read_bytes:
            lav = self.compression_buffer[look_ahead]
            if lav < 33:
                if look_ahead + lav + 1 < self.total_read_bytes:
                    look_ahead += lav + 2
                else:
                    break
            elif lav < 128:
                compressed_diff_entries = (lav - 33) // 4 + 1
                if look_ahead + compressed_diff_entries < self.total_read_bytes:
                    look_ahead += compressed_diff_entries + 1
                else:
                    break
            else:
                if look_ahead + 1 < self.total_read_bytes:
                    look_ahead += 2
                else:
                    break
        compression_len = look_ahead - self.compression_pos
        d_length = self._decompress_pbd8(compression_len)
        self.compression_pos = look_ahead
        self.decompression_pos += d_length

    def _update_buffer16(self) -> None:
        look_ahead = self.compression_pos
        while look_ahead < self.total_read_bytes:
            lav = self.compression_buffer[look_ahead]
            if lav < 32:
                if look_ahead + (lav + 1) * 2 < self.total_read_bytes:
                    look_ahead += (lav + 1) * 2 + 1
                else:
                    break
            elif lav < 80:
                diff_bytes = int(((lav - 31) * 3 / 8) - 0.0001) + 1
                if look_ahead + diff_bytes < self.total_read_bytes:
                    look_ahead += diff_bytes + 1
                else:
                    break
            elif lav < 183:
                diff_bytes = int(((lav - 79) * 4 / 8) - 0.0001) + 1
                if look_ahead + diff_bytes < self.total_read_bytes:
                    look_ahead += diff_bytes + 1
                else:
                    break
            elif lav < 223:
                diff_bytes = int(((lav - 182) * 5 / 8) - 0.0001) + 1
                if look_ahead + diff_bytes < self.total_read_bytes:
                    look_ahead += diff_bytes + 1
                else:
                    break
            else:
                if look_ahead + 2 < self.total_read_bytes:
                    look_ahead += 3
                else:
                    break
        compression_len = look_ahead - self.compression_pos
        d_length = self._decompress_pbd16(compression_len)
        self.compression_pos = look_ahead
        self.decompression_pos += d_length

    def load_image(self, path: str | Path) -> np.ndarray:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        self.decompression_prior = 0
        with p.open("rb") as f:
            file_size = os.path.getsize(p)
            header_sz = 4 * 4 + 2 + 1 + len(_PBD_FORMAT_KEY)
            if file_size < header_sz:
                raise ValueError("Invalid v3dpbd file: too small")
            fmt = f.read(len(_PBD_FORMAT_KEY)).decode("utf-8")
            if fmt != _PBD_FORMAT_KEY:
                raise ValueError("Invalid v3dpbd format key")
            endian_code = f.read(1).decode("utf-8")
            if endian_code == "B":
                self.endian = ">"
            elif endian_code == "L":
                self.endian = "<"
            else:
                raise ValueError("Invalid endian code in v3dpbd")
            datatype = struct.unpack(self.endian + "h", f.read(2))[0]
            if datatype in (1, 33):
                dt = "u1"
            elif datatype == 2:
                dt = "u2"
            else:
                raise ValueError("Unsupported v3dpbd datatype")
            if datatype == 33:
                raise ValueError("Datatype 33 is currently not supported")

            sx, sy, sz, sc = struct.unpack(self.endian + "iiii", f.read(4 * 4))
            total_unit = sx * sy * sz * sc
            compressed_bytes = file_size - header_sz
            self.max_decompression_size = total_unit * (2 if datatype == 2 else 1)
            self.channel_len = sx * sy * sz
            read_step_size = 1024 * 20000
            self.total_read_bytes = 0
            self.compression_buffer = bytearray(compressed_bytes)
            self.decompression_buffer = bytearray(self.max_decompression_size)

            remaining = compressed_bytes
            while remaining > 0:
                current = min(remaining, read_step_size)
                new_bytes = f.read(current)
                self.compression_buffer[self.total_read_bytes : self.total_read_bytes + current] = new_bytes
                self.total_read_bytes += current
                remaining -= current
                if datatype == 1:
                    self._update_buffer8()
                elif datatype == 2:
                    self._update_buffer16()

            img = np.frombuffer(self.decompression_buffer, self.endian + dt)
            return img.reshape((sc, sz, sy, sx))


def load_v3dpbd(path: str | Path) -> np.ndarray:
    """Load V3DPBD file into ndarray in (c,z,y,x) shape."""
    return PBD().load_image(path)
