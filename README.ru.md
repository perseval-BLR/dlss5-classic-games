# DLSS 5 Neural Rendering в 22 играх без нативного DLSS

Рабочие установки DLSS 5 Neural Rendering (nvngx_dlssnr.dll 310.8.0) в двадцати двух играх, которые вышли без DLSS, проверено на RTX 5070 Ti (16 GB) + Ryzen 7 9800X3D, 4K:

| Игра | Движок / API | Схема | Статус |
|---|---|---|---|
| Deus Ex: Human Revolution | Daedalus, 32-bit нативный D3D11 | ReShade x86 dxgi + DLSS5-Feeder addon32 + host64 + Lumenite | ✅ работает |
| The Elder Scrolls III: Morrowind (OpenMW) | OpenMW 0.51, 64-bit OpenGL | ReShade64 как opengl32.dll + Feeder addon64 + VORT (векторы движения) | ✅ работает |
| Fallout 3 | Gamebryo, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + Lumenite | ✅ работает |
| Black Mesa | Source 2013, 32-bit D3D9 | DXVK 3.0.2 x86 + глобальный Vulkan-слой ReShade + Feeder addon32 + Lumenite | ✅ работает |
| Quake III Arena | ioq3, 64-bit OpenGL | ReShade64 как opengl32.dll + Feeder addon64 + VORT (ioq3 обязателен — GOG-бинарь грузит system32 opengl32) | ✅ работает |
| Serious Sam: The First Encounter | Serious Engine 1, 32-bit OpenGL | ReShade x86 как opengl32.dll + Feeder addon32 + host64 + VORT | ✅ работает |
| Far Cry 2004 | CryEngine 1, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + Lumenite | ✅ работает |
| Star Wars Jedi Knight: Jedi Academy | id Tech 3, 32-bit OpenGL | ReShade x86 как opengl32.dll + Feeder addon32 + host64 + VORT | ✅ работает |
| The Chronicles of Riddick: Assault on Dark Athena | Starbreeze/Ogier, 32-bit OpenGL | ReShade x86 как opengl32.dll + Feeder addon32 + host64 + VORT (4K через `VID_MODE=desktop` — движок не умеет 3840×2160 fullscreen) | ✅ работает |
| BloodRayne 2 Terminal Cut | Terminal Cut, 32-bit D3D8→D3D9 (бандл-мост) | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Dark Messiah: Might and Magic | Source Engine, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| DOOM 2016 | id Tech 6, 64-bit Vulkan | глобальный Vulkan-слой ReShade + Feeder addon64 + Lumenite (без host64 — 64-bit путь) | ✅ работает |
| Half-Life 2 | Source Engine, 32-bit D3D11 (dxgi.dll + d3d11.dll динамически) | ReShade x86 dxgi + Feeder addon32 + host64 + Lumenite | ✅ работает |
| DOOM 3 BFG Edition | id Tech 4, 32-bit OpenGL | ReShade x86 как opengl32.dll + Feeder addon32 + host64 + VORT | ✅ работает |
| Mass Effect Legendary Edition (ME1/ME2/ME3) | Unreal Engine 3.5, 64-bit D3D11 | ReShade x64 dxgi + Feeder addon64 + Lumenite (без host64 — 64-bit путь) | ✅ работает |
| Need for Speed: Underground | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Need for Speed: Underground 2 | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Need for Speed: Most Wanted (2005) | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Split/Second | Black Rock Studio, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Race Driver: GRID | Codemasters EGO 1.0, 32-bit D3D9 | DXVK 2.7.1 addon_fix x86 (фикс 4K-краша) + dxvk.conf forceRefreshRate + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Need for Speed: Shift | Slightly Mad Studios, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |
| Need for Speed: ProStreet | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 + host64 + Lumenite | ✅ работает |

Все подтверждены: `feature 18 created`, `inline feature 18 evaluation succeeded`, счётчик NR-кадров растёт (`frame N evaluated` в host64\dlss5-feed-host.log).

## Что нужно

- GPU RTX 50-серии (Neural Rendering только на RTX 50), драйвер 616.56+
- [DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) v0.11.0-beta.2 / v0.12.0 / v0.13.1-beta.1 (addon32/addon64 + host64 из ОДНОГО релиза)
- [renodx-dlss5](https://github.com/RankFTW/rhi-repo) 4.70 (для OpenGL-пути — 4.60: fenced workset pool 4.70 не ресайклится на OpenGL)
- nvngx_dlssnr.dll 310.8.0 + nvngx_dlss.dll / nvngx_dlssg.dll / nvngx_dlssd.dll (310.9.0 / 310.9.0 / 310.9.0)
- ReShade 6.8 addon-сборка (x86 dxgi для 32-bit игр, x64 dxgi для host64)
- DXVK 3.0.2 x86 (d3d9.dll) для Fallout 3 / Black Mesa / Far Cry / BloodRayne 2 / Dark Messiah / серии NFS
- VORT-шейдеры (vortigern11/vort_Shaders) для OpenGL-путей (OpenMW, ioq3, Serious Sam, Jedi Academy, Riddick, DOOM 3 BFG)
- бинарники ioq3 (ioquake3.org) для Quake III Arena

## Установка

Каждый скрипт читает пути из переменных окружения (без захардкоженных личных путей):

```bat
set GAME_DIR=D:\Games\Deus Ex Human Revolution
set FEEDER_DIR=D:\tools\DLSS5-Feeder-0.11.0-beta.2
set RENODX_ADDON=D:\tools\renodx-dlss5.addon64
set RESHADE_X86_DXGI=D:\tools\ReShade-x86\dxgi.dll
set RESHADE_X64_DXGI=D:\tools\ReShade-x64\dxgi.dll
set NVNGX_DIR=D:\tools\nvngx
python scripts\install_dxhr.py
```

Переменные по играм:

- `install_dxhr.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X86_DXGI, RESHADE_X64_DXGI, NVNGX_DIR
- `install_openmw.py` — GAME_DIR (папка OpenMW), FEEDER_DIR, RENODX_ADDON (**4.60!**), RESHADE_X64_DXGI, NVNGX_DIR
- `install_fallout3.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X64_DXGI, NVNGX_DIR, DXVK_D3D9, VULKAN1_X86
- `install_blackmesa.py` — как Fallout 3
- `install_ioq3.py` — GAME_DIR (папка Quake III), IOQ3_SRC (распакованные бинарники ioq3), OPENGL_DONOR (рабочая 64-bit OpenGL-установка, напр. OpenMW)
- `install_serioussam.py` — GAME_DIR (папка Serious Sam, обычно `<игра>\Bin`), OPENGL_DONOR (OpenMW), X86_DONOR (рабочая 32-bit установка, напр. Deus Ex: HR)
- `install_farcry.py` — GAME_DIR (папка Far Cry, обычно `<игра>\Bin32`), DXVK_DONOR (рабочая D3D9-установка, напр. Fallout 3)
- `install_quake3_ja.py` — GAME_DIR_Q3, GAME_DIR_JA (GameData), X86_DONOR (рабочая 32-bit OpenGL-установка, напр. Serious Sam)
- `install_nfs_series.py` — GAME_DIR для каждой NFS, DXVK_DONOR (рабочая D3D9-установка, напр. Fallout 3)

## Грабли (почему это заняло время)

1. **DLSS 5 не чинит примитивную геометрию/текстуры.** Neural Rendering пересчитывает свет на том, что движок уже отрисовал — плоские стены с текстурами 2002 года остаются плоскими. Эффект масштабируется от богатства сцены.
2. **Feeder не понимает D3D9.** D3D9-игры нужно сначала перевести: DXVK (D3D9→Vulkan) — dgVoodoo (D3D9→D3D11) крашит Fallout 3 и Black Mesa (LockVertex/LockIndexBuffer).
3. **Fallout 3: `LoadFromDllMain` ломает регистрацию аддона через Vulkan-слой.** Аддон грузится в DllMain слоя ДО инициализации ReShade-рантайма → «No add-on was registered... Unloading again». Фикс: убрать LoadFromDllMain — аддон подхватывается сканированием папки после инициализации рантайма. (Black Mesa LoadFromDllMain терпит — другой порядок загрузки движка.)
4. **OpenMW (OpenGL): renodx-dlss5 4.70 не работает** — fenced workset pool исчерпывается после 4 кадров (`NR workset pool exhausted; preserving game output`). Ставить 4.60. То же для всех OpenGL-путей (ioq3, Serious Sam, Jedi Academy, Riddick, DOOM 3 BFG).
5. **OpenMW: Lumenite даёт 0% non-zero векторов движения на OpenGL.** Использовать VORT (`DLSS5_MV_PROVIDER=2`), технику `vort_MotionEffects` ПЕРВОЙ в пресете, инклуды в `Shaders/Includes/` (БОЛЬШАЯ буква — препроцессор чувствителен к регистру).
6. **OpenMW: диагностические флаги валят NR.** `reset_every=1` / `rebuild=1` / `warmup_rebuild=180` в dlss5-feed.cfg → NR умирает после нескольких кадров. Держать 0.
7. **Deus Ex: HR — самый простой случай.** 32-bit Daedalus динамически грузит dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi подхватывается вообще без обёрток.
8. **ReShade затирает LoadFromDllMain при выходе** — патчить ini при закрытой игре.
9. **host64/ReShade.ini нужен полный блок тюнинга [RenoDX.DLSS5]** (NRStyle=2, EnableHooks=2, NeuralUplift=1, NREnableUpscaling=0 + preset/intensity/tone) — дефолты слабые.
10. **Quake III (GOG): игра грузит opengl32.dll из system32, игнорируя локальный.** ReShade не загружается вообще (подтверждено модулями процесса). Фикс: ioq3 — он грузит opengl32.dll из своей папки, и весь стек работает из коробки.
11. **Serious Sam: TFE — в меню нет 4K.** Движок перечисляет режимы через EnumDisplaySettings, поэтому 3840×2160 пишется прямо в `Scripts\PersistentSymbols.ini` (sam_iScreenSizeI/J). Внутриигровая опция «Widescreen» — это letterbox, НЕ растяжение — держать sam_bWideScreen=0. Steamify-патч (archive.org) чинит Hor+ FOV. DPI: exe не DPI-aware — ставить HIGHDPIAWARE через AppCompatFlags, иначе картинка смещается.
12. **Serious Sam: ReShade умирает при смене видеорежима** (`game device destroyed; shutting down` — пересоздание GL-контекста убивает стек). Не менять разрешение в меню — выставлять в конфиге до запуска.
13. **Серия NFS: сейвы лежат в неожиданных местах.** UG → `C:\ProgramData\NFS Underground` (файлы профиля `<имя>.ugd`), UG2 → `%LOCALAPPDATA%\NFS Underground 2` (слоты — ПАПКИ `<имя>\<имя>`, `NAME DVD 1\NAME DVD 1`), MW → `Documents\NFS Most Wanted\<имя>\`. Игра при первом запуске создаёт свой профиль — переименовать скачанные сейвы под него.
14. **NFS Underground: разрешение — индекс режима.** `RES: N` в конфиге профиля — индекс в EnumDisplaySettings (0 = 640×480@59, 789 = 3840×2160@60). exe уже пропатчен под 4K (uniws: `mov eax,3840; mov esi,2160`), но игра всё равно стартует в 640×480 — разрешение выбирать в меню игры.
15. **NFS Most Wanted: widescreen-фикс — dinput8.dll + .asi-лоадер.** Встроенный фикс (dinput8.dll + scripts\NFSMW2005_widescreen_fix.asi + nfsmw_res.ini) — 4K пишется туда (ResX/ResY). UG/UG2 — ThirteenAG WidescreenFixesPack (dinput8.dll + scripts\*.asi).

## Проверка

- ReShade.log: `signed DLSSNR 310.8.0 ... runtime initialized`, `feature 18 created`
- host64\dlss5-feed-host.log: `feature ready: 3840x2160 DLAA`, `frame N evaluated`
- В игре: Home → Add-ons → DLSS 5 Neural Rendering → `Successful NR frames` растёт, `Latest NR NGX result: 0x00000000`

## Файлы

- `scripts/` — параметризованные установщики (env vars, без личных путей)
- `configs/` — эталонные ReShade.ini / ReShadePreset.ini / dlss5-feed.cfg по играм
- `OLD-GAMES-GOTCHAS.md` — полные заметки по отладке (RU)
- `OLD-GAMES-GOTCHAS.en.md` — полные заметки по отладке (EN)

## Связанное

- [dlss5-bridge](https://github.com/NIGos/dlss5-bridge) — DLSS 5 в DX11/Vulkan-играх с нативным DLSS; наш фикс глубины R32_SFLOAT для RTX Remix влит в апстрим (PR #21)
- [DLSS5-Video-Converter](https://github.com/perseval-BLR/DLSS5-Video-Converter) — DLSS 5 NR на видео
- [NR-Media-UI](https://github.com/perseval-BLR/NR-Media-UI) — DLSS 5 NR на скриншотах

## Автор

**Perseval** — https://youtube.com/@perseval_BLR
