"""Leitura minima de PBO do DayZ (formato ``\\0sreV``).

Sem dependencia de DayZ Tools. Usado apenas pelo script de correcao do
BaseBuildingPlus (`patch_bbp.py`).

Formato do header (DayZ SA / Enfusion):

    "\\0sreV" + 16 bytes 0x00
    propriedades: key\\0value\\0 ... key\\0value\\0 \\0
    entradas:     nome\\0 + <IIIII (mime, tamanho_original, offset, timestamp, tamanho_dados)
    terminador:   \\0
    "trailer" de 19 bytes (geralmente zeros)
    dados das entradas, na ordem do header

`mime` 0 = dados crus; ``0x43707273`` ("Cprs") = LZSS comprimido.
"""

import struct

MAGIC = b"\x00sreV"
CPRS = 0x43707273


def read_pbo(path):
    """Le um PBO e devolve ``(data, data_start, entries)``.

    ``entries`` e uma lista de ``[nome, mime, tamanho_original, tamanho_dados]``.
    O offset real de cada entrada e calculado de forma sequencial a partir de
    ``data_start`` (o campo `offset` do header costuma vir 0).
    """
    with open(path, "rb") as f:
        data = f.read()

    if data[:5] != MAGIC:
        raise ValueError("nao e um PBO do DayZ: %s" % path)

    pos = 5 + 16

    # bloco de propriedades (product, prefix, ...)
    while True:
        end = data.index(b"\x00", pos)
        key = data[pos:end]
        pos = end + 1
        if not key:
            break
        end = data.index(b"\x00", pos)
        pos = end + 1

    entries = []
    while True:
        end = data.index(b"\x00", pos)
        name = data[pos:end].decode("latin-1")
        pos = end + 1
        if not name:
            break
        mime, orig, _off, _ts, dsize = struct.unpack("<IIIII", data[pos:pos + 20])
        pos += 20
        entries.append([name, mime, orig, dsize])

    data_start = pos + 19  # 19 bytes de trailer do header
    return data, data_start, entries


def decompress_cprs(raw, out_size):
    """Descomprime o formato LZSS usado nos PBOs (mime 'Cprs')."""
    out = bytearray()
    i = 0
    n = len(raw)

    while i < n and len(out) < out_size:
        ctl = raw[i]
        i += 1
        for bit in range(8):
            if i >= n or len(out) >= out_size:
                break
            if ctl & (1 << bit):
                out.append(raw[i])
                i += 1
            else:
                if i + 1 >= n:
                    i = n
                    break
                b1 = raw[i]
                b2 = raw[i + 1]
                i += 2
                off = ((b2 & 0xF0) << 4) | b1
                length = (b2 & 0x0F) + 2
                if off == 0:
                    i = n
                    break
                start = len(out) - off
                for k in range(length + 1):
                    if 0 <= start + k < len(out):
                        out.append(out[start + k])

    return bytes(out[:out_size])


def get_data(data, data_start, entries, idx):
    """Devolve os bytes (descomprimidos, se necessario) da entrada ``idx``."""
    entry = entries[idx]
    offset = data_start + sum(e[3] for e in entries[:idx])
    raw = data[offset:offset + entry[3]]

    if entry[1] == 0:
        return raw
    if entry[1] == CPRS and entry[2] and entry[2] < 80_000_000:
        return decompress_cprs(raw, entry[2])
    return raw


def main():
    """Uso: ``python pbo_scan.py <arquivo.pbo> [--extract <nome>]``."""
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        print("uso: python pbo_scan.py <arquivo.pbo>")
        raise SystemExit(1)

    path = sys.argv[1]
    data, data_start, entries = read_pbo(path)

    print("%s" % path)
    print("  %d entradas, dados a partir do byte %d" % (len(entries), data_start))
    print()
    print("  %-70s %-8s %12s" % ("nome", "mime", "tamanho"))
    for nome, mime, orig, dsize in entries:
        kind = "cru" if mime == 0 else ("cprs" if mime == CPRS else hex(mime))
        print("  %-70s %-8s %12d" % (nome, kind, dsize))


if __name__ == "__main__":
    main()
