# DLSS 5 Neural Rendering in 13 classic games

Working installs of DLSS 5 Neural Rendering (nvngx_dlssnr.dll 310.8.0) in thirteen classic games, tested on RTX 5070 Ti (16 GB) + Ryzen 7 9800X3D, 4K:

| Game | Engine / API | Path | Status |
|---|---|---|---|
| Deus Ex: Human Revolution | Daedalus, 32-bit native D3D11 | ReShade x86 dxgi + DLSS5-Feeder addon32 + host64 | ✅ works |
| The Elder Scrolls III: Morrowind (OpenMW) | OpenMW 0.51, 64-bit OpenGL | ReShade64 as opengl32.dll + Feeder addon64 + VORT motion vectors | ✅ works |
| Fallout 3 | Gamebryo, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 | ✅ works |
| Black Mesa | Source 2013, 32-bit D3D9 | DXVK 3.0.2 x86 + global ReShade Vulkan layer + Feeder addon32 | ✅ works |
| Quake III Arena | ioq3, 64-bit OpenGL | ReShade64 as opengl32.dll + Feeder addon64 + VORT (ioq3 required — GOG binary loads system32 opengl32) | ✅ works |
| Serious Sam: The First Encounter | Serious Engine 1, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT | ✅ works |
| Far Cry 2004 | CryEngine 1, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 | ✅ works |
| Star Wars Jedi Knight: Jedi Academy | id Tech 3, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT | ✅ works |
| The Chronicles of Riddick: Assault on Dark Athena | Starbreeze/Ogier, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT (4K via `VID_MODE=desktop` — engine can't apply 3840×2160 fullscreen) | ✅ works |
| BloodRayne 2 Terminal Cut | Terminal Cut, 32-bit D3D8→D3D9 (bundled bridge) | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Dark Messiah: Might and Magic | Source Engine, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| DOOM 2016 | id Tech 6, 64-bit Vulkan | global ReShade Vulkan layer + Feeder addon64 + Lumenite (no host64 — 64-bit path) | ✅ works |
| Half-Life 2 | Source Engine, 32-bit D3D9 | dgVoodoo2 (D3D9→D3D11) + ReShade x86 dxgi + Feeder addon32 + host64 + Lumenite | ⚠️ installed, NR not verified (cfg was mode=1) |

Twelve of thirteen verified: `feature 18 created`, `inline feature 18 evaluation succeeded`, NR frame counter growing. HL2 is installed but its last session ran in transport-only mode (`mode=1` — no NGX evaluate); fix `mode=2` in dlss5-feed.cfg and re-verify.

## What you need

- RTX 50-series GPU (Neural Rendering is RTX 50-only), driver 616.56+
- [DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) v0.11.0-beta.2 / v0.12.0 (addon32/addon64 + host64 from the SAME release)
- [renodx-dlss5](https://github.com/RankFTW/rhi-repo) 4.70 (4.60 for the OpenGL path — 4.70's fenced workset pool does not recycle on OpenGL)
- nvngx_dlssnr.dll 310.8.0 + nvngx_dlss.dll / nvngx_dlssg.dll / nvngx_dlssd.dll (310.8.0 / 310.7.129)
- ReShade 6.8 addon build (x86 dxgi for 32-bit games, x64 dxgi for host64)
- DXVK 3.0.2 x86 (d3d9.dll) for Fallout 3 / Black Mesa / Far Cry / BloodRayne 2 / Dark Messiah
- dgVoodoo2 (D3D9.dll) for Half-Life 2 (D3D9→D3D11 path)
- VORT shaders (vortigern11/vort_Shaders) for the OpenGL paths (OpenMW, ioq3, Serious Sam, Jedi Academy, Riddick)
- ioq3 binaries (ioquake3.org) for Quake III Arena

## Install

Each script reads paths from environment variables (no hardcoded personal paths):

```bat
set GAME_DIR=D:\Games\Deus Ex Human Revolution
set FEEDER_DIR=D:\tools\DLSS5-Feeder-0.11.0-beta.2
set RENODX_ADDON=D:\tools\renodx-dlss5.addon64
set RESHADE_X86_DXGI=D:\tools\ReShade-x86\dxgi.dll
set RESHADE_X64_DXGI=D:\tools\ReShade-x64\dxgi.dll
set NVNGX_DIR=D:\tools\nvngx
python scripts\install_dxhr.py
```

Per-game variables:

- `install_dxhr.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X86_DXGI, RESHADE_X64_DXGI, NVNGX_DIR
- `install_openmw.py` — GAME_DIR (OpenMW folder), FEEDER_DIR, RENODX_ADDON (**4.60!**), RESHADE_X64_DXGI, NVNGX_DIR
- `install_fallout3.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X64_DXGI, NVNGX_DIR, DXVK_D3D9, VULKAN1_X86
- `install_blackmesa.py` — same as Fallout 3
- `install_ioq3.py` — GAME_DIR (Quake III folder), IOQ3_SRC (unpacked ioq3 binaries), OPENGL_DONOR (working 64-bit OpenGL install, e.g. OpenMW)
- `install_serioussam.py` — GAME_DIR (Serious Sam folder, usually `<game>\Bin`), OPENGL_DONOR (OpenMW), X86_DONOR (working 32-bit install, e.g. Deus Ex: HR)
- `install_farcry.py` — GAME_DIR (Far Cry folder, usually `<game>\Bin32`), DXVK_DONOR (working D3D9 install, e.g. Fallout 3)
- `install_quake3_ja.py` — GAME_DIR_Q3, GAME_DIR_JA (GameData), X86_DONOR (working 32-bit OpenGL install, e.g. Serious Sam)
- `install_riddick.py` — GAME_DIR (Riddick `System\Win32_x86` folder), X86_DONOR (working 32-bit OpenGL install, e.g. Serious Sam)
- `install_bloodrayne2.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X64_DXGI, NVNGX_DIR, DXVK_D3D9
- `install_darkmessiah.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X64_DXGI, NVNGX_DIR, DXVK_D3D9
- `install_doom2016.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, NVNGX_DIR (64-bit path, no host64)
- `install_hl2.py` — GAME_DIR, FEEDER_DIR, RENODX_ADDON, RESHADE_X86_DXGI, RESHADE_X64_DXGI, NVNGX_DIR, DGVOODOO_D3D9

## The gotchas (why this took a while)

1. **DLSS 5 does not fix primitive geometry/textures.** Neural Rendering recomputes lighting on what the engine already renders — flat walls with 2002 textures stay flat. The effect scales with scene richness.
2. **The Feeder does not understand D3D9.** D3D9 games must be translated first: DXVK (D3D9→Vulkan) — dgVoodoo (D3D9→D3D11) crashes Fallout 3 and Black Mesa (LockVertex/LockIndexBuffer).
3. **Fallout 3: `LoadFromDllMain` breaks add-on registration through the Vulkan layer.** The add-on loads in the layer's DllMain before the ReShade runtime initializes → "No add-on was registered... Unloading again". Fix: remove LoadFromDllMain, the add-on is picked up by folder scanning after runtime init. (Black Mesa tolerates LoadFromDllMain — different engine load order.)
4. **OpenMW (OpenGL): renodx-dlss5 4.70 does not work** — fenced workset pool exhausts after 4 frames (`NR workset pool exhausted; preserving game output`). Use 4.60. Same for all OpenGL paths (ioq3, Serious Sam, Jedi Academy).
5. **OpenMW: Lumenite gives 0% non-zero motion vectors on OpenGL.** Use VORT (`DLSS5_MV_PROVIDER=2`), technique `vort_MotionEffects` FIRST in the preset, includes into `Shaders/Includes/` (capital I — the preprocessor is case-sensitive).
6. **OpenMW: diagnostic flags kill NR.** `reset_every=1` / `rebuild=1` / `warmup_rebuild=180` in dlss5-feed.cfg → NR dies after a few frames. Keep them 0.
7. **Deus Ex: HR is the easy one.** 32-bit Daedalus engine dynamically loads dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi is picked up with no wrappers at all.
8. **ReShade overwrites LoadFromDllMain on exit** — patch ini files with the game closed.
9. **host64/ReShade.ini needs the full [RenoDX.DLSS5] tuning block** (NRStyle=2, EnableHooks=2, NeuralUplift=1, NREnableUpscaling=0 + preset/intensity/tone values) — defaults are weak.
10. **Quake III (GOG): the game loads opengl32.dll from system32, ignoring the local one.** ReShade never loads (verified via process modules). Fix: use ioq3 — it loads opengl32.dll from its own folder and the whole stack works out of the box.
11. **Serious Sam: TFE has no 4K in the menu.** The engine enumerates modes via EnumDisplaySettings, so 3840×2160 goes straight into `Scripts\PersistentSymbols.ini` (sam_iScreenSizeI/J). The in-game "Widescreen" option is a letterbox, NOT stretching — keep sam_bWideScreen=0. Steamify patch (archive.org) fixes the Hor+ FOV. DPI: the exe is not DPI-aware — set HIGHDPIAWARE via AppCompatFlags or the image shifts.
12. **Serious Sam: ReShade dies on video mode change** (`game device destroyed; shutting down` — GL context recreation kills the stack). Don't change resolution in the menu; set it in the config before launch.
13. **Riddick: AODA — 4K only via `VID_MODE=desktop` in `%LOCALAPPDATA%\Atari\The Chronicles of Riddick - Assault on Dark Athena\Environment.cfg`.** Starting with `VID_MODE=3840 2160 32 144` = black ~1600×1024 window + silent exit (the engine can't find the exact mode and falls back). The in-game menu applies 4K but the engine silently loads the closest supported mode — the picture stays non-4K. `VID_DWIDTH/VID_DHEIGHT=3840/2160`; windowed 4K renders 3840×2071 (title bar). Also: startup hang on modern NVIDIA is the GLSL bias syntax in `System\GL\HLInclude_GLSL.xrg` (see OLD-GAMES-GOTCHAS.md §16).
14. **Riddick/32-bit schemes: `NRStyle=2` in host64/ReShade.ini → black screen when the feed engages.** The 32-bit host64 path needs `NRStyle=0` (the §9 tuning block with NRStyle=2 is for 64-bit schemes).
15. **HL2: `mode=1` in dlss5-feed.cfg = transport-only, no NGX.** host64 log shows `transport-only mode: Color will be copied to Output, no evaluate` and `feature 18` never appears. Fix: `mode=2` + `mv_scale_x/y=1.000` (was 0.000). Verify in host64\dlss5-feed-host.log.
16. **BloodRayne 2: the bundled `d3d8.dll` (279 KB) is a D3D8→D3D9 bridge** — it imports d3d9.dll, so our DXVK `D3D9.dll` is picked up without touching d3d8. Don't replace d3d8.dll.
17. **DOOM 2016 (64-bit Vulkan): no host64 needed** — the addon64 creates its own D3D12 device. `LoadFromDllMain=renodx-dlss5.addon64` works (global layer path). Keep Feeder v0.11.0-beta.2 — v0.13.1-beta.1 regresses (CreateFeature 0xC0000005).

## Verify

- ReShade.log: `signed DLSSNR 310.8.0 ... runtime initialized`, `feature 18 created`
- host64\dlss5-feed-host.log: `feature ready: 3840x2160 DLAA`, `frame N evaluated`
- In-game: Home → Add-ons → DLSS 5 Neural Rendering → `Successful NR frames` growing, `Latest NR NGX result: 0x00000000`

## Files

- `scripts/` — parametrized installers (env vars, no personal paths)
- `configs/` — reference ReShade.ini / ReShadePreset.ini / dlss5-feed.cfg per game
- `OLD-GAMES-GOTCHAS.md` — full troubleshooting notes (RU)

## Related

- [dlss5-bridge](https://github.com/NIGos/dlss5-bridge) — DLSS 5 in DX11/Vulkan games with native DLSS; our R32_SFLOAT depth fix for RTX Remix games is merged upstream (PR #21)
- [DLSS5-Video-Converter](https://github.com/perseval-BLR/DLSS5-Video-Converter) — run DLSS 5 NR on videos
- [NR-Media-UI](https://github.com/perseval-BLR/NR-Media-UI) — run DLSS 5 NR on screenshots

## Author

**Perseval** — https://youtube.com/@perseval_BLR
