# Changelog

Todas as mudanças relevantes do modpack. Formato baseado em
[Keep a Changelog](https://keepachangelog.com/pt-BR/) e versionamento
[SemVer](https://semver.org/lang/pt-BR/).

---

## [1.0.1] — 2026-10-26

### Adicionado
- **`config/PLAY.bat`** — inicia o **cliente** com os mesmos 39 mods do
  servidor (lê o `MODS.txt`, caminhos absolutos) e conecta em `127.0.0.1:2302`.
  Sem ele o cliente sobe vanilla e **nenhuma ação funciona** em jogo.
- Seção 13 no troubleshooting: "Nenhuma ação funciona: porta, água, comida".

### Alterado (otimização)
- `ZombieMaxCount`: 700 → **450** (cada zumbi é uma IA com física/rede).
- `AnimalMaxCount`: 140 → **80**.
- `SpawnInitial`: 2.000 → **1.500**.
- `CleanupLifetimeDefault`: 30 s → **20 s**.
- `START.bat`: encerramento **suave** (`taskkill` sem `/F`, 20 s de espera)
  antes do forçado — evita save corrompido no reinício de 12 h.

### Notas
- Em máquina com 16 GB rodando servidor + cliente, a RAM é o gargalo:
  com 98% em uso as ações cancelam por timeout. Liberar OneDrive/Steam
  devolve ~5 GB e normaliza o jogo.

---

## [1.0.0] — 2026-10-26

### Adicionado
- Documentação completa em `docs/` (instalação, mods, loot, chefes, eventos,
  performance e troubleshooting).
- Script `tools/patch_bbp.py` para corrigir o BaseBuildingPlus na DayZ 1.30,
  com recálculo do hash SHA-1 interno do PBO.
- 4 raid bosses em `profiles/MI_RaidBoss/` com baús de recompensa:
  - Chernarus Butcher (2.100–2.800 HP, 45–60 min)
  - Altar Signal Brute (2.700–3.600 HP, 60–90 min)
  - Severograd Bear King (3.200–4.200 HP, 60–90 min)
  - Tisy Blacksite Overlord (3.900–5.200 HP, 90–120 min)
- Marcadores dos 4 chefes em `profiles/BasicMap/ServerMarkers.json`.
- 2 missões de IA em `profiles/AIMissions/MainConfig.json`.
- Config de hordas em `profiles/ZombieHorde/Settings/`.
- `types.xml` mesclado com 5.719 tipos (3.962 com spawn ativo).
- `globals.xml` ajustado para performance e respawn.

### Corrigido
- **BaseBuildingPlus não compilava** na DayZ 1.30:
  `Undefined function 'CombinationLock.UnlockServer'` → `Can't compile "World" script module!`.
  - 4 chamadas trocadas para `UnlockOnServer` (2 arquivos de 858 entradas).
  - `config.bin`, prefixo e demais entradas preservados byte a byte.
  - SHA-1 de integridade do PBO recalculado (sem isso o engine crasha nativamente).
- Crash ao carregar save antigo (`Scripted variables corrupted upon "ChernarusMap"`)
  resolvido com mundo novo; save corrompido removido.

### Alterado
- `MODS.txt` passou a ser a única fonte da ordem de mods (o `START.bat` lê o arquivo).
- `START.bat` detecta a própria pasta (`%~dp0`) em vez de caminho fixo.
- Expansion consolidado no **Bundle** (Core/BaseBuilding/Market/Vehicles desativados).
- `@MiniMap` desativado (redundante com o Basic Map).

### Removido
- Mundo de teste corrompido de 25/10 (`storage_1`).

---

## [0.1.0] — 2026-10-25

### Adicionado
- Primeira montagem do servidor com 39 mods.
- `START.bat` com detecção de pastas ausentes.
- `serverDZ.cfg` para uso solo (`maxPlayers=1`, `verifySignatures=0`).
