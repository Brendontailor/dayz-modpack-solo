#!/usr/bin/env python3
"""Corrige o BaseBuildingPlus para o DayZ 1.30.

Problema
--------
A 1.30 renomeou ``CombinationLock.UnlockServer(...)`` para
``UnlockOnServer(EntityAI player, EntityAI parent, bool isInsideLock = false)``.
O BBP chama o nome antigo em 4 pontos e o modulo ``World`` nao compila:

    BaseBuildingPlus/scripts/4_World/items/bbp_base.c(949):
        Undefined function 'CombinationLock.UnlockServer'
    -> Can't compile "World" script module!

O que este script faz
---------------------
Reescreve o PBO alterando **somente** os 2 arquivos com chamadas em
``combination_lock`` (as chamadas em ``codelock`` / ``codelock_exp`` usam
``ExpansionCodeLock``, que ainda tem ``UnlockServer`` e nao devem mudar).

Preserva:
  * ``config.bin`` e todas as outras 856 entradas (byte a byte);
  * prefixo ``BaseBuildingPlus`` e propriedades do PBO;
  * o trailer de integridade de 22 bytes do fim do arquivo.

ATENCAO: PBOs do DayZ podem terminar com ``0x00 0x00 + SHA1(conteudo)``.
Se o PBO for reempacotado sem recalcular esse SHA1, o engine **crasha
nativamente** (minidump) sem mensagem de script. Este script recalcula.

Uso
---
    python patch_bbp.py --src "C:\\...\\@BaseBuildingPlus\\addons\\BaseBuildingPlus.pbo"

Gera ``BaseBuildingPlus_patched.pbo`` ao lado do original (use ``--out`` para
escolher outro caminho). O original nunca e sobrescrito.
"""

import argparse
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pbo_scan import decompress_cprs, CPRS  # noqa: E402

REPLACEMENTS = [
    ("combination_lock.UnlockServer(", "combination_lock.UnlockOnServer("),
]

TARGET_SUFFIXES = (
    "bbp_base.c",
    "actiondialcombinationlockontarget.c",
)


def parse_header(raw):
    """Devolve (props, entries, trailer19, data_start)."""
    pos = 5 + 16
    props = []
    while True:
        end = raw.index(b"\x00", pos)
        key = raw[pos:end]
        pos = end + 1
        if not key:
            break
        end = raw.index(b"\x00", pos)
        val = raw[pos:end]
        pos = end + 1
        props.append((key, val))

    entries = []
    while True:
        end = raw.index(b"\x00", pos)
        name = raw[pos:end]
        pos = end + 1
        if not name:
            break
        mime, orig, _off, ts, dsize = struct.unpack("<IIIII", raw[pos:pos + 20])
        pos += 20
        entries.append([name, mime, orig, ts, dsize])

    trailer = raw[pos:pos + 19]
    return props, entries, trailer, pos + 19


def build(src, out):
    raw = open(src, "rb").read()
    props, entries, trailer, data_start = parse_header(raw)

    has_hash = raw[-21:] == b"\x00" + hashlib.sha1(raw[:-21]).digest()
    if has_hash:
        # sanity: 0x00 0x00 + sha1 no fim
        assert len(raw) - data_start - sum(e[4] for e in entries) == 22

    payloads = {}
    pos = data_start
    for i, e in enumerate(entries):
        payloads[i] = raw[pos:pos + e[4]]
        pos += e[4]

    patched = {}
    for i, e in enumerate(entries):
        name = e[0].decode("latin-1").replace("\\", "/").lower()
        if not name.endswith(TARGET_SUFFIXES):
            continue

        content = payloads[i]
        if e[1] == CPRS and e[2]:
            content = decompress_cprs(content, e[2])

        text = content.decode("latin-1")
        hits = 0
        for old, new in REPLACEMENTS:
            hits += text.count(old)
            text = text.replace(old, new)

        if hits == 0:
            raise SystemExit("nenhuma chamada encontrada em %s" % e[0])

        new_bytes = text.encode("latin-1")
        print("  %-70s %2d chamada(s)  %d -> %d bytes"
              % (e[0].decode("latin-1"), hits, len(content), len(new_bytes)))
        patched[i] = new_bytes

    if not patched:
        raise SystemExit("os arquivos alvo nao existem neste PBO; nada a fazer.")

    header = b"\x00sreV" + b"\x00" * 16
    for k, v in props:
        header += k + b"\x00" + v + b"\x00"
    header += b"\x00"
    for i, (name, mime, orig, ts, dsize) in enumerate(entries):
        if i in patched:
            header += name + b"\x00" + struct.pack("<IIIII", 0, 0, 0, ts, len(patched[i]))
        else:
            header += name + b"\x00" + struct.pack("<IIIII", mime, orig, 0, ts, dsize)
    header += b"\x00" + trailer

    body = bytearray()
    for i, e in enumerate(entries):
        body += patched.get(i, payloads[i])

    result = header + bytes(body)
    if has_hash:
        result += b"\x00"
        result += b"\x00" + hashlib.sha1(result).digest()

    with open(out, "wb") as f:
        f.write(result)

    # ------- validacao -------
    raw2 = open(out, "rb").read()
    props2, entries2, trailer2, ds2 = parse_header(raw2)
    assert [e[0] for e in entries2] == [e[0] for e in entries], "lista de entradas mudou"
    assert len(entries2) == len(entries)

    payloads2 = {}
    pos = ds2
    for i, e in enumerate(entries2):
        payloads2[i] = raw2[pos:pos + e[4]]
        pos += e[4]

    changed = [i for i in payloads2 if payloads2[i] != payloads[i]]
    assert sorted(changed) == sorted(patched), "entradas alteradas inesperadas"
    if has_hash:
        assert raw2[-20:] == hashlib.sha1(raw2[:-21]).digest(), "SHA1 invalido"

    print("\nOK: %d entradas, %d alteradas" % (len(entries2), len(changed)))
    print("    %s (%d bytes)  ->  %s (%d bytes)"
          % (src, len(raw), out, len(result)))


def main():
    ap = argparse.ArgumentParser(description="Corrige CombinationLock.UnlockServer no BaseBuildingPlus.")
    ap.add_argument("--src", required=True, help="caminho do BaseBuildingPlus.pbo original")
    ap.add_argument("--out", help="arquivo de saida (padrao: *_patched.pbo)")
    args = ap.parse_args()

    if not os.path.isfile(args.src):
        raise SystemExit("arquivo nao encontrado: %s" % args.src)

    out = args.out or os.path.splitext(args.src)[0] + "_patched.pbo"
    build(args.src, out)


if __name__ == "__main__":
    main()
