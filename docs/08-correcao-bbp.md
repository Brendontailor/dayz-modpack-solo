# 08 — Correção do BaseBuildingPlus na DayZ 1.30

Documento técnico do patch aplicado em `@BaseBuildingPlus`. Se você só quer
fazer o servidor subir, siga o [tutorial de instalação](01-instalacao.md#6-corrigir-o-basebuildingplus-obrigatório-na-130)
e volte aqui apenas se algo der errado.

---

## 1. O problema

O BaseBuildingPlus (Workshop) chama um método que a DayZ **1.30 renomeou**:

```c
// DayZ 1.29
proto native void UnlockServer(EntityAI player, EntityAI parent);

// DayZ 1.30
proto native void UnlockOnServer(EntityAI player, EntityAI parent, bool isInsideLock = false);
```

Resultado no `script_*.log`:

```text
BaseBuildingPlus/scripts/4_World/items/bbp_base.c(949):
    Undefined function 'CombinationLock.UnlockServer'

Can't compile "World" script module!
```

Como o módulo `World` inteiro falha, **nenhum** mod que depende dele compila
(Expansion, RaG, BuilderItems...). O servidor não sobe.

### Detalhe que quase todo mundo erra

O erro aparece **4 vezes**, mas nem todas são do mesmo objeto:

| Arquivo | Chamada em | Objeto | Correto |
|---|---|---|---|
| `BBP_BASE.c` | linha ~949, ~1263 | `combination_lock` | `UnlockOnServer` |
| `ActionDialCombinationLockOnTarget.c` | 2 pontos | `combination_lock` | `UnlockOnServer` |
| `codelock.c` | — | `ExpansionCodeLock` | **`UnlockServer`** (não mexer) |
| `codelock_exp.c` | — | `ExpansionCodeLock` | **`UnlockServer`** (não mexer) |

Se você fizer um `replace all` no PBO inteiro, o `ExpansionCodeLock` perde o
método e o **Expansion para de funcionar** (o erro só aparece quando alguém usa
o cadeado, dias depois).

O patch deste repositório altera **apenas** os 2 arquivos do
`combination_lock` vanilla.

---

## 2. Por que não recompilar com DayZ Tools

Seria o caminho "oficial", mas:

1. exige instalar ~30 GB de DayZ Tools + **DayZ Samples** (`DZ\` e `Dta\`);
2. o .pbo da Workshop não vem com o projeto (`*.p3d`/`*.cfg`), só com o PBO
   compilado;
3. recompilar gera um PBO com **ordem de entradas e compressão diferentes** —
   funcional, mas não idêntico ao original, o que dificulta comparar/depurar.

Como a mudança é **só textual em 2 scripts**, patchear o PBO é mais rápido,
determinístico e reversível. Depois, se você tiver os fontes, pode recompilar.

---

## 3. Formato do PBO do DayZ

Um PBO (Enfusion) é assim:

```text
┌──────────────────────────────────────────────┐
│ "\0sreV"                     5 bytes         │  magic
│ 00 × 16                     16 bytes         │  reservado
│ propriedades                 key\0value\0... │  product / prefix / ...
│ 00                           terminator       │
│ entradas                     nome\0 + 20 B    │  mime, tamanho_original,
│                              ...              │  offset, timestamp, tamanho_dados
│ 00                           terminator       │
│ trailer do header            19 bytes         │  geralmente zeros
├──────────────────────────────────────────────┤
│ dados das entradas, na ordem do header       │
│ (mime 0 = cru | "Cprs" = LZSS comprimido)    │
├──────────────────────────────────────────────┤
│ 00                                            │  ← trailer de integridade
│ 00 + SHA1(256 primeiros... todos os bytes    │    (22 bytes no total)
│      anteriores a esses 21)                  │
└──────────────────────────────────────────────┘
```

Dois detalhes que quebram qualquer script de PBO:

### 3.1 O campo `offset` do header deve ser **0**

O DayZ calcula o offset **sequencialmente**:

```text
offset_entrada[i] = data_start + soma(tamanho_dados[0..i-1])
```

Se você gravar offsets "de verdade" no header, o engine soma de novo e lê lixo →
**crash nativo**. Por isso o patch grava `0` em todas as entradas (era `0` no
original também).

### 3.2 O SHA-1 do fim é obrigatório em PBOs grandes

O arquivo termina com:

```text
0x00 0x00 + SHA1(bytes[0 : len-21])
```

Se você regrava os dados e **não** recalcula, o engine detecta e gera
`crash_*.mdmp` **sem nenhuma mensagem de script**. Foi exatamente o que
aconteceu na primeira tentativa de patch deste pack.

---

## 4. O que o script faz

`tools/patch_bbp.py`:

```text
1. lê o PBO inteiro em memória
2. parse_header()  -> propriedades, 858 entradas, trailer de 19 bytes
3. confere se existe o trailer SHA1 no fim
4. para cada entrada cujo nome termina em:
       bbp_base.c
       actiondialcombinationlockontarget.c
   a. descomprime se mime == "Cprs"
   b. troca "combination_lock.UnlockServer(" -> "combination_lock.UnlockOnServer("
   c. aborta se não encontrou nenhuma ocorrência
5. reescreve o header com os novos tamanhos (offset = 0)
6. copia os payloads das outras 856 entradas byte a byte
7. recalcula 0x00 0x00 + SHA1 e anexa
8. valida: lista de nomes igual? só 2 entradas mudaram? SHA1 confere?
```

A troca é feita **com o prefixo do objeto** (`combination_lock.`), não só no
nome do método. É isso que impede o patch de tocar no `ExpansionCodeLock`.

### Antes e depois

```text
scripts\4_World\actions\vanilla\ActionDialCombinationLockOnTarget.c
    2 chamadas    1800 bytes  ->  1804 bytes

scripts\4_World\items\BBP_BASE.c
    2 chamadas   25307 bytes  -> 25311 bytes

858 entradas, 2 alteradas
320.203.061 bytes  ->  320.203.069 bytes   (+8)
```

Cada chamada cresce 2 bytes (`UnlockServer` → `UnlockOnServer`), 2 chamadas por
arquivo × 2 arquivos = **8 bytes**.

### Propriedades e prefixo preservados

O header mantém `product` e `prefix` originais (`BaseBuildingPlus`). Isso é
essencial: o `prefix` define o namespace virtual dos scripts
(`BaseBuildingPlus/scripts/...`). Mudar o prefixo faz o mod carregar em outro
caminho e as classes não serem encontradas.

O `config.bin` (que define as classes C++ do mod) também não é tocado — ele é
uma entrada como outra qualquer.

---

## 5. Como aplicar

```powershell
# 0) servidor parado
Stop-Process -Name DayZServer_x64 -Force -ErrorAction SilentlyContinue

$bbp = "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo"

# 1) backup
Copy-Item $bbp "$bbp.orig" -Force

# 2) gerar
cd C:\dayz-modpack-solo\tools
python patch_bbp.py --src $bbp --out "$bbp.patched"

# 3) validar tamanho
(Get-Item "$bbp.patched").Length      # 320203069

# 4) instalar
Copy-Item "$bbp.patched" $bbp -Force

# 5) subir
cd C:\DayZServer
.\START.bat
```

### Saída esperada

```text
  scripts\4_World\actions\vanilla\ActionDialCombinationLockOnTarget.c     2 chamada(s)  1800 -> 1804 bytes
  scripts\4_World\items\BBP_BASE.c                                        2 chamada(s)  25307 -> 25311 bytes

OK: 858 entradas, 2 alteradas
    ...\BaseBuildingPlus.pbo (320203061 bytes)  ->  ...\BaseBuildingPlus.pbo.patched (320203069 bytes)
```

O script **nunca** sobrescreve `--src`: se você não passar `--out`, ele gera
`BaseBuildingPlus_patched.pbo` ao lado.

---

## 6. Validação

### 6.1 Hash do PBO

O PBO gerado a partir do original da Workshop é **determinístico**:

| Arquivo | SHA-256 |
|---|---|
| original | (varia por versão da Workshop) |
| **corrigido** | `18D991E7AC54E17F92037C5ABA97679D4C3A2E3DC2F2B2468D245AAB7101974D` |

```powershell
(Get-FileHash C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo -Algorithm SHA256).Hash
```

Se o hash bater, o patch é idêntico ao validado neste pack. Se o original da
Workshop for atualizado, o hash muda — o que importa é o tamanho (+8 bytes) e a
ausência de erros no boot.

### 6.2 Boot

```text
Module: World; loaded 4450x files; 11196x classes
Module: Mission; loaded 788x files
```

E **zero** ocorrências de:

```powershell
Select-String $rpt -Pattern "UnlockServer|Can't compile"
```

`UnlockServer` pode aparecer em **outros** mods (Expansion) — o que não pode
aparecer é `Can't compile` ou o caminho `bbp_base.c`.

### 6.3 Em jogo

1. Construa uma cerca/porta do BBP.
2. Coloque um **Combination Lock** (cadeado numérico vanilla).
3. Digite a combinação, destrave e tranque de novo.
4. Abra a porta.

Se o cadeado funcionar, a chamada `UnlockOnServer(player, parent)` está correta.
Se o servidor crashar ao destravar, o patch ficou inconsistente — reverta.

---

## 7. Como reverter

```powershell
Stop-Process -Name DayZServer_x64 -Force -ErrorAction SilentlyContinue
Copy-Item "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo.orig" `
          "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo" -Force
```

Reverter devolve o crash de compilação na 1.30. Só faça isso para confirmar que
o problema é do patch (e não de outro mod).

---

## 8. Quando o patch não for mais necessário

Se o autor do BBP publicar uma versão compatível com 1.30:

1. **Desative o patch** — desinscreva/resubscribe o mod na Workshop (a Steam
   baixa o PBO novo).
2. Confira se o PBO novo tem `UnlockOnServer`:

```powershell
python -c "import sys; sys.path.insert(0,'.'); from pbo_scan import read_pbo,get_data; d,s,e=read_pbo(r'C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo'); print([x[0] for x in e if 'bbp_base' in x[0].lower()])"
```

3. Rode o boot e confirme `0` erros. Se compilar, **não** aplique o patch de
   novo (ele vai falhar com "nenhuma chamada encontrada" — o que é a resposta
   correta: o mod já está corrigido).

---

## 9. Arquivos envolvidos

```text
tools/
├─ patch_bbp.py    aplica a correção e recalcula o SHA-1
└─ pbo_scan.py     leitor/descompressor de PBO (sem DayZ Tools)
```

`pbo_scan.py` também serve para inspecionar qualquer PBO:

```powershell
python -c "from pbo_scan import read_pbo; d,s,e=read_pbo(r'C:\...\AlgumMod.pbo'); print(len(e),'entradas'); [print(x[0],x[3]) for x in e[:10]]"
```

---

## 10. Resumo

| Item | Valor |
|---|---|
| Mod afetado | `@BaseBuildingPlus` (Workshop) |
| Arquivos alterados | 2 de 858 |
| Chamadas trocadas | 4 (`combination_lock.UnlockServer` → `UnlockOnServer`) |
| Tamanho | 320.203.061 → **320.203.069** bytes |
| SHA-256 corrigido | `18D991E7...1974D` |
| Preservado | `config.bin`, prefixo, propriedades, 856 entradas, trailer SHA-1 recalculado |
| Reversível | sim (`*.pbo.orig`) |
| Validação em jogo | cadeado numérico do BBP tranca/destrava |
