# 05 — Eventos: hordas, missões IA e eventos do mundo

Três sistemas rodam em paralelo no servidor:

| Sistema | Mod | Config |
|---|---|---|
| Hordas de zumbis | SF Zombie Horde Event | `profiles\ZombieHorde\Settings\` |
| Missões com bots | Dynamic AI Missions (Expansion AI) | `profiles\AIMissions\MainConfig.json` |
| Eventos do mundo | Central Economy (vanilla) | `types.xml` / `globals.xml` |

---

## 1. Hordas — SF Zombie Horde Event

### Configuração atual

`profiles\ZombieHorde\Settings\GeneralSettings.json`

| Parâmetro | Valor | Significado |
|---|---:|---|
| `Enabled` | 1 | Liga o sistema |
| `MinPlayersOnline` | 1 | Precisa de 1 jogador online |
| `MinTimeBetweenEventsSeconds` | **900** | 15 min mínimo entre hordas |
| `MaxTimeBetweenEventsSeconds` | **1800** | 30 min máximo |
| `WarningDurationSeconds` | **60** | Aviso 1 min antes |
| `EventDurationSeconds` | **180** | A horda dura 3 min |
| `SpawnIntervalSeconds` | **20** | Uma onda a cada 20 s |
| `ZombiesPerWave` | **10** | 10 zumbis por onda |
| `MaxAliveEventZombies` | **40** | Teto de zumbis vivos da horda |
| `SpawnRadiusMin` / `Max` | **35 / 90** | Nascem de 35 a 90 m de você |
| `AggroSpawnRadiusMin` / `Max` | 8 / 18 | Zumbis agressivos nascem perto |
| `CleanupSpawnedInfectedOnEnd` | 1 | Remove os sobreviventes ao fim |

### Como funciona

```text
15–30 min  →  aviso no chat/tela ("A horde event is about to begin")
   60 s    →  contagem regressiva
    0 s    →  começa o spawn: 10 zumbis a cada 20 s durante 180 s
  180 s    →  fim: sobra o que não foi morto, depois limpa
```

O evento sorteia a localização **perto do jogador** (35–90 m), então não existe
"mapa de horda": ela vem até você.

### Recompensa

`Rewards.json` define itens entregues ao sobreviver/concluir. Ajuste os
`ClassName` e `ChancePercent` conforme o seu loot.

### Como confirmar que está ativo

No RPT/script log:

```text
[ZombieHorde] Loaded general settings: $profile:ZombieHorde\Settings\GeneralSettings.json
[ZombieHorde] Next horde event scheduled in 1623 seconds.
[ZombieHorde] Zombie Horde manager started.
```

### Deixar mais leve / mais pesada

| Objetivo | Mudança |
|---|---|
| Menos lag | `ZombiesPerWave: 6`, `MaxAliveEventZombies: 24` |
| Mais raro | `MinTime: 1800`, `MaxTime: 3600` |
| Mais desafiador | `ZombiesPerWave: 15`, `MaxAlive: 60`, `EventDuration: 300` |
| Desligar | `Enabled: 0` |

> ⚠️ Cada zumbi extra consome CPU. Com `ZombieMaxCount=700` no `globals.xml`,
> uma horda de 40 ainda cabe no teto — mas em máquina fraca reduza os dois.

---

## 2. Missões de IA — Dynamic AI Missions

### Configuração atual

`profiles\AIMissions\MainConfig.json`

| Parâmetro | Valor | Significado |
|---|---:|---|
| `Missions_Max_Concurrent` | **1** | Só 1 missão por vez |
| `Mission_Start_Delay` | **900** | 15 min após o boot para a 1ª |
| `Mission_Time_Between` | **1800** | 30 min entre missões |
| `Mission_Time_Limit` | **1800** | 30 min para completar |
| `Mission_Time_Extension_Limit` | 900 | +15 min de prorrogação |
| `Mission_Inner_Radius` | 500 | Raio da área da missão |
| `Mission_AI_Spawn_Radius` | 1200 | Onde os bots podem nascer |
| `Cleanup_Radius_Running` | 100 | Limpa corpos a 100 m |
| `Bots_Timeout_Time` | 300 | Bots somem se ninguém chegar em 5 min |
| `Minimum_Players` | 0 | Funciona solo |
| `Markers_CircleRadius` | 350 | Círculo vermelho no mapa |
| `Notification_Time` | 10 | Aviso de 10 s antes |

### As 2 missões

| Missão | Local | Bots | Recompensa |
|---|---|---:|---|
| **NWAF Runway** | Aeroporto NWAF `4176 339 10726` | 3–5 | Caixa + chance de veículo |
| **Downed Helicopter** | Oeste `144 320 8074` | 2–3 | Caixa + helicóptero Mi-8 caído |

Loadout dos bots: **M4A1 + ACOG + CMAG 40** (ID 1), colete e capacete.

### Como confirmar

```text
[AI Missions] Loaded!
[AI Missions] Initialized! Waiting for 900 seconds before running cleanup script and attempting to start first mission.
```

Depois de 15 min:

```text
Mission 'NWAF Runway' starting! Eliminate all threats to claim the loot!
```

> Avisos `FIX-ME: Unexpected statement 'ref'` no `3_Game` são **warnings** do
> compilador (sintaxe antiga), não impedem o mod de funcionar.

---

## 3. Eventos do mundo (Central Economy)

O `globals.xml` mantém os eventos vanilla ativos — no boot o log mostra:

```text
[CE][DynEvent] :: 51 types
```

São 51 tipos de evento dinâmico (helicóptero caído, comboios militares,
acampamentos, etc.) que o CE sorteia pelo mapa. Eles dependem de:

- `<flags deloot="1">` nos itens de evento no `types.xml`;
- `RestartSpawn = 600` (10 min) para repor;
- `SpawnInitial = 2000` para o primeiro povoamento.

> **HeliWreckNoLoot** está ativo: o helicóptero caído **não** traz loot.
> Se quiser o loot de volta, comente `@HeliWreckNoLoot` no `MODS.txt`.

---

## Linha do tempo de uma sessão

```text
t = 0 min     servidor liga (mundo + loot + zumbis)
t = 10-13 min pronto para conectar (1º boot)
t = 15 min    1ª missão de IA (NWAF Runway ou Downed Helicopter)
t = 15-30 min 1ª horda (aleatório)
t = 30 min    próxima missão (se a anterior terminou)
t = 45-60 min próxima horda
...
boss           quando você entra no raio de um dos 4
```

---

## Ajustes rápidos

### Quero menos eventos (mais tranquilo)

```jsonc
// ZombieHorde/GeneralSettings.json
"MinTimeBetweenEventsSeconds": 1800,
"MaxTimeBetweenEventsSeconds": 3600,
"ZombiesPerWave": 8,
"MaxAliveEventZombies": 24

// AIMissions/MainConfig.json
"Mission_Time_Between": 3600,
"Missions_Max_Concurrent": 1,
"Bots_Count_Maximum": 3
```

### Quero mais ação

```jsonc
"MinTimeBetweenEventsSeconds": 600,
"MaxTimeBetweenEventsSeconds": 1200,
"ZombiesPerWave": 15,
"MaxAliveEventZombies": 60,
"Mission_Time_Between": 900
```

Depois de editar qualquer JSON, **reinicie o servidor** — os mods leem os
arquivos apenas no boot.

---

## Checklist de eventos

- [ ] `profiles\ZombieHorde\Settings\*.json` presentes
- [ ] `profiles\AIMissions\MainConfig.json` com JSON válido
- [ ] RPT mostra `ZombieHorde manager started` e `AI Missions Initialized`
- [ ] `[CE][DynEvent] :: 51 types` no boot
- [ ] Horda/missão testadas depois de 15–30 min de servidor no ar
