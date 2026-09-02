# DLSS 5 Neural Rendering в 4 классических играх

Рабочие установки DLSS 5 Neural Rendering (nvngx_dlssnr.dll 310.8.0) в четырёх классических играх, проверено на RTX 5070 Ti (16 GB) + Ryzen 7 9800X3D, 4K:

| Игра | Движок / API | Схема | Статус |
|---|---|---|---|
| Deus Ex: Human Revolution | Daedalus, 32-bit нативный D3D11 | ReShade x86 dxgi + DLSS5-Feeder addon32 + host64 | ✅ работает |
| The Elder Scrolls III: Morrowind (OpenMW) | OpenMW 0.51, 64-bit OpenGL | ReShade64 как opengl32.dll + Feeder addon64 + VORT (векторы движения) | ✅ работает |
| Fallout 3 | Gamebryo, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + глобальный Vulkan-слой ReShade + Feeder addon32 | ✅ работает |
| Black Mesa | Source 2013, 32-bit D3D9 | DXVK 3.0.2 x86 + глобальный Vulkan-слой ReShade + Feeder addon32 | ✅ работает |

Все четыре запускают DLSS 5 Neural Rendering в нативном 4K (DLAA-контракт, без апскейла — Feeder видит финальный кадр). Подтверждено: `feature 18 created`, `inline feature 18 evaluation succeeded`, счётчик NR-кадров растёт.

## Что нужно

- GPU RTX 50-серии (Neural Rendering только на RTX 50), драйвер 616.56+
- [DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) v0.11.0-beta.2 (addon32/addon64 + host64 из ОДНОГО релиза)
- [renodx-dlss5](https://github.com/RankFTW/rhi-repo) 4.70 (для OpenGL-пути — 4.60: fenced workset pool 4.70 не ресайклится на OpenGL)
- nvngx_dlssnr.dll 310.8.0 + nvngx_dlss.dll / nvngx_dlssg.dll / nvngx_dlssd.dll (310.8.0 / 310.7.129)
- ReShade 6.8 addon-сборка (x86 dxgi для 32-bit игр, x64 dxgi для host64)
- DXVK 3.0.2 x86 (d3d9.dll) для Fallout 3 / Black Mesa
- VORT-шейдеры (vortigern11/vort_Shaders) для OpenGL-пути OpenMW

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

## Грабли (почему это заняло время)

1. **DLSS 5 не чинит примитивную геометрию/текстуры.** Neural Rendering пересчитывает свет на том, что движок уже отрисовал — плоские стены с текстурами 2002 года остаются плоскими. Эффект масштабируется от богатства сцены.
2. **Feeder не понимает D3D9.** D3D9-игры нужно сначала перевести: DXVK (D3D9→Vulkan) — dgVoodoo (D3D9→D3D11) крашит Fallout 3 и Black Mesa (LockVertex/LockIndexBuffer).
3. **Fallout 3: `LoadFromDllMain` ломает регистрацию аддона через Vulkan-слой.** Аддон грузится в DllMain слоя ДО инициализации ReShade-рантайма → «No add-on was registered... Unloading again». Фикс: убрать LoadFromDllMain — аддон подхватывается сканированием папки после инициализации рантайма. (Black Mesa LoadFromDllMain терпит — другой порядок загрузки движка.)
4. **OpenMW (OpenGL): renodx-dlss5 4.70 не работает** — fenced workset pool исчерпывается после 4 кадров (`NR workset pool exhausted; preserving game output`). Ставить 4.60.
5. **OpenMW: Lumenite даёт 0% non-zero векторов движения на OpenGL.** Использовать VORT (`DLSS5_MV_PROVIDER=2`), технику `vort_MotionEffects` ПЕРВОЙ в пресете, инклуды в `Shaders/Includes/` (БОЛЬШАЯ буква — препроцессор чувствителен к регистру).
6. **OpenMW: диагностические флаги валят NR.** `reset_every=1` / `rebuild=1` / `warmup_rebuild=180` в dlss5-feed.cfg → NR умирает после нескольких кадров. Держать 0.
7. **Deus Ex: HR — самый простой случай.** 32-bit Daedalus динамически грузит dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi подхватывается вообще без обёрток.
8. **ReShade затирает LoadFromDllMain при выходе** — патчить ini при закрытой игре.
9. **host64/ReShade.ini нужен полный блок тюнинга [RenoDX.DLSS5]** (NRStyle=2, EnableHooks=2, NeuralUplift=1, NREnableUpscaling=0 + preset/intensity/tone) — дефолты слабые.

## Проверка

- ReShade.log: `signed DLSSNR 310.8.0 ... runtime initialized`, `feature 18 created`
- host64\dlss5-feed-host.log: `feature ready: 3840x2160 DLAA`, `frame N evaluated`
- В игре: Home → Add-ons → DLSS 5 Neural Rendering → `Successful NR frames` растёт, `Latest NR NGX result: 0x00000000`

## Файлы

- `scripts/` — параметризованные установщики (env vars, без личных путей)
- `configs/` — эталонные ReShade.ini / ReShadePreset.ini / dlss5-feed.cfg по играм
- `OLD-GAMES-GOTCHAS.md` — полные заметки по отладке (RU)

## Связанное

- [dlss5-bridge](https://github.com/NIGos/dlss5-bridge) — DLSS 5 в DX11/Vulkan-играх с нативным DLSS; наш фикс глубины R32_SFLOAT для RTX Remix влит в апстрим (PR #21)
- [DLSS5-Video-Converter](https://github.com/perseval-BLR/DLSS5-Video-Converter) — DLSS 5 NR на видео
- [NR-Media-UI](https://github.com/perseval-BLR/NR-Media-UI) — DLSS 5 NR на скриншотах
