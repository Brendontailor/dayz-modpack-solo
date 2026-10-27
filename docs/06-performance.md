# 06 — Performance

O pack foi ajustado para rodar **servidor + cliente na mesma máquina**, com 39
mods, sem lag perceptível.

---

## Parâmetros do `START.bat`

```bat
DayZServer_x64.exe -config=serverDZ.cfg -port=2302 -profiles=profiles
    "-mod=!clientMods!" -cpuCount=4 -exThreads=7
    -maxMem=2047 -maxVRAM=2047 -dologs -adminlog -freezecheck
```

| Parâmetro | Valor | Por quê |
|---|---:|---|
| `-cpuCount` | **4** | Núcleos **físicos** usados pelo engine. Em CPU de 4c/8t mantenha 4 |
| `-exThreads` | **7** | Threads extras para tarefas paralelas |
| `-maxMem` | **2047** | Teto de heap do engine (MB). Acima disso o DayZ ignora |
| `-maxVRAM` | **2047** | Servidor é headless; o teto evita alocar VRAM |
| `-dologs` | — | Gera `.RPT`, `script_*.log`, `error_*.log` |
| `-adminlog` | — | Gera `.ADM` (entradas/saídas, mortes) |
| `-freezecheck` | — | Encerra se o servidor travar (evita processo zumbi) |

### Ajuste por hardware

| Máquina | `-cpuCount` | `-exThreads` | `ZombieMaxCount` | `AnimalMaxCount` |
|---|---:|---:|---:|---:|
| 4c/8t, 8 GB | 4 | 5 | 300 | 60 |
| 6c/12t, 16 GB | 6 | 7 | 400 | 80 |
| 8c/16t, 16 GB (servidor + cliente) | **4** | **7** | **450** | **80** |
| 8c/16t, 16 GB+ (só servidor) | 6 | 7 | 700 | 140 |

> `-cpuCount` maior que o número de núcleos **físicos** piora (contenção).
> Em CPU com *hyper-threading*, use o número de núcleos reais.

---

## Números medidos (máquina de teste)

Máquina: 8 núcleos / 16 threads, 15 GB RAM, SSD, Windows 11.

| Fase | Tempo | RAM |
|---|---|---:|
| Carregar 655+ PBOs | ~60 s | ~1,0 GB |
| Compilar `GameLib` (43 arquivos) | <1 s | — |
| Compilar `Game` (1.267 arquivos) | ~4 s | ~1,2 GB |
| Compilar `World` (4.450 arquivos) | ~30 s | ~1,5 GB |
| Compilar `Mission` (788 arquivos) | ~2 min | ~2,0 GB |
| Montar mundo + loot + zumbis | 4–10 min | **~4,3 GB** |
| Boot completo (1º, mundo novo) | **~13 min** | 4,3 GB |
| Boot completo (save existente) | **4–6 min** | 4,3 GB |

Referência de compilação (se `World` carregar menos que isso, algum mod não
carregou):

```text
Module: Game;    loaded 1267x files; 3647x classes
Module: World;   loaded 4450x files; 11196x classes
Module: Mission; loaded  788x files; 1751x classes
```

---

## O que mais custa performance

| Fator | Impacto | Como reduzir |
|---|---|---|
| Nº de mods | Alto (boot e RAM) | desative linhas no `MODS.txt` |
| Zumbis vivos | Alto (IA + física) | `ZombieMaxCount` no `globals.xml` |
| Itens no chão | Alto | `CleanupLifetimeDefault: 20` |
| Hordas | Médio (picos) | `ZombiesPerWave`, `MaxAliveEventZombies` |
| Missões IA | Médio | `Missions_Max_Concurrent: 1` |
| Chefes on-demand | Baixo | já otimizado (`spawnOnServerStart: false`) |
| 3ª pessoa em veículo | Baixo | `@Vehicle3PP` |
| **RAM livre < 1 GB** | **Crítico** | ver seção abaixo |

---

## RAM: o gargalo que faz as ações pararem

Medição real nesta máquina (Ryzen 7 7735HS, 8c/16t, **15,3 GB**):

| Estado | RAM em uso | Efeito em jogo |
|---|---:|---|
| Cliente vanilla + servidor + OneDrive + Steam | **98%** (0,2 GB livres) | ações cancelam, tudo trava |
| Depois de fechar OneDrive/Steam/aba do Task Manager | 66% (5,1 GB livres) | normal |

Com o Windows paginando para o disco, o cliente **anda** (movimento é previsto
localmente) mas **as ações falham**: abrir porta, beber água e comer dependem de
confirmação do servidor e são canceladas por timeout antes da resposta chegar.

### Regras práticas

1. **Deixe pelo menos 3 GB livres** antes de abrir o cliente com 39 mods
   (servidor ~2 GB + cliente com mods ~5 GB).
2. **Feche o OneDrive durante o jogo** — ele sincroniza a pasta do servidor
   (15 GB de PBOs) e consome I/O além de RAM.
3. **Não deixe o servidor dentro do OneDrive.** Mova para `C:\DayZServer`.
4. Feche abas/janelas do Steam (cada `steamwebhelper` chega a ~500 MB).
5. Confira antes de jogar:

```powershell
$os = Get-CimInstance Win32_OperatingSystem
"livre: {0:N1} GB" -f ($os.FreePhysicalMemory/1MB)
```

Se estiver abaixo de 3 GB, feche programas antes de conectar.

---

## Dicas que fazem diferença

### 1. Não rode o servidor dentro do OneDrive

Pastas sincronizadas (OneDrive/Dropbox/Google Drive) causam:

- leitura lenta de PBOs grandes (o BBP tem **320 MB**);
- travamentos quando o sync bloqueia o arquivo durante o boot;
- risco de o sync substituir um `.pbo` no meio da leitura.

Mova o servidor para algo como `C:\DayZServer` e deixe o **repositório de
configs** no OneDrive/Git.

### 2. Exclua o servidor do antivírus

Windows Defender varrendo 15 GB de PBOs a cada boot dobra o tempo de carga.
Adicione exclusão para:

```text
C:\DayZServer
```

### 3. Pagefile

Com 39 mods o pico é ~4,3 GB, mas o *commit* chega perto de 8 GB. Deixe o
pagefile gerenciado pelo Windows (ou 8 GB fixos em SSD).

### 4. Feche o cliente DayZ durante o boot

O servidor compila ~6.500 arquivos de script nos primeiros minutos. Rodar o
cliente junto atrasa o boot em 30–50%.

### 5. Reinício programado

O `START.bat` reinicia o servidor a cada **12 h** (`restartSeconds=43200`).
Reinício diário limpa memória fragmentada pelo CE e evita queda de FPS em
sessões longas. Para desligar, comente o `timeout`.

---

## Diagnóstico rápido de lag

| Sintoma | Verificar |
|---|---|
| Lag ao entrar | `Module: World` compilando? (normal no 1º boot) |
| Lag constante | `ZombieMaxCount` alto + hordas simultâneas |
| Lag só perto de base | muitos itens no chão — reduza `CleanupLifetimeDefault` |
| Travadas de 1–2 s | sync do OneDrive ou antivírus lendo PBO |
| FPS baixo no cliente | 39 mods + 2 mapas (BasicMap/MiniMap) — MiniMap já está off |
| Servidor morre sozinho | `-freezecheck` atuando: veja `error_*.log` |

---

## Checklist de performance

- [ ] Servidor fora de pasta sincronizada
- [ ] Exclusão de antivírus configurada
- [ ] `-cpuCount` = núcleos físicos
- [ ] `ZombieMaxCount` coerente com a RAM
- [ ] `CleanupLifetimeDefault` ≤ 60
- [ ] Boot completo em < 15 min (1º) e < 7 min (seguintes)
