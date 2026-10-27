# tools — utilitários

Dois scripts Python 3 (sem dependências externas, sem DayZ Tools).

```text
tools/
├─ patch_bbp.py   corrige o BaseBuildingPlus para a DayZ 1.30
└─ pbo_scan.py    leitor/descompressor de PBO (biblioteca usada pelo patch)
```

Requisitos: **Python 3.8+**. Nada de `pip install`.

---

## `patch_bbp.py`

Troca `combination_lock.UnlockServer(` por `combination_lock.UnlockOnServer(`
nos 2 arquivos do BaseBuildingPlus e **recalcula o SHA-1** de integridade do
PBO (sem isso o engine crasha nativamente).

```powershell
cd tools
python patch_bbp.py --src "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo"
```

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `--src` | sim | PBO original do BaseBuildingPlus |
| `--out` | não | saída (padrão: `<src>_patched.pbo`) |

O arquivo de origem **nunca** é sobrescrito.

Saída esperada:

```text
  scripts\4_World\actions\vanilla\ActionDialCombinationLockOnTarget.c     2 chamada(s)  1800 -> 1804 bytes
  scripts\4_World\items\BBP_BASE.c                                        2 chamada(s)  25307 -> 25311 bytes

OK: 858 entradas, 2 alteradas
```

Detalhes técnicos, validação e reversão: [docs/08-correcao-bbp.md](../docs/08-correcao-bbp.md).

---

## `pbo_scan.py`

Leitor de PBO do DayZ (formato `\0sreV`) com descompressão LZSS (`Cprs`).

```python
from pbo_scan import read_pbo, get_data

data, data_start, entries = read_pbo(r"C:\DayZServer\@CF\addons\cf.pbo")
print(len(entries), "entradas")

# listar as 10 primeiras
for nome, mime, tam_original, tam_dados in entries[:10]:
    print(f"{nome:<60} {mime=} {tam_dados}")

# extrair o conteúdo da entrada 0 (já descomprimido)
conteudo = get_data(data, data_start, entries, 0)
```

Também funciona como script:

```powershell
python pbo_scan.py "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo"
```

Formato do header (resumo):

```text
"\0sreV" + 16 zeros
propriedades: key\0value\0 ... \0
entradas:     nome\0 + <IIIII mime, tamanho_original, offset, timestamp, tamanho_dados>
terminador:   \0
trailer:      19 bytes
dados:        sequenciais, na ordem do header
fim:          0x00 0x00 + SHA1(bytes anteriores)   (PBOs grandes)
```

⚠️ O campo `offset` do header é sempre **0** no DayZ — o engine calcula os
offsets somando os tamanhos na ordem. Gravar offsets reais faz o engine ler
lixo e crashar.

---

## Aviso

Estes scripts **modificam** um PBO de terceiros. Eles:
- não redistribuem o mod;
- não tocam em `config.bin` nem no prefixo;
- alteram apenas as 2 entradas com o bug;
- geram um arquivo novo (não sobrescrevem o original).

Guarde sempre um backup (`*.pbo.orig`) antes de substituir o PBO no servidor.
