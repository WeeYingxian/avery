"""Write avery.ico for the desktop shortcut.

A 32x32 and a 16x16 icon in the plan's own teal, drawn straight into ICO
format so there is no image library to install. Run once; re-run only if
you want to change the colours.
"""

import pathlib
import struct

TEAL = (0x0F, 0x6B, 0x5F)      # matches the page accent
LIGHT = (0xE1, 0xEF, 0xEB)     # the accent wash


def pixels(size):
    """Rounded teal tile with a lighter circle, as RGBA rows, top row first."""
    r = size * 0.22                      # corner radius
    cx = cy = (size - 1) / 2
    dot = size * 0.26                    # circle radius
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            # rounded-rectangle test: only the corner quadrants use the radius
            qx = max(r - x, x - (size - 1 - r), 0)
            qy = max(r - y, y - (size - 1 - r), 0)
            inside = (qx * qx + qy * qy) <= r * r
            if not inside:
                row.append((0, 0, 0, 0))
                continue
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            row.append((*LIGHT, 255) if d <= dot else (*TEAL, 255))
        rows.append(row)
    return rows


def image_blob(size):
    rows = pixels(size)
    # BITMAPINFOHEADER: height is doubled to cover the colour and mask planes
    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    xor = bytearray()
    for row in reversed(rows):                      # DIBs are stored bottom-up
        for red, green, blue, alpha in row:
            xor += bytes((blue, green, red, alpha))  # BGRA
    mask_row = (size + 31) // 32 * 4                 # 1bpp, padded to 4 bytes
    return header + bytes(xor) + bytes(mask_row * size)


def main():
    sizes = (32, 16)
    blobs = [image_blob(s) for s in sizes]
    offset = 6 + 16 * len(sizes)
    out = bytearray(struct.pack("<HHH", 0, 1, len(sizes)))
    for size, blob in zip(sizes, blobs):
        out += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    for blob in blobs:
        out += blob

    path = pathlib.Path(__file__).parent / "avery.ico"
    path.write_bytes(bytes(out))
    print(f"{path.name} written: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
