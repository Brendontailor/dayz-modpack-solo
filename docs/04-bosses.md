# 04 — Chefes (MI Raid Boss)

Quatro raid bosses espalhados por Chernarus, com **fases**, **minions**,
**baú de recompensa** e **marcador no mapa**.

Configurações:

```text
profiles\MI_RaidBoss\
├─ Settings.json        comportamento global (anúncios, UI, hotkey)
├─ Bosses.json          os 4 chefes (posição, HP, fases, drops)
└─ RewardChests.json    o conteúdo de cada baú
profiles\BasicMap\ServerMarkers.json   marcadores no mapa
```

---

## Os 4 chefes

| # | Nome | Classe | Posição (x y z) | HP | Respawn | Baú |
|---|---|---|---:|---:|---|---|
| 01 | **Chernarus Butcher** | `ZmbM_DoctorFat_Winter` | `6351.6 51.6 3020.0` | 2.100–2.800 | 45–60 min | 12 itens + 1.000 |
| 02 | **Altar Signal Brute** | `ZmbM_HeavyIndustryWorker` | `8144.6 475.1 9132.6` | 2.700–3.600 | 60–90 min | 16 itens + 2.500 |
| 03 | **Severograd Bear King** | `Animal_UrsusArctos` | `14162.3 142.0 15043.3` | 3.200–4.200 | 60–90 min | 22 itens + 5.000 |
| 04 | **Tisy Blacksite Overlord** | `ZmbM_usSoldier_Heavy_Woodland` | `556.6 501.8 13671.7` | 3.900–5.200 | 90–120 min | 30 itens + 10.000 |

### Onde ficam

```text
01 Butcher      → oeste de Chernogorsk (perto da costa)
02 Altar Signal → centro-sul, região de Electro/Altar
03 Bear King    → nordeste (Severograd)
04 Overlord     → noroeste (Tisy / base militar)
```

Os marcadores aparecem no **Basic Map** com o ícone `warn.paa` vermelho
(`RGB 200,40,40`), sempre visíveis (`HideOnMap: false`).

---

## Como eles nascem

```json
"spawnOnServerStart": false,
"requirePlayerInAreaToSpawn": true
```

- **Não** spawnam quando o servidor liga (economiza CPU).
- Nascem quando um jogador entra no raio de spawn da posição.
- Depois de mortos, respeitam o `respawnMinutesMin/Max` do chefe.
- `persistenceEnabled: 0` → o timer de respawn **não** sobrevive a restart
  (ele volta a ficar disponível). Se quiser persistência, mude para `1`.

---

## Mecânicas de combate

### Fases de armadura (por % de vida)

| Vida | Fase | Efeito |
|---:|---|---|
| 100% | Normal | — |
| **≤ 75%** | **Guarded** | Spawna 1–2 minions; anúncio "armor is hardening" |
| **≤ 50%** | **Armored** | Spawna 1–2 minions; balas causam 15% menos dano |
| **≤ 25%** | **Rage** | Chefe cresce (2,6–3,1×), 2–3 minions, dano recebido −10% |
| **≤ 10%** | **Last Stand** | Cresce mais (3,2–3,45×), cura 5%, 2–3 minions, dano recebido −20% |

### Resistências (chefe)

| Tipo de dano | Multiplicador |
|---|---:|
| Bala (corpo) | 0,90 |
| Bala (cabeça) | 1,35 |
| Corpo a corpo | 0,18 |
| Explosivo | 0,65 |
| Veículo | **0** (imune a atropelamento) |
| Armadilha | 0,70 |

### Minions

- 2–4 no spawn, até **6 vivos**, respawn a cada **120 s**.
- 2–3 por fase, raio de 12–18 m.
- Dano ao jogador: 18% do chefe (bem mais fracos).
- Morrem junto com o chefe (`minionsDespawnOnDeath`, 30 s).

### Anti-camping

- **Anti-perch**: ficar em telhado/altura reduz o dano do chefe, mas ele
  escala até 50% do normal em 11 m de altura; minions atiram em quem está
  elevado.
- **Anti-veículo**: 12 de dano a cada 3 s em quem fica dentro de veículo no
  raio de 27 m (só quando o raid está engajado).
- **Leash**: 60 m — fora disso o chefe volta.
- **Raio de dano**: 90 m — mais longe que isso, dano bloqueado com aviso.

### Vida escalonada

`healthScaling`: +25% de vida por jogador extra (máx. 2×).
Solo: HP base. Dupla: 1,25×. Trio: 1,5×. Quatro+: 2×.

---

## Baús de recompensa

Cada chefe deixa um baú (`MIRB_RaidBossChest*`) que:

- só pode ser aberto pelo **matador** (`rewardChestKillerOnlyClaim: true`);
- expira em **120 s** após a morte (`rewardChestClaimSeconds`);
- é removido em **30 min** (`rewardChestCleanupMinutes`);
- sorteia `itemsToSpawn` itens (com duplicatas permitidas) + moeda interna.

### Resumo dos drops

| Baú | Itens sorteados | Moeda | Destaques |
|---|---:|---:|---|
| 01 | 12 | 1.000 | AKM, SKS, Mosin, colete, capacete, meds |
| 02 | 16 | 2.500 | M4A1 + ACOG, AK101 + Kobra, AKM drum, **NVGoggles**, Rangefinder, LandMine |
| 03 | 22 | 5.000 | FAL + ACOG, SVD + PSO-1, M4A1_Green + supressor, VSS, Ghillie, Claymore, 40mm |
| 04 | 30 | 10.000 | FAL, SVD, M4A1_Black + supressor, ASVAL, **M79**, gás CS, 2 coletes, NVG, explosivos |

> A moeda (`currency`) está **desativada** (`enabled: 0`) — os valores ficam só
> como referência caso você ative o mercado do Expansion.

---

## Interface e anúncios

| Recurso | Config |
|---|---|
| Hotkey do painel de raid | **NUMPAD 1** |
| Painel público | `raidStatusUiPublic: 1` |
| Barra de vida do chefe | `raidBossHealthBarEnabled: 1` |
| Anúncio no chat | `[Boss] <nome> is alive.` |
| Anúncio de morte | `[Boss] <nome> defeated. Respawn: <tempo>.` |
| Discord webhook | desativado (`enabled: 0`) |

Para anunciar **para todos** os jogadores (e não só quem está perto), mude no
chefe:

```json
"announceLifecycleToAllPlayers": true
```

---

## Como testar

### Opção 1 — ir até o chefe (recomendado)

1. Entre no servidor.
2. Use o VPPAdminTools para teleportar até a posição do chefe (ex.: Tisy
   `556 501 13671`).
3. Ao chegar no raio, o chefe nasce e anuncia no chat.

### Opção 2 — forçar no boot

Em `Bosses.json`, no chefe desejado:

```json
"spawnOnServerStart": true
```

Reinicie. Ele nasce junto com o mundo (útil para testar drops).

### Opção 3 — debug

```json
"debugLogging": 1,
"damageDebugEnabled": 1,
"damageDebugChat": 1
```

O log sai em `profiles\script_*.log` com prefixo `[MI Raid Boss]`.

---

## Como adicionar um novo chefe

1. Copie um bloco inteiro em `Bosses.json` e troque:
   - `id` (único, ex.: `"05"`),
   - `bossName`, `bossClassName`, `position`,
   - `rewardChestId`.
2. Copie o baú correspondente em `RewardChests.json` (`id: "05"`).
3. Adicione o marcador em `profiles\BasicMap\ServerMarkers.json`:

```json
{
  "Name": "BOSS - Meu Chefe",
  "Pos": [1234.0, 0.0, 5678.0],
  "Icon": "BasicMap\\gui\\images\\warn.paa",
  "Is3DMarker": false,
  "Colour": [200, 40, 40],
  "Alpha": 240,
  "Group": "BASICMAP_SERVER"
}
```

4. Reinicie. Confira no RPT:

```text
[MI Raid Boss] Config loaded. Enabled=true, Bosses=5, UpdateInterval=2.
```

> Se o JSON tiver vírgula sobrando, o mod ignora o arquivo e usa o padrão —
> valide com `Get-Content Bosses.json -Raw | ConvertFrom-Json` no PowerShell.

---

## Solução de problemas

| Sintoma | Causa provável | Correção |
|---|---|---|
| Chefe não nasce | `enabled: false` ou jogador fora do raio | Ative e aproxime-se |
| Baú não abre | não foi o matador | `rewardChestKillerOnlyClaim: false` |
| Baú some rápido | 120 s de claim | aumente `rewardChestClaimSeconds` |
| Chefe imortal | dano de veículo = 0 | use arma/explosivo |
| Marcador não aparece | Basic Map não carregou o JSON | veja `profiles\BasicMap\` e o RPT |
| Crash ao matar | classe de baú inválida | confira `rewardChestClassName` |
