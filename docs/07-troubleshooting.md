# 07 — Troubleshooting (erros reais deste pack)

Todos os problemas abaixo **aconteceram de verdade** enquanto este servidor era
montado. Cada um tem o sintoma exato do log, a causa e a correção.

> Regra de ouro: **sempre leia o RPT mais recente** antes de mexer em qualquer
> coisa. 90% dos problemas estão escritos lá.
>
> ```powershell
> $rpt = Get-ChildItem C:\DayZServer\profiles\*.RPT |
>        Sort-Object LastWriteTime | Select-Object -Last 1
> $rpt.FullName
> ```

---

## Índice

1. [Servidor não sobe: `UnlockServer` / `Can't compile "World"`](#1)
2. [Crash nativo (minidump) depois de repackar um PBO](#2)
3. [Crash ao carregar o save: `ChernarusMap`](#3)
4. [Servidor abre mas nenhum mod carrega](#4)
5. [`You were kicked off the game` / mods diferentes](#5)
6. [`Conflicting addon` do BuilderItems](#6)
7. [`[AVISO] Pastas listadas no MODS.txt mas ausentes`](#7)
8. [Cliente não encontra o servidor na LAN](#8)
9. [`World` carrega menos de 4.450 arquivos](#9)
10. [Avisos do Dynamic Scavenging (81 classnames)](#10)
11. [`SCRIPT (E)` que são inofensivos](#11)
12. [Servidor fecha sozinho durante o boot](#12)
13. [**Nenhuma ação funciona: porta, água, comida**](#13)

---

<a id="1"></a>
## 1. Servidor não sobe: `UnlockServer` / `Can't compile "World"`

### Sintoma

O console fecha ou fica parado e o `script_*.log` termina assim:

```text
BaseBuildingPlus/scripts/4_World/items/bbp_base.c(949):
    Undefined function 'CombinationLock.UnlockServer'
...
Can't compile "World" script module!
```

### Causa

A **DayZ 1.30 renomeou** o método:

```c
// 1.29
proto native void UnlockServer(EntityAI player, EntityAI parent);
// 1.30
proto native void UnlockOnServer(EntityAI player, EntityAI parent, bool isInsideLock = false);
```

O BaseBuildingPlus da Workshop ainda chama o nome antigo. O módulo inteiro de
`World` não compila e o servidor aborta.

### Correção

Aplique o patch incluído neste repositório:

```powershell
cd C:\dayz-modpack-solo\tools
python patch_bbp.py --src "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo"
Copy-Item "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus_patched.pbo" `
          "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo" -Force
```

Detalhes em [08-correcao-bbp.md](08-correcao-bbp.md).

### ⚠️ Não troque tudo

O log mostra 4 chamadas. **Duas delas não são do `CombinationLock`:**

| Arquivo | Objeto | Método correto |
|---|---|---|
| `BBP_BASE.c` | `combination_lock` (vanilla) | **`UnlockOnServer`** |
| `ActionDialCombinationLockOnTarget.c` | `combination_lock` (vanilla) | **`UnlockOnServer`** |
| `codelock.c` | `ExpansionCodeLock` | `UnlockServer` (continua existindo) |
| `codelock_exp.c` | `ExpansionCodeLock` | `UnlockServer` (continua existindo) |

Substituir as chamadas do `ExpansionCodeLock` **quebra o Expansion**. O script
do repositório só altera os 2 arquivos do `combination_lock` vanilla.

---

<a id="2"></a>
## 2. Crash nativo (minidump) depois de repackar um PBO

### Sintoma

O servidor **fecha em silêncio** logo depois de carregar o PBO alterado, gera
`crash_*.mdmp` e **não** escreve nenhum erro de script. No RPT a última linha é
o carregamento do addon.

### Causa

PBOs grandes do DayZ terminam com **22 bytes de integridade**:

```text
... dados das entradas ...
00                      <- byte de fechamento
00 + SHA1(conteudo)     <- 21 bytes
```

Ao reempacotar, se esse SHA-1 **não for recalculado**, o engine detecta a
inconsistência e morre nativamente — sem mensagem, sem `SCRIPT (E)`.

### Correção

1. Não repacke "na mão" com addon builder antigo.
2. Use `tools/patch_bbp.py`, que:
   - detecta o trailer (`raw[-21:] == b"\x00" + sha1(raw[:-21])`);
   - regrava os payloads;
   - **recalcula** o SHA-1 e reescreve `00 + 00 + sha1`.
3. Confira o resultado:

```powershell
Get-Item C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo | Select Length
# esperado: 320203069
```

O PBO gerado pelo script é **byte a byte idêntico** ao que está validado neste
pack (SHA-256 `18D991E7...974D`).

### Como reverter

```powershell
# o .orig é o backup feito antes do patch
Copy-Item "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo.orig" `
          "C:\DayZServer\@BaseBuildingPlus\addons\BaseBuildingPlus.pbo" -Force
```

Sem o patch o servidor não compila na 1.30 — reverter só faz sentido para
descobrir se o problema é do patch ou de outra coisa.

---

<a id="3"></a>
## 3. Crash ao carregar o save: `ChernarusMap`

### Sintoma

O servidor sobe, compila tudo, e morre ao carregar a persistência:

```text
Scripted variables corrupted upon "ChernarusMap"
  at .../init.c:6  main
```

### Causa

O `storage_1` (save do mundo) foi gravado com uma lista de mods diferente da
atual. Quando um objeto persistido referencia uma variável de script que não
existe mais (mod removido/trocado), o engine não consegue reconstruir o objeto
e aborta.

Gatilhos comuns:

- remover/desativar um mod que tinha objetos no mundo;
- trocar `@DayZ-Expansion-*` separados pelo `Bundle` (as classes mudam);
- save gravado durante um crash (arquivo `.bin` truncado).

### Correção

**Opção A — mundo novo (usado neste pack, à prova de bala):**

```powershell
Stop-Process -Name DayZServer_x64 -Force -ErrorAction SilentlyContinue
Rename-Item "C:\DayZServer\mpmissions\dayzOffline.chernarusplus\storage_1" `
            "storage_1_old"
```

O servidor recria o mundo no próximo boot (~9–13 min). Perde bases, veículos e
personagens.

**Opção B — tentar salvar o mundo:**

```powershell
# 1. storageAutoFix=1 no serverDZ.cfg (já está)
# 2. apague só os binários suspeitos, do mais novo para o mais antigo:
$s = "C:\DayZServer\mpmissions\dayzOffline.chernarusplus\storage_1"
Remove-Item "$s\data\*.bin" -Force
```

Se o crash persistir, só a opção A resolve.

> ⚠️ **Sempre** faça `storageAutoFix = 1` (padrão deste pack). Ele substitui
> arquivos corrompidos por vazios em vez de crashar — mas não conserta
> inconsistência de *classes*, só de formato.

---

<a id="4"></a>
## 4. Servidor abre mas nenhum mod carrega

### Sintoma

Boot rápido (menos de 1 min), mapa vanilla, sem HUD de mod, e no RPT:

```text
Module: World; loaded 1187x files     <- deveria ser 4450
```

### Causa

O `-mod=` não chegou ao processo. Isso acontece quando:

1. o servidor é iniciado por **`Start-Process`** do PowerShell sem array de
   argumentos (o `;` do `-mod=` é interpretado como separador de comando);
2. o caminho dos mods está entre aspas **dentro** da string;
3. o `START.bat` foi executado de outra pasta (usa `cd /d` — se falhar, procura
   `@*` no lugar errado).

### Correção

**Use o `START.bat`.** Ele monta a lista e passa tudo como **um único
argumento**:

```bat
start "DayZ Server" /min "DayZServer_x64.exe" ... "-mod=!clientMods!" ...
```

Se precisar lançar manualmente pelo PowerShell, passe os argumentos como
**array**:

```powershell
$mods = (Get-Content .\MODS.txt | Where-Object { $_ -and $_ -notmatch '^\s*#' }) -join ';'
Start-Process .\DayZServer_x64.exe -ArgumentList @(
  '-config=serverDZ.cfg','-port=2302','-profiles=profiles',"-mod=$mods",
  '-cpuCount=4','-exThreads=7','-maxMem=2047','-maxVRAM=2047',
  '-dologs','-adminlog','-freezecheck'
) -WorkingDirectory (Get-Location)
```

Confirme o que foi carregado:

```powershell
Select-String (Get-ChildItem .\profiles\*.RPT | Sort LastWriteTime | Select -Last 1) `
  -Pattern "Addon .* \(.*\)" | Measure-Object
```

Devem aparecer **~39 addons** `@...` no RPT.

---

<a id="5"></a>
## 5. `You were kicked off the game` / mods diferentes

### Sintoma

Conecta, aparece a tela de loading e volta com:

```text
You were kicked off the game.
```

ou "This server is using mods you don't have".

### Causa

Cliente e servidor com **conjuntos diferentes** de mods. `forceSameBuild=1` exige
a mesma build; `verifySignatures` controla assinatura.

### Correção

1. No cliente, ative **exatamente** os 39 mods de `config/MODS.txt`.
   A ordem **não** importa no cliente — o conjunto sim.
2. Os 2 mods sem assinatura (**JS Storage**, **Secret Trader**) exigem
   `verifySignatures = 0` no servidor (já configurado).
3. Se você mudou a lista no servidor, **feche o DayZ do cliente** e reabra com a
   lista nova (o launcher cacheia).

Diagnóstico:

```powershell
# mods que o servidor carregou
Select-String $rpt -Pattern "Addon @|Addon \\@" | ForEach-Object { $_.Line.Trim() }
```

Compare com o que o cliente mostra em **Launcher → Mods**.

---

<a id="6"></a>
## 6. `Conflicting addon` do BuilderItems

### Sintoma

```text
Conflicting addon BuilderItems_rocks_sakhal in 'DayZ-Expansion-Bundle\...'
previous definition in 'BuilderItems\rocks_sakhal\'
```

### Causa

O **Expansion Bundle já contém** o BuilderItems. Ao ativar também o
`@BuilderItems` separado (ou `@DayZ-Expansion-BaseBuilding` junto do Bundle),
as mesmas classes são registradas duas vezes.

### Correção

Não é crash — é conflito de registro. Mantenha **apenas**:

```text
@DayZ-Expansion-Bundle      <- ativo
@DayZ-Expansion-Core        <- comentado
@DayZ-Expansion-BaseBuilding<- comentado
@DayZ-Expansion-Market      <- comentado
@DayZ-Expansion-Vehicles    <- comentado
```

E **remova** `@BuilderItems` se ele for o mesmo pacote que já vem no Bundle.
Neste pack o `@BuilderItems` está ativo de propósito (versão independente) e o
aviso aparece — é esperado e inofensivo, porque o Bundle é carregado depois e
sobrescreve as classes.

> Se um dia virar erro (`SCRIPT (E)` por classe duplicada), comente
> `@BuilderItems` no `MODS.txt` e reinicie.

---

<a id="7"></a>
## 7. `[AVISO] Pastas listadas no MODS.txt mas ausentes`

### Sintoma

```text
[AVISO] Pastas listadas no MODS.txt mas ausentes no disco:
        @RaG_Vehicle_Pack @CookZ
```

### Causa

O nome da pasta não bate exatamente com a linha do `MODS.txt` (espaço, acento,
maiúscula) ou o mod não foi baixado.

### Correção

```powershell
# veja os nomes reais
Get-ChildItem C:\DayZServer -Directory -Filter '@*' | Select-Object -Expand Name |
  Sort-Object
```

Compare **caractere por caractere** com `MODS.txt`. Exemplos que já deram
problema:

| No `MODS.txt` | Errado |
|---|---|
| `@SF Zombie Horde Event` | `@SF_Zombie_Horde_Event` |
| `@MMG - Mightys Military Gear` | `@MMG-MightysMilitaryGear` |
| `@Secret Trader. Chernarus map. mapping` | `@SecretTrader` |
| `@Auto Stack - Proper` | `@AutoStack-Proper` |

> O aviso **não** impede o boot: o mod ausente é simplesmente ignorado. Mas o
> cliente com esse mod ativo vai ser expulso — corrija antes de jogar.

---

<a id="8"></a>
## 8. Cliente não encontra o servidor na LAN

### Sintoma

O servidor está rodando (RPT atualizando) mas a aba **LAN** está vazia.

### Causa e correção, em ordem

| Verificar | Comando / ação |
|---|---|
| Servidor realmente escutando | `netstat -ano \| findstr :2302` |
| Firewall | libere `DayZServer_x64.exe` (UDP 2302) |
| Porta diferente | o `START.bat` usa `-port=2302`; o cliente precisa `-port=2302` |
| Máquina diferente | use o IP local (`ipconfig`), aba **Direct Connect** |
| Steam rodando como admin e o jogo não | execute os dois no mesmo nível |

Teste de conexão direta no cliente:

```text
-connect=127.0.0.1 -port=2302
```

Se isso funciona e a LAN não, é firewall/descoberta — a conexão direta resolve.

---

<a id="9"></a>
## 9. `World` carrega menos de 4.450 arquivos

### Sintoma

```text
Module: World; loaded 4123x files    <- faltam ~330
```

Nenhum erro visível, mas alguma feature não aparece (arma sem textura, HUD
sumido, chefe sem baú).

### Causa

Um mod falhou ao carregar e o engine **pulou** os scripts dele sem abortar (PBO
corrompido, `.bisign` inválido com `verifySignatures=1`, dependência faltando).

### Correção

1. Compare a lista de addons carregados com o `MODS.txt`:

```powershell
$rpt = Get-ChildItem .\profiles\*.RPT | Sort LastWriteTime | Select -Last 1
Select-String $rpt -Pattern "Addon" | ForEach-Object { $_.Line.Trim() }
```

2. Procure por `Cannot open` / `Wrong signature` / `Addon ... not found`:

```powershell
Select-String $rpt -Pattern "Cannot open|Wrong signature|not found|Cannot load"
```

3. Revalide os arquivos do mod na Steam:
   **Biblioteca → DayZ → Engrenagem → Propriedades → Arquivos instalados →
   Verificar integridade**. Depois recopie a pasta `@Mod`.

> Referência de um boot saudável: `Game` 1267, `World` **4450**, `Mission` 788,
> **0** `SCRIPT (E)`.

---

<a id="10"></a>
## 10. Avisos do Dynamic Scavenging (81 classnames)

### Sintoma

```text
[DynamicScavenging] CONFIG WARNING: jackpotItems references unknown item classname "Deagle_Gold"
[DynamicScavenging] Loot data validation found 81 unknown classname(s)
```

### Causa

O config do mod cita itens que **não existem** neste pack (`Deagle_Gold`, `M14`,
`Scout`, `Mag_Aug_30Rnd`, ...). Ele valida a lista no boot e avisa.

### Correção

**Não é preciso fazer nada.** Os itens simplesmente não aparecem. Se quiser o log
limpo, edite o arquivo de config do mod e remova as linhas com `unknown` — mas
lembre que é um arquivo do mod, então guarde o original.

---

<a id="11"></a>
## 11. `SCRIPT (E)` que são inofensivos

Nem todo `SCRIPT (E)` impede o jogo. Os conhecidos deste pack:

| Erro | Origem | Impacto |
|---|---|---|
| `FIX-ME: Unexpected statement 'ref'` | Dynamic AI Missions (`3_Game`) | nenhum — sintaxe antiga |
| `Undefined variable 'm_...'` em `MissionGameplay` | mods de HUD antigos | nenhum em servidor dedicado |
| `Cannot find texture ...` | asset ausente de mod | textura rosa em 1 item |

O que **realmente** importa é:

```powershell
Select-String $rpt -Pattern "Can't compile|SCRIPT \(E\): .*Undefined function" 
```

Se aparecer `Can't compile`, o módulo inteiro caiu (ver item 1).

---

<a id="12"></a>
## 12. Servidor fecha sozinho durante o boot

### Sintoma

O processo desaparece entre 1 e 10 minutos de boot, sem erro de script.

### Causas, em ordem de frequência

| Causa | Como confirmar | Correção |
|---|---|---|
| **PBO repackado sem SHA-1** | você alterou algum `.pbo` | ver item 2 |
| RAM esgotada | Gerenciador de Tarefas > 90% | feche o cliente, aumente pagefile |
| `-freezecheck` matando | `error_*.log` com timeout | veja o log; se for boot lento, remova o `-freezecheck` |
| Antivírus bloqueando o `.exe` | log do Defender | exclusão para `C:\DayZServer` |
| OneDrive sincronizando PBO | pasta dentro do OneDrive | mova para `C:\DayZServer` |
| `storage_1` travado | último log é de persistência | ver item 3 |

---

<a id="13"></a>
## 13. Nenhuma ação funciona: porta, água, comida

### Sintoma

O personagem **anda, corre, olha** — mas:

- não abre porta de casa (nem aparece a opção);
- não bebe água no poço;
- não come nada do inventário;
- nada acontece ao segurar **F** perto de qualquer objeto.

Nenhum erro de script no log. É o sintoma mais confuso do DayZ e **quase
sempre é a mesma causa**.

### Causa

**O cliente está rodando sem os mods** (vanilla) e o servidor com os 39.
O `PlayerBase` dos dois lados fica diferente, então:

- **movimento** funciona → é previsto pelo cliente;
- **ações** falham → dependem de confirmação do servidor, que responde num
  protocolo que o cliente vanilla não conhece.

### Confirmação (10 segundos)

```powershell
$d = "$env:LOCALAPPDATA\DayZ"
$log = Get-ChildItem "$d\script_*.log" | Sort LastWriteTime | Select -Last 1
Select-String $log.FullName -Pattern "Module: "
```

| Resultado | Significado |
|---|---|
| `Game 1267 / World 4450 / Mission 788` | cliente **com** os mods ✅ |
| `Game 440 / World 2322 / Mission 219` | cliente **vanilla** ❌ — é isso |

No `defines:` do mesmo log, um cliente modado lista os nomes dos mods
(`Expansion`, `BBP_keybind`, `BasicMapDefine`, ...). O vanilla lista só
`DAYZ_1_30,PLATFORM_WINDOWS,RELEASE,sakhal,nasdara,DayZ,...`.

### Correção

Use o **`PLAY.bat`** (está em `config/`). Ele monta o `-mod=` com o caminho
absoluto dos 39 mods e conecta:

```text
Duplo clique em PLAY.bat
```

Não basta colocar `-connect=127.0.0.1` nas opções de inicialização da Steam —
isso conecta **sem mods** e produz exatamente esse bug.

### Se estiver usando o PLAY.bat e continuar igual

1. Confira se algum mod está sem a pasta `addons` (o script avisa `[AVISO]`).
2. Veja no log do cliente se aparece `Could not load module` ou `Addon`.

---

## Comandos de diagnóstico (cheat sheet)

```powershell
$srv = "C:\DayZServer"
$rpt = Get-ChildItem "$srv\profiles\*.RPT" | Sort-Object LastWriteTime | Select-Object -Last 1

# 1. versão e módulos
Select-String $rpt -Pattern "Version |Module: "

# 2. erros de compilação
Select-String $rpt -Pattern "Can't compile|SCRIPT \(E\)"

# 3. addons carregados
(Select-String $rpt -Pattern "^Addon ").Count

# 4. eventos e mods ativos
Select-String $rpt -Pattern "ZombieHorde|AI Missions|MI Raid Boss|DynEvent"

# 5. processos
Get-Process DayZServer_x64 -ErrorAction SilentlyContinue |
  Select-Object Id, @{n='RAM_GB';e={[math]::Round($_.WorkingSet64/1GB,2)}}

# 6. parar tudo
Stop-Process -Name DayZServer_x64 -Force -ErrorAction SilentlyContinue
```

---

## Ainda não resolveu?

1. Guarde o `RPT`, o `script_*.log` e o `error_*.log` da sessão.
2. Desative **metade** dos mods no `MODS.txt` (comentando linhas) e teste.
   Se subir, o problema está na metade desativada — repita até isolar 1 mod.
3. Nunca apague pastas de mods: só comente linhas. Assim você consegue reverter
   sem baixar 15 GB de novo.
