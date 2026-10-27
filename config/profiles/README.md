# config/profiles — configurações dos mods

Estes arquivos são copiados para `C:\DayZServer\profiles\`, onde os mods os leem
no boot.

```text
profiles\
├─ MI_RaidBoss\      chefes, baús e settings       (doc: 04-bosses.md)
├─ BasicMap\         marcadores no mapa            (doc: 04-bosses.md)
├─ AIMissions\       missões com bots do Expansion (doc: 05-eventos.md)
└─ ZombieHorde\      hordas de zumbis              (doc: 05-eventos.md)
```

> As pastas são **criadas pelo próprio mod** no primeiro boot. Copiar antes só
> antecipa a configuração; se um arquivo não existir, o mod gera o padrão dele.

---

## `MI_RaidBoss/`

| Arquivo | O que define |
|---|---|
| `Settings.json` | comportamento global: anúncios, hotkey, barra de vida, debug |
| `Bosses.json` | os 4 chefes — classe, posição, HP, fases, resistências, minions, drops |
| `RewardChests.json` | conteúdo de cada baú de recompensa (itens + moeda) |

Os 4 chefes: **Chernarus Butcher**, **Altar Signal Brute**, **Severograd Bear
King**, **Tisy Blacksite Overlord**. Todos nascem on-demand (`requirePlayerInAreaToSpawn`),
com 4 fases de armadura e minions.

## `BasicMap/`

| Arquivo | O que define |
|---|---|
| `ServerMarkers.json` | marcadores fixos no mapa (**inclui os 4 chefes**, em vermelho) |
| `ServerSettings.json` | opções do mapa: zoom, grid, waypoints, 3D markers |

O ícone dos chefes é `BasicMap\gui\images\warn.paa`, cor `[200, 40, 40]`,
`Group: BASICMAP_SERVER`.

## `AIMissions/`

| Arquivo | O que define |
|---|---|
| `MainConfig.json` | 2 missões (NWAF Runway, Downed Helicopter), loadout dos bots, timers, marcadores |

Padrão: 1 missão por vez, 15 min para a primeira, 30 min entre elas, 30 min de
duração, raio de 500 m.

## `ZombieHorde/`

| Arquivo | O que define |
|---|---|
| `Settings/GeneralSettings.json` | timers, ondas, raio de spawn, limpeza |
| `Settings/ZombieTypes.json` | tipos de zumbi que a horda usa |
| `Settings/Rewards.json` | recompensas por sobreviver/concluir |
| `Settings/Permissions/Whitelist.json` | quem pode forçar uma horda via comando |

Padrão: 1 horda a cada 15–30 min, 10 zumbis por onda de 20 s, máximo 40 vivos,
duração de 3 min, aviso 60 s antes.

---

## Editar com segurança

1. **Valide o JSON antes de reiniciar:**

```powershell
Get-Content .\profiles\MI_RaidBoss\Bosses.json -Raw | ConvertFrom-Json | Out-Null
"JSON OK"
```

Se der erro, o mod **ignora o arquivo inteiro** e usa o padrão — sem aviso claro
no log.

2. **Não use comentários** (`//` ou `/* */`) nesses arquivos: não é JSONC.
   Uma vírgula sobrando no último item invalida tudo.

3. **Reinicie o servidor.** Os mods leem esses arquivos apenas no boot.

4. **Guarde o padrão.** Se editar muito, copie o arquivo antes:

```powershell
Copy-Item .\profiles\MI_RaidBoss\Bosses.json .\profiles\MI_RaidBoss\Bosses.json.bak
```

---

## Onde confirmar que carregou

```powershell
$rpt = Get-ChildItem C:\DayZServer\profiles\*.RPT | Sort LastWriteTime | Select -Last 1
Select-String $rpt -Pattern "MI Raid Boss|AI Missions|ZombieHorde|BasicMap"
```

Esperado:

```text
[MI Raid Boss] Config loaded. Enabled=true, Bosses=4, UpdateInterval=2.
[AI Missions] Loaded!
[AI Missions] Initialized! Waiting for 900 seconds ...
[ZombieHorde] Loaded general settings: $profile:ZombieHorde\Settings\GeneralSettings.json
[ZombieHorde] Zombie Horde manager started.
```
