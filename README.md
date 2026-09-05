# DLSS 5 Neural Rendering in 25 games without native DLSS

Working installs of DLSS 5 Neural Rendering (nvngx_dlssnr.dll 310.8.0) in twenty-five games that shipped without DLSS, tested on RTX 5070 Ti (16 GB) + Ryzen 7 9800X3D, 4K:

| Game | Engine / API | Path | Status |
|---|---|---|---|
| Deus Ex: Human Revolution | Daedalus, 32-bit native D3D11 | ReShade x86 dxgi + DLSS5-Feeder addon32 + host64 + Lumenite | ✅ works |
| The Elder Scrolls III: Morrowind (OpenMW) | OpenMW 0.51, 64-bit OpenGL | ReShade64 as opengl32.dll + Feeder addon64 + VORT motion vectors | ✅ works |
| Fallout 3 | Gamebryo, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + Lumenite | ✅ works |
| Black Mesa | Source 2013, 32-bit D3D9 | DXVK 3.0.2 x86 + global ReShade Vulkan layer + Feeder addon32 + Lumenite | ✅ works |
| Quake III Arena | ioq3, 64-bit OpenGL | ReShade64 as opengl32.dll + Feeder addon64 + VORT (ioq3 required — GOG binary loads system32 opengl32) | ✅ works |
| Serious Sam: The First Encounter | Serious Engine 1, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT | ✅ works |
| Far Cry 2004 | CryEngine 1, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + Lumenite | ✅ works |
| Star Wars Jedi Knight: Jedi Academy | id Tech 3, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT | ✅ works |
| The Chronicles of Riddick: Assault on Dark Athena | Starbreeze/Ogier, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT (4K via `VID_MODE=desktop` — engine can't apply 3840×2160 fullscreen) | ✅ works |
| BloodRayne 2 Terminal Cut | Terminal Cut, 32-bit D3D8→D3D9 (bundled bridge) | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Dark Messiah: Might and Magic | Source Engine, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| DOOM 2016 | id Tech 6, 64-bit Vulkan | global ReShade Vulkan layer + Feeder addon64 + Lumenite (no host64 — 64-bit path) | ✅ works |
| Half-Life 2 | Source Engine, 32-bit D3D11 (dxgi.dll + d3d11.dll dynamic) | ReShade x86 dxgi + Feeder addon32 + host64 + Lumenite | ✅ works |
| DOOM 3 BFG Edition | id Tech 4, 32-bit OpenGL | ReShade x86 as opengl32.dll + Feeder addon32 + host64 + VORT | ✅ works |
| Mass Effect Legendary Edition (ME1/ME2/ME3) | Unreal Engine 3.5, 64-bit D3D11 | ReShade x64 dxgi + Feeder addon64 + Lumenite (no host64 — 64-bit path) | ✅ works |
| Need for Speed: Underground | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Need for Speed: Underground 2 | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Need for Speed: Most Wanted (2005) | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Split/Second | Black Rock Studio, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Race Driver: GRID | Codemasters EGO 1.0, 32-bit D3D9 | DXVK 2.7.1 addon_fix x86 (4K-краш-фикс) + dxvk.conf forceRefreshRate + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Need for Speed: Shift | Slightly Mad Studios, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |
| Need for Speed: ProStreet | EA Black Box, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 + host64 + Lumenite | ✅ works |

All verified: `feature 18 created`, `inline feature 18 evaluation succeeded`, NR frame counter growing (`frame N evaluated` in host64\dlss5-feed-host.log).

## What you need

- RTX 50-series GPU (Neural Rendering is RTX 50-only), driver 616.56+
- [DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) v0.11.0-beta.2 / v0.12.0 / v0.13.1-beta.1 (addon32/addon64 + host64 from the SAME release)
- [renodx-dlss5](https://github.com/RankFTW/rhi-repo) 4.70 (4.60 for the OpenGL path — 4.70's fenced workset pool does not recycle on OpenGL)
- nvngx_dlssnr.dll 310.8.0 + nvngx_dlss.dll / nvngx_dlssg.dll / nvngx_dlssd.dll (310.9.0 / 310.9.0 / 310.9.0)
- ReShade 6.8 addon build (x86 dxgi for 32-bit games, x64 dxgi for host64)
- DXVK 3.0.2 x86 (d3d9.dll) for Fallout 3 / Black Mesa / Far Cry / BloodRayne 2 / Dark Messiah / NFS series / Split/Second / Shift / ProStreet
- DXVK 2.7.1 addon_fix (xatornet/GridGogger) for Race Driver: GRID — fixes the 4K crash on high-refresh monitors; pair with dxvk.conf `d3d9.forceRefreshRate = <Hz>`
- VORT shaders (vortigern11/vort_Shaders) for the OpenGL paths (OpenMW, ioq3, Serious Sam, Jedi Academy, Riddick, DOOM 3 BFG)
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
- `install_nfs_series.py` — GAME_DIR per NFS game, DXVK_DONOR (working D3D9 install, e.g. Fallout 3)

## The gotchas (why this took a while)

1. **DLSS 5 does not fix primitive geometry/textures.** Neural Rendering recomputes lighting on what the engine already renders — flat walls with 2002 textures stay flat. The effect scales with scene richness.
2. **The Feeder does not understand D3D9.** D3D9 games must be translated first: DXVK (D3D9→Vulkan) — dgVoodoo (D3D9→D3D11) crashes Fallout 3 and Black Mesa (LockVertex/LockIndexBuffer).
3. **Fallout 3: `LoadFromDllMain` breaks add-on registration through the Vulkan layer.** The add-on loads in the layer's DllMain before the ReShade runtime initializes → "No add-on was registered... Unloading again". Fix: remove LoadFromDllMain, the add-on is picked up by folder scanning after runtime init. (Black Mesa tolerates LoadFromDllMain — different engine load order.)
4. **OpenMW (OpenGL): renodx-dlss5 4.70 does not work** — fenced workset pool exhausts after 4 frames (`NR workset pool exhausted; preserving game output`). Use 4.60. Same for all OpenGL paths (ioq3, Serious Sam, Jedi Academy, Riddick, DOOM 3 BFG).
5. **OpenMW: Lumenite gives 0% non-zero motion vectors on OpenGL.** Use VORT (`DLSS5_MV_PROVIDER=2`), technique `vort_MotionEffects` FIRST in the preset, includes into `Shaders/Includes/` (capital I — the preprocessor is case-sensitive).
6. **OpenMW: diagnostic flags kill NR.** `reset_every=1` / `rebuild=1` / `warmup_rebuild=180` in dlss5-feed.cfg → NR dies after a few frames. Keep them 0.
7. **Deus Ex: HR is the easy one.** 32-bit Daedalus engine dynamically loads dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi is picked up with no wrappers at all.
8. **ReShade overwrites LoadFromDllMain on exit** — patch ini files with the game closed.
9. **host64/ReShade.ini needs the full [RenoDX.DLSS5] tuning block** (NRStyle=2, EnableHooks=2, NeuralUplift=1, NREnableUpscaling=0 + preset/intensity/tone values) — defaults are weak.
10. **Quake III (GOG): the game loads opengl32.dll from system32, ignoring the local one.** ReShade never loads (verified via process modules). Fix: use ioq3 — it loads opengl32.dll from its own folder and the whole stack works out of the box.
11. **Serious Sam: TFE has no 4K in the menu.** The engine enumerates modes via EnumDisplaySettings, so 3840×2160 goes straight into `Scripts\PersistentSymbols.ini` (sam_iScreenSizeI/J). The in-game "Widescreen" option is a letterbox, NOT stretching — keep sam_bWideScreen=0. Steamify patch (archive.org) fixes the Hor+ FOV. DPI: the exe is not DPI-aware — set HIGHDPIAWARE via AppCompatFlags or the image shifts.
12. **Serious Sam: ReShade dies on video mode change** (`game device destroyed; shutting down` — GL context recreation kills the stack). Don't change resolution in the menu; set it in the config before launch.
13. **NFS series: saves live in unexpected places.** UG → `C:\ProgramData\NFS Underground` (profile files `<name>.ugd`), UG2 → `%LOCALAPPDATA%\NFS Underground 2` (slots are FOLDERS `<name>\<name>`, `NAME DVD 1\NAME DVD 1`), MW → `Documents\NFS Most Wanted\<name>\`. The game creates its own profile on first launch — rename the downloaded saves to match it.
14. **NFS Underground: resolution is a mode index.** `RES: N` in the profile cfg is an index into EnumDisplaySettings (0 = 640×480@59, 789 = 3840×2160@60). The exe is already patched for 4K (uniws patch: `mov eax,3840; mov esi,2160`), but the game still starts at 640×480 — pick the resolution in the in-game options menu.
15. **NFS Most Wanted: widescreen fix is a dinput8.dll + .asi loader.** The bundled fix (dinput8.dll + scripts\NFSMW2005_widescreen_fix.asi + nfsmw_res.ini) sets `ResX/ResY` — 3840×2160 goes there. UG/UG2 use ThirteenAG WidescreenFixesPack (dinput8.dll + scripts\*.asi).

## Verify

- ReShade.log: `signed DLSSNR 310.8.0 ... runtime initialized`, `feature 18 created`
- host64\dlss5-feed-host.log: `feature ready: 3840x2160 DLAA`, `frame N evaluated`
- In-game: Home → Add-ons → DLSS 5 Neural Rendering → `Successful NR frames` growing, `Latest NR NGX result: 0x00000000`

## Files

- `scripts/` — parametrized installers (env vars, no personal paths)
- `configs/` — reference ReShade.ini / ReShadePreset.ini / dlss5-feed.cfg per game
- `OLD-GAMES-GOTCHAS.md` — full troubleshooting notes (RU)
- `OLD-GAMES-GOTCHAS.en.md` — full troubleshooting notes (EN)

## Related

- [dlss5-bridge](https://github.com/NIGos/dlss5-bridge) — DLSS 5 in DX11/Vulkan games with native DLSS; our R32_SFLOAT depth fix for RTX Remix games is merged upstream (PR #21)
- [DLSS5-Video-Converter](https://github.com/perseval-BLR/DLSS5-Video-Converter) — run DLSS 5 NR on videos
- [NR-Media-UI](https://github.com/perseval-BLR/NR-Media-UI) — run DLSS 5 NR on screenshots

## Author

**Perseval** — https://youtube.com/@perseval_BLR
