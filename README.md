# DayZ Modpack Solo — Apocalipse (DayZ 1.30)

![DayZ](https://img.shields.io/badge/DayZ-1.30-4a4a4a)
![Mods](https://img.shields.io/badge/mods-39-2ea44f)
![Scripts](https://img.shields.io/badge/World-4450%20arquivos-blue)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-yellow)

Configuração completa de um servidor **DayZ 1.30** para jogar sozinho (ou com poucos
amigos): 39 mods, loot balanceado, 4 chefes com baú de recompensa, hordas de zumbis,
missões de IA, construção com BaseBuildingPlus e ajustes de performance.

> **Este repositório não distribui os mods.** Ele contém apenas configurações,
> arquivos de loot, perfis e documentação. Os mods são baixados pela Steam Workshop
> e pertencem aos seus autores.

---

## O que tem no pack

| Área | Conteúdo |
|---|---|
| **Mods** | 39 ativos, ordem de carga validada (`config/MODS.txt`) |
| **Loot** | `types.xml` com 5.719 tipos (3.962 com spawn ativo) |
| **Economia** | `globals.xml` ajustado (zumbis, animais, respawn, limpeza) |
| **Chefes** | 4 raid bosses com fases, minions, baú e marcador no mapa |
| **Hordas** | SF Zombie Horde (15–30 min, 10/onda, máx. 40 vivos) |
| **Missões IA** | 2 missões (NWAF Runway, Downed Helicopter) |
| **Construção** | BaseBuildingPlus **corrigido para a 1.30** (patch incluso) |
| **Admin** | VPPAdminTools |
| **Performance** | parâmetros de CPU/memória + limites de IA testados |

---

## Requisitos

- **DayZ Server 1.30** (Steam, gratuito em *Ferramentas*)
- Windows 10/11 64-bit
- 8 GB de RAM no mínimo — **16 GB recomendado** (pico medido: ~4,3 GB)
- ~25 GB livres em SSD (servidor + 39 mods)
- Cliente DayZ com **os mesmos 39 mods** ativos

---

## Instalação rápida

```text
1. Baixe o DayZ Server e os 39 mods pela Steam Workshop
2. Copie as pastas dos mods para a raiz do servidor como @Nome
3. Copie config/ do repositório para a raiz do servidor
4. Aplique o patch do BaseBuildingPlus (tools/patch_bbp.py)
5. Rode START.bat e conecte em 127.0.0.1:2302
```

O passo a passo completo, com comandos e verificação de cada etapa, está em
**[docs/01-instalacao.md](docs/01-instalacao.md)**.

---

## Estrutura do repositório

```text
dayz-modpack-solo/
├─ config/
│  ├─ MODS.txt                  ordem oficial dos 39 mods
│  ├─ START.bat                 launcher (lê MODS.txt)
│  ├─ serverDZ.cfg              configuração do servidor
│  ├─ db/
│  │  ├─ types.xml              5.719 tipos de loot
│  │  └─ globals.xml            limites de zumbis/animais/respawn
│  └─ profiles/                 configs de mods (bosses, mapa, IA, hordas)
├─ docs/
│  ├─ 01-instalacao.md          tutorial completo
│  ├─ 02-mods.md                lista e função de cada mod
│  ├─ 03-loot.md                types.xml + globals.xml
│  ├─ 04-bosses.md              chefes, baús e marcadores
│  ├─ 05-eventos.md             hordas, missões IA e eventos
│  ├─ 06-performance.md         parâmetros e números medidos
│  ├─ 07-troubleshooting.md     erros conhecidos e correções
│  └─ 08-correcao-bbp.md        patch do BaseBuildingPlus (1.30)
└─ tools/
   ├─ patch_bbp.py              corrige o PBO do BBP
   └─ pbo_scan.py               leitor de PBO (sem DayZ Tools)
```

---

## Destaques

### Chefes com recompensa
| # | Chefe | HP | Respawn | Baú |
|---|---|---|---|---|
| 01 | Chernarus Butcher | 2.100–2.800 | 45–60 min | 12 itens + 1.000 |
| 02 | Altar Signal Brute | 2.700–3.600 | 60–90 min | 16 itens + 2.500 |
| 03 | Severograd Bear King | 3.200–4.200 | 60–90 min | 22 itens + 5.000 |
| 04 | Tisy Blacksite Overlord | 3.900–5.200 | 90–120 min | 30 itens + 10.000 |

Eles nascem **on-demand** (quando você chega perto), têm fases de armadura,
minions, anti-camping e marcador vermelho no mapa. Detalhes em
[docs/04-bosses.md](docs/04-bosses.md).

### Performance
O pack foi ajustado para rodar bem em uma máquina só (servidor + cliente):

- `-cpuCount=4 -exThreads=7 -maxMem=2047 -maxVRAM=2047`
- Zumbis: 700 simultâneos · Animais: 140
- Loot: 2.000 no primeiro spawn, respawn em 10 min
- Chefes: spawn on-demand (não consomem CPU parados)

Medições e como ajustar em [docs/06-performance.md](docs/06-performance.md).

---

## Aviso legal

- Os **mods** são propriedade dos seus autores e são distribuídos pela Steam Workshop.
  Este repositório não contém, redistribui ou reempacota nenhum mod.
- O patch do BaseBuildingPlus é aplicado **na sua cópia local** do mod. Guarde o PBO
  original; o script nunca sobrescreve o arquivo de origem.
- DayZ é marca da Bohemia Interactive. Este é um projeto de fã, sem vínculo oficial.

## Créditos

- Todos os autores dos 39 mods (Expansion, BaseBuildingPlus, RaG, VPP, Dabs, etc.)
- Comunidade DayZ Brasil

## Licença

Configurações, scripts e documentação: [MIT](LICENSE).
