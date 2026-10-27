# 03 — Loot e economia (`types.xml` / `globals.xml`)

Dois arquivos controlam todo o loot do servidor:

```text
mpmissions\dayzOffline.chernarusplus\db\
├─ types.xml     → O QUE pode spawnar (item por item)
└─ globals.xml   → QUANTO e QUÃO RÁPIDO o servidor repõe
```

---

## `types.xml` — 5.719 tipos

| Métrica | Valor |
|---|---|
| Tipos no arquivo | **5.719** |
| Tipos com `nominal > 0` (spawn ativo) | **3.962** |
| Duplicados de `<type name="...">` | **0** |

O arquivo é a **mescla** do `types.xml` vanilla com os `types.xml` de todos os
mods do pack. Regras usadas na mescla:

1. Um `<type>` por `name` — se dois mods definem o mesmo item, vale o de maior
   `nominal` (evita item "sumir" por causa de um mod antigo).
2. Itens de mods que vinham com `nominal = 0` e eram claramente loot (ex.: o
   conjunto **FOG**) foram forçados para `nominal = 1` — sem isso eles nunca
   apareceriam no mapa.
3. Categorias (`<category name="...">`) preservadas.
4. Nada de `<type>` sem `<nominal>` ou sem `<lifetime>` (o CE ignora).

### Estrutura de um item

```xml
<type name="AKM">
    <nominal>8</nominal>          <!-- quantos existem no mapa -->
    <lifetime>14400</lifetime>     <!-- segundos até sumir -->
    <restock>0</restock>           <!-- 0 = usa o respawn global -->
    <min>4</min>                   <!-- mínimo antes de repor -->
    <quantmin>-1</quantmin>        <!-- -1 = quantidade cheia -->
    <quantmax>-1</quantmax>
    <cost>100</cost>               <!-- prioridade de spawn -->
    <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="1" crafted="0" deloot="0"/>
    <category name="weapons"/>
    <usage name="Military"/>
</type>
```

### Como ajustar

**Deixar uma arma mais rara**

```xml
<type name="M4A1">
    <nominal>3</nominal>   <!-- era 8 -->
```

**Fazer um item aparecer só em helicóptero**

```xml
<flags ... deloot="1"/>
```

**Tirar um item do mapa**

```xml
<nominal>0</nominal>
```

Depois de editar, **apague o cache de economia** para o servidor reler:

```powershell
Remove-Item "C:\DayZServer\mpmissions\dayzOffline.chernarusplus\storage_1\data\types.bin" -Force
```

> ⚠️ Isso **não** apaga o loot já existente no mundo, só força o recálculo na
> próxima inicialização. Para um mundo limpo, apague `storage_1` inteiro (perde
> bases e personagens).

---

## `globals.xml` — valores atuais

| Variável | Valor | O que faz |
|---|---:|---|
| `SpawnInitial` | **1.500** | Itens criados no primeiro boot |
| `RespawnTypes` | **16** | Tipos repostos por ciclo |
| `RespawnLimit` | **28** | Máx. de itens repostos por ciclo |
| `RestartSpawn` | **600** | Segundos entre ciclos de respawn (10 min) |
| `LootSpawnAvoidance` | **150** | Distância (m) que evita spawnar loot perto de jogador |
| `ZombieMaxCount` | **450** | Zumbis simultâneos no mapa |
| `AnimalMaxCount` | **80** | Animais simultâneos |
| `CleanupLifetimeDefault` | **20** | Itens comuns somem em 20 s após largados |
| `CleanupLifetimeLimit` | **50** | Teto de itens "largados" por célula |
| `CleanupLifetimeDeadInfected` | **240** | Corpo de zumbi: 4 min |
| `CleanupLifetimeDeadAnimal` | **600** | Corpo de animal: 10 min |
| `CleanupLifetimeDeadPlayer` | **3.600** | Corpo de jogador: 1 h |
| `CleanupLifetimeRuined` | **300** | Item arruinado: 5 min |
| `CleanupAvoidance` | **100** | Não limpa loot a menos de 100 m de jogador |

### Por que esses valores

- **1.500 no primeiro spawn** dá um mundo "cheio" sem derrubar o boot.
- **16 tipos / 28 itens a cada 10 min** mantém o loot girando sem enxurrada.
- **450 zumbis** é o teto que a máquina de teste aguentou com o **cliente
  rodando junto** (era 700, reduzido na otimização de 26/10 — cada zumbi é uma
  IA completa, com física e rede). Em servidor dedicado sem cliente, pode voltar
  para 700.
- **80 animais** (era 140) pelo mesmo motivo: animal também é IA com física.
- **Cleanup agressivo (20 s)** é o que mais ajuda FPS: item largado no chão
  custa caro.

---

## Avisos conhecidos

### Dynamic Scavenging — 81 classnames inexistentes

No boot o mod avisa:

```text
[DynamicScavenging] CONFIG WARNING: jackpotItems references unknown item classname "Deagle_Gold"
[DynamicScavenging] Loot data validation found 81 unknown classname(s)
```

São itens de "jackpot" que não existem no pack (ex.: `Deagle_Gold`, `M14`,
`Scout`, `Mag_Aug_30Rnd`). **Não quebra nada** — esses itens simplesmente não
aparecem. Para limpar, edite o config do mod e remova as entradas com aviso.

### FOG forçado para `nominal = 1`

O conjunto **FOG** (MFS/Mustache etc.) veio com `nominal=0` no `types.xml`
original. Foi ajustado para `1` para poder aparecer. Se achar que aparece
demais, reduza para `0` novamente.

---

## Checklist de loot

- [ ] `types.xml` copiado para `mpmissions\dayzOffline.chernarusplus\db\`
- [ ] `globals.xml` copiado para a mesma pasta
- [ ] Nenhum `<type>` duplicado (`Select-String` por `name=` deve dar 0 repetidos)
- [ ] Após editar: `types.bin` removido para forçar recálculo
- [ ] Boot sem `SCRIPT (E)` relacionado a CE
