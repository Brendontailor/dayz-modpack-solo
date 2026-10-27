# 02 — Mods do pack

**39 mods ativos.** A ordem oficial está em [`config/MODS.txt`](../config/MODS.txt)
e é a única fonte usada pelo `START.bat`.

> Curiosidade técnica: o DayZ registra os addons na ordem **inversa** da linha
> `-mod=`. Por isso, no RPT, o `@VPPAdminTools` (último da lista) carrega
> primeiro e o `@CF` por último.

---

## Ordem de carga (por categoria)

```text
# --- Base / frameworks ---
@CF
@Dabs Framework

# --- Expansion (Bundle = Core + BaseBuilding + Market + Vehicles + Quests + AI + Groups) ---
@DayZ-Expansion-Bundle
@DayZ-Expansion-Licensed

# --- RaG (dependencias nesta ordem) ---
@RaG_Core
@RaG_BaseItems
@RaG_Vehicle_Pack

# --- Construcao ---
@BaseBuildingPlus
@BuilderItems
@Breachingcharge

# --- Mapas / HUD ---
@Basic Map

# --- Armas, roupas e equipamento ---
@Advanced Weapon Scopes
@MMG - Mightys Military Gear
@TLH Item Pack
@Forward Operator Gear
@Generic_Gunplay
@BS KeyRoom

# --- Sobrevivencia / utilidades ---
@CookZ
@KM_BetterFishing
@ProjectHope Survivor Backpack
@AmmoStackBullet
@Auto Stack - Proper
@Combinable Items
@BetterHarvest
@AutoCarFlip
@Bed-Respawning
@HeliWreckNoLoot
@Vehicle3PP
@JS Storage

# --- Mundo / pontos de interesse ---
@ApocalipticCityChernarus
@Secret Trader. Chernarus map. mapping

# --- Bandeira instantanea (precisa vir DEPOIS do Expansion) ---
@Instant Flag

# --- Zumbis / eventos ---
@PvZmoD_CustomisableZombies
@Beetle Zombie pack
@SF Zombie Horde Event

# --- Bosses e missoes ---
@MI Raid Boss
@Dynamic AI Missions for DayZ Expansion AI
@Dynamic Scavenging

# --- Admin ---
@VPPAdminTools
```

---

## Tabela dos 39 mods

| # | Mod | Categoria | O que faz |
|---:|---|---|---|
| 1 | `@CF` | Base | Community Framework: biblioteca de RPC, redes e configs usada por vários mods |
| 2 | `@Dabs Framework` | Base | Framework de UI/efeitos (luzes, notificações) usado por mods de armas |
| 3 | `@DayZ-Expansion-Bundle` | Base | Expansion completo: Core, BaseBuilding, Market, Vehicles, Quests, AI, Groups |
| 4 | `@DayZ-Expansion-Licensed` | Base | Assets licenciados do Expansion (mapas, veículos, objetos) |
| 5 | `@RaG_Core` | Framework | Núcleo do conjunto RaG (armas/veículos) |
| 6 | `@RaG_BaseItems` | Itens | Itens-base e peças do RaG |
| 7 | `@RaG_Vehicle_Pack` | Veículos | Veículos adicionais do RaG |
| 8 | `@BaseBuildingPlus` | Construção | Construção avançada (paredes, portas, cadeados, flag) — **corrigido para 1.30** |
| 9 | `@BuilderItems` | Construção | Objetos de construção (móveis, muros, rampas) |
| 10 | `@Breachingcharge` | Construção | Carga de arrombamento para invadir bases |
| 11 | `@Basic Map` | HUD | Mapa com marcadores, waypoints e marcadores de servidor |
| 12 | `@Advanced Weapon Scopes` | Armas | Lunetas e miras avançadas |
| 13 | `@MMG - Mightys Military Gear` | Roupas | Equipamento militar (coletes, capacetes, mochilas) |
| 14 | `@TLH Item Pack` | Itens | Pacote de itens variados (roupas, utilidades) |
| 15 | `@Forward Operator Gear` | Roupas | Equipamento tático moderno |
| 16 | `@Generic_Gunplay` | Armas | Ajustes de manuseio/recuo das armas |
| 17 | `@BS KeyRoom` | Utilidades | Sistema de salas/chaves para bases |
| 18 | `@CookZ` | Sobrevivência | Culinária: panelas, receitas e comida |
| 19 | `@KM_BetterFishing` | Sobrevivência | Pesca melhorada (varas, iscas, peixes) |
| 20 | `@ProjectHope Survivor Backpack` | Roupas | Mochilas de sobrevivente |
| 21 | `@AmmoStackBullet` | Utilidades | Empilhamento de munição solta |
| 22 | `@Auto Stack - Proper` | Utilidades | Empilhamento automático no inventário |
| 23 | `@Combinable Items` | Utilidades | Combina/desmonta itens (kits, peças) |
| 24 | `@BetterHarvest` | Sobrevivência | Coleta de recursos mais rápida/completa |
| 25 | `@AutoCarFlip` | Veículos | Desvirar veículos sozinho |
| 26 | `@Bed-Respawning` | Utilidades | Respawn em camas |
| 27 | `@HeliWreckNoLoot` | Mundo | Remove loot dos helicópteros caídos (evita farm fácil) |
| 28 | `@Vehicle3PP` | Veículos | Permite 3ª pessoa em veículos |
| 29 | `@JS Storage` | Utilidades | Armazenamento extra (baús) — **sem `.bisign`** |
| 30 | `@ApocalipticCityChernarus` | Mundo | Expansão urbana de Chernarus (cidade e POIs) |
| 31 | `@Secret Trader. Chernarus map. mapping` | Mundo | Pontos de traders com marcadores no mapa — **sem `.bikey`** |
| 32 | `@Instant Flag` | Construção | Captura de bandeira instantânea (override do Expansion) |
| 33 | `@PvZmoD_CustomisableZombies` | Zumbis | Customização de zumbis (tipos, dano, comportamento) |
| 34 | `@Beetle Zombie pack` | Zumbis | Variantes de zumbis (chefes, monstros) |
| 35 | `@SF Zombie Horde Event` | Eventos | Hordas periódicas com aviso e recompensa |
| 36 | `@MI Raid Boss` | Chefes | 4 raid bosses com fases e baú de recompensa |
| 37 | `@Dynamic AI Missions for DayZ Expansion AI` | Missões | Missões com bots do Expansion AI |
| 38 | `@Dynamic Scavenging` | Loot | Loot dinâmico em prédios/containers |
| 39 | `@VPPAdminTools` | Admin | Ferramentas de administração (teleporte, spawn, logs) |

---

## Mods desativados de propósito

| Mod | Motivo |
|---|---|
| `@DayZ-Expansion-Core` | Já incluído no **Bundle** (duplicaria addons e scripts) |
| `@DayZ-Expansion-BaseBuilding` | Já incluído no Bundle |
| `@DayZ-Expansion-Market` | Já incluído no Bundle |
| `@DayZ-Expansion-Vehicles` | Já incluído no Bundle |
| `@MiniMap` | Redundante com o **Basic Map** (dois mapas = mais HUD e menos FPS) |

As pastas continuam no disco — apenas as linhas estão comentadas no `MODS.txt`.
Para reativar, remova o `#` da linha.

---

## Dependências e pegadinhas

1. **`@RaG_Core` → `@RaG_BaseItems` → `@RaG_Vehicle_Pack`**
   Nessa ordem. Inverter causa classes não encontradas no `World`.

2. **Expansion**: use **somente o Bundle**. Ativar Core/BaseBuilding/Market/Vehicles
   separados duplica addons (`BuilderItems_*`, `Expansion_*`) e o servidor
   registra conflitos como:
   `Conflicting addon BuilderItems_rocks_sakhal ... previous definition in 'BuilderItems\rocks_sakhal\'`.

3. **`@Instant Flag` precisa vir depois do Expansion** — ele substitui
   (`modded`) a lógica de captura de bandeira.

4. **`@BaseBuildingPlus` depois de `@RaG_*`** — ele estende classes de base.

5. **`@Basic Map`** é quem lê `profiles\BasicMap\ServerMarkers.json`
   (marcadores dos chefes).

6. **`@VPPAdminTools` por último** — ele monitora os demais mods.

---

## Duplicados: o que foi verificado

Antes de fechar o pack, todos os 3.661 scripts dos 39 mods foram varridos:

| Verificação | Resultado |
|---|---|
| Funções (`Classe.metodo`) definidas por 2+ mods | **0** |
| Caminhos virtuais de script iguais em 2+ mods | **0** |
| Nomes de PBO iguais em 2+ mods | apenas os do **Expansion Bundle** × BuilderItems (esperado) |

Se for adicionar um mod novo, rode a mesma checagem: funções e caminhos
duplicados são a causa mais comum de crash silencioso.
