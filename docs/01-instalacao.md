# 01 — Tutorial de instalação (passo a passo)

Guia completo para montar este servidor do zero no Windows. Leva cerca de
**1 hora** (a maior parte é o download dos mods).

```text
┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐
│ DayZ Server │ → │ 39 mods      │ → │ configs deste │ → │ patch do BBP │ → START.bat
│ (Steam)     │   │ (Workshop)   │   │ repositório   │   │ (1.30)       │
└─────────────┘   └──────────────┘   └───────────────┘   └──────────────┘
```

---

## 1. Requisitos

| Item | Mínimo | Recomendado |
|---|---|---|
| Sistema | Windows 10 64-bit | Windows 11 64-bit |
| RAM | 8 GB | **16 GB** (pico medido ~4,3 GB) |
| Disco | 25 GB livres | SSD |
| CPU | 4 núcleos | 6+ núcleos |
| Python | 3.8+ (só para o patch) | 3.10+ |

> O **cliente** DayZ precisa dos **mesmos 39 mods**. Rodar servidor + cliente na
> mesma máquina funciona, mas consuma 16 GB de RAM para cima.

---

## 2. Baixar o DayZ Server

### Opção A — Steam (mais fácil)

1. Abra a Steam → **Biblioteca** → filtro **Ferramentas**.
2. Instale **DayZ Server** (gratuito).
3. Anote a pasta, por exemplo `C:\DayZServer`.

### Opção B — SteamCMD

```powershell
steamcmd +force_install_dir C:\DayZServer +login anonymous +app_update 223350 validate +quit
```

Confirme a versão: dentro de `profiles\DayZServer_x64_*.RPT` deve aparecer
`Version 1.30.xxxxx`.

---

## 3. Baixar os 39 mods

Os mods são itens da **Steam Workshop** (app `221100`). Não há como baixá-los
por este repositório — assine cada um na Steam e copie a pasta.

### 3.1 Assinar na Steam

1. Abra a página de cada mod na Workshop e clique em **Inscrever-se**.
2. A Steam baixa para:
   `C:\Program Files (x86)\Steam\steamapps\workshop\content\221100\<ID>`
3. Espere o download terminar (o ícone da Steam para de girar).

### 3.2 Copiar para o servidor

Cada pasta baixada deve ser copiada para a raiz do servidor com o **nome exato**
usado em `config/MODS.txt` (com espaços e maiúsculas), prefixado por `@`:

```text
C:\DayZServer\
├─ @CF\
│  ├─ addons\...
│  └─ keys\...
├─ @Dabs Framework\
├─ @DayZ-Expansion-Bundle\
├─ @BaseBuildingPlus\
└─ ... (39 pastas)
```

Regras importantes:

- **O nome da pasta é a ordem de carga.** `@BaseBuildingPlus` ≠ `@Basebuildingplus`.
- Cada mod precisa ter uma subpasta `addons` com os `.pbo`.
- Se o mod tiver `keys\*.bikey`, copie para `C:\DayZServer\keys\`
  (obrigatório só com `verifySignatures=2`).
- **Nunca apague** a pasta de um mod para "desativar": comente a linha no
  `MODS.txt`.

### 3.3 Lista dos 39 mods

A lista e a explicação de cada um estão em **[02-mods.md](02-mods.md)**.

---

## 4. Copiar as configurações

Copie o conteúdo de `config/` deste repositório para a raiz do servidor:

| Origem (repositório) | Destino (servidor) |
|---|---|
| `config/MODS.txt` | `C:\DayZServer\MODS.txt` |
| `config/START.bat` | `C:\DayZServer\START.bat` |
| `config/PLAY.bat` | `C:\DayZServer\PLAY.bat` |
| `config/serverDZ.cfg` | `C:\DayZServer\serverDZ.cfg` |
| `config/db/types.xml` | `C:\DayZServer\mpmissions\dayzOffline.chernarusplus\db\types.xml` |
| `config/db/globals.xml` | `C:\DayZServer\mpmissions\dayzOffline.chernarusplus\db\globals.xml` |
| `config/profiles/MI_RaidBoss/` | `C:\DayZServer\profiles\MI_RaidBoss\` |
| `config/profiles/BasicMap/` | `C:\DayZServer\profiles\BasicMap\` |
| `config/profiles/AIMissions/` | `C:\DayZServer\profiles\AIMissions\` |
| `config/profiles/ZombieHorde/` | `C:\DayZServer\profiles\ZombieHorde\` |

Em PowerShell:

```powershell
$server = "C:\DayZServer"
$repo   = "C:\dayz-modpack-solo"

Copy-Item "$repo\config\MODS.txt"      "$server\" -Force
Copy-Item "$repo\config\START.bat"     "$server\" -Force
Copy-Item "$repo\config\serverDZ.cfg"  "$server\" -Force

$mission = "$server\mpmissions\dayzOffline.chernarusplus"
Copy-Item "$repo\config\db\types.xml"   "$mission\db\" -Force
Copy-Item "$repo\config\db\globals.xml" "$mission\db\" -Force

New-Item -ItemType Directory "$server\profiles" -Force | Out-Null
Copy-Item "$repo\config\profiles\*" "$server\profiles\" -Recurse -Force
```

> As pastas em `profiles\` são **criadas pelos mods no primeiro boot**. Copiar
> antes só antecipa as suas configurações; se o mod não encontrar o arquivo, ele
> gera o padrão.

---

## 5. Ajustar o `serverDZ.cfg`

Campos que você provavelmente vai querer mudar:

```ini
hostname = "Apocalipse";      // nome na lista de servidores
password = "";                // senha para entrar (vazio = aberto)
passwordAdmin = "";           // senha de admin (para o VPP)
maxPlayers = 1;               // solo: 1 | amigos: 2-8
verifySignatures = 0;         // 0 = aceita mods sem .bisign (JS Storage, Secret Trader)
forceSameBuild = 1;           // cliente e servidor na mesma versão
thirdPersonView = 1;          // 0 = só 1ª pessoa
serverTimeAcceleration = 12;  // dia mais rápido
serverNightTimeAcceleration = 4;
storageAutoFix = 1;           // corrige persistência corrompida automaticamente
instanceId = 1;               // troque se rodar mais de um servidor na mesma máquina
```

> ⚠️ `verifySignatures=0` é necessário porque **JS Storage** e **Secret Trader**
> não têm `.bisign`. Se um dia abrir o servidor ao público, volte para `2` e
> remova esses dois mods (ou peça os `.bikey` aos autores).

A porta **não** fica no `.cfg`: ela é passada na linha de comando
(`START.bat` usa `-port=2302`).

---

## 6. Corrigir o BaseBuildingPlus (obrigatório na 1.30)

O BBP que está na Workshop usa uma função que a **DayZ 1.30 renomeou**
(`CombinationLock.UnlockServer` → `UnlockOnServer`). Sem o patch o servidor
**não sobe** (`Can't compile "World" script module!`).

```powershell
# 1) backup do PBO original
Copy-Item "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo" `
          "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo.orig" -Force

# 2) gerar o PBO corrigido (Python 3)
cd C:\dayz-modpack-solo\tools
python patch_bbp.py --src "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo"

# 3) instalar (sobrescreve o PBO; o .orig fica de backup)
Copy-Item "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus_patched.pbo" `
          "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo" -Force
```

Saída esperada:

```text
  scripts\4_World\actions\vanilla\ActionDialCombinationLockOnTarget.c   2 chamada(s)  1800 -> 1804 bytes
  scripts\4_World\items\BBP_BASE.c                                      2 chamada(s)  25307 -> 25311 bytes

OK: 858 entradas, 2 alteradas
```

O PBO corrigido tem **320.203.069 bytes** (o original, 320.203.061). Detalhes
técnicos e como reverter em **[08-correcao-bbp.md](08-correcao-bbp.md)**.

> Se você usa **DayZ Tools**, pode recompilar o mod a partir do fonte. O patch
> do PBO é o caminho sem dependências.

---

## 7. Primeiro boot

```text
Duplo clique em START.bat
```

O `START.bat` lê o `MODS.txt`, avisa se faltar alguma pasta e inicia o servidor
minimizado. Ele também reinicia o servidor a cada 12 h (útil para servidor
dedicado).

> O script usa **a própria pasta** como raiz (`%~dp0`) — não há caminho fixo
> para editar. Basta colocar o `START.bat` na raiz do servidor, ao lado do
> `DayZServer_x64.exe`.

### Linha do tempo esperada (máquina de teste)

| Fase | Tempo | RAM |
|---|---|---|
| Carregar PBOs (655+) | ~1 min | ~1 GB |
| Compilar `Game` (1.267 arquivos) | ~4 s | ~1,2 GB |
| Compilar `World` (4.450 arquivos) | ~30 s | ~1,5 GB |
| Compilar `Mission` (788 arquivos) | ~2 min | ~2 GB |
| Montar mundo + loot + zumbis | 4–10 min | ~4,3 GB |
| **Pronto para conectar** | **~10–13 min (1º boot)** | ~4,3 GB |

No segundo boot (save já gerado) cai para **4–6 min**.

### Como saber se compilou tudo

```powershell
$rpt = Get-ChildItem C:\DayZServer\profiles\*.RPT | Sort-Object LastWriteTime | Select-Object -Last 1
Select-String $rpt.FullName -Pattern "Module: "
```

Esperado:

```text
Module: GameLib;  loaded   43x files
Module: Game;     loaded 1267x files
Module: World;    loaded 4450x files
Module: Mission;  loaded  788x files
```

E **nenhuma** linha `SCRIPT (E):` ou `Can't compile`.

---

## 8. Conectar o cliente

**Use o `PLAY.bat`.** Ele lê o `MODS.txt`, monta o `-mod=` com o caminho
absoluto de cada mod do servidor e conecta em `127.0.0.1:2302`:

```text
Duplo clique em PLAY.bat
```

> ⚠️ **Não abra o DayZ pela Steam** (nem só com `-connect=` nas opções de
> inicialização). Sem `-mod=`, o cliente carrega o jogo **vanilla** e acontece
> o pior sintoma possível: você **anda**, mas **nenhuma ação funciona** — não
> abre porta, não bebe água, não come. É a causa nº 1 de "servidor bugado".

Se o cliente estiver em **outra máquina**, edite no `PLAY.bat`:

```bat
set "serverIp=192.168.8.7"
set "dayzExe=C:\Program Files (x86)\Steam\steamapps\common\DayZ\DayZ_x64.exe"
```

e copie as 39 pastas `@...` para essa máquina (ou use caminho de rede).

### Como saber se o cliente carregou os mods

No `script_*.log` do cliente
(`%LOCALAPPDATA%\DayZ\script_<data>.log`) deve aparecer:

```text
Module: Game;    loaded 1267x files; 3647x classes
Module: World;   loaded 4450x files; 11196x classes
Module: Mission; loaded  788x files; 1751x classes
```

Se aparecer **440 / 2322 / 219**, o cliente está vanilla — feche e use o
`PLAY.bat`. A ordem no cliente não importa; o **conjunto** precisa ser igual.

### Sem o PLAY.bat

Se preferir o DayZ Launcher: ative os 39 mods na aba *Mods*, inicie o jogo e
use **Direct Connect** → `127.0.0.1:2302`. O importante é que o cliente suba
com os mods.

O primeiro login pode demorar ~1 min (o servidor gera o personagem).

> Se o cliente estiver em outra máquina, libere a porta **2302/UDP** no firewall
> e use o IP da máquina do servidor.

---

## 9. Checklist final

- [ ] `DayZServer_x64.exe` é 1.30
- [ ] 39 pastas `@...` na raiz, com `addons\` dentro
- [ ] `MODS.txt` copiado e sem mods faltando (`START.bat` não mostra `[AVISO]`)
- [ ] `types.xml` e `globals.xml` na pasta `db` da missão
- [ ] `profiles\MI_RaidBoss`, `BasicMap`, `AIMissions`, `ZombieHorde` copiados
- [ ] `BaseBuildingPlus.pbo` = **320.203.069 bytes**
- [ ] RPT mostra `World` com **4.450** arquivos
- [ ] `0` erros `SCRIPT (E)`
- [ ] Porta `2302/UDP` aberta (se for jogar em rede)

Problemas? Veja **[07-troubleshooting.md](07-troubleshooting.md)**.
