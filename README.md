# DLSS 5 Neural Rendering in 4 classic games

Working installs of DLSS 5 Neural Rendering (nvngx_dlssnr.dll 310.8.0) in four classic games, tested on RTX 5070 Ti (16 GB) + Ryzen 7 9800X3D, 4K:

| Game | Engine / API | Path | Status |
|---|---|---|---|
| Deus Ex: Human Revolution | Daedalus, 32-bit native D3D11 | ReShade x86 dxgi + DLSS5-Feeder addon32 + host64 | ✅ works |
| The Elder Scrolls III: Morrowind (OpenMW) | OpenMW 0.51, 64-bit OpenGL | ReShade64 as opengl32.dll + Feeder addon64 + VORT motion vectors | ✅ works |
| Fallout 3 | Gamebryo, 32-bit D3D9 | DXVK 3.0.2 x86 (D3D9→Vulkan) + global ReShade Vulkan layer + Feeder addon32 | ✅ works |
| Black Mesa | Source 2013, 32-bit D3D9 | DXVK 3.0.2 x86 + global ReShade Vulkan layer + Feeder addon32 | ✅ works |

All four run DLSS 5 Neural Rendering at native 4K (DLAA contract, no upscaling — the Feeder sees the final frame). Verified: `feature 18 created`, `inline feature 18 evaluation succeeded`, NR frame counter growing.

## What you need

- RTX 50-series GPU (Neural Rendering is RTX 50-only), driver 616.56+
- [DLSS5-Feeder](https://github.com/jlrouzies-fr/DLSS5-Feeder) v0.11.0-beta.2 (addon32/addon64 + host64 from the SAME release)
- [renodx-dlss5](https://github.com/RankFTW/rhi-repo) 4.70 (4.60 for the OpenGL path — 4.70's fenced workset pool does not recycle on OpenGL)
- nvngx_dlssnr.dll 310.8.0 + nvngx_dlss.dll / nvngx_dlssg.dll / nvngx_dlssd.dll (310.8.0 / 310.7.129)
- ReShade 6.8 addon build (x86 dxgi for 32-bit games, x64 dxgi for host64)
- DXVK 3.0.2 x86 (d3d9.dll) for Fallout 3 / Black Mesa
- VORT shaders (vortigern11/vort_Shaders) for the OpenMW OpenGL path

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

## The gotchas (why this took a while)

1. **DLSS 5 does not fix primitive geometry/textures.** Neural Rendering recomputes lighting on what the engine already renders — flat walls with 2002 textures stay flat. The effect scales with scene richness.
2. **The Feeder does not understand D3D9.** D3D9 games must be translated first: DXVK (D3D9→Vulkan) — dgVoodoo (D3D9→D3D11) crashes Fallout 3 and Black Mesa (LockVertex/LockIndexBuffer).
3. **Fallout 3: `LoadFromDllMain` breaks add-on registration through the Vulkan layer.** The add-on loads in the layer's DllMain before the ReShade runtime initializes → "No add-on was registered... Unloading again". Fix: remove LoadFromDllMain, the add-on is picked up by folder scanning after runtime init. (Black Mesa tolerates LoadFromDllMain — different engine load order.)
4. **OpenMW (OpenGL): renodx-dlss5 4.70 does not work** — fenced workset pool exhausts after 4 frames (`NR workset pool exhausted; preserving game output`). Use 4.60.
5. **OpenMW: Lumenite gives 0% non-zero motion vectors on OpenGL.** Use VORT (`DLSS5_MV_PROVIDER=2`), technique `vort_MotionEffects` FIRST in the preset, includes into `Shaders/Includes/` (capital I — the preprocessor is case-sensitive).
6. **OpenMW: diagnostic flags kill NR.** `reset_every=1` / `rebuild=1` / `warmup_rebuild=180` in dlss5-feed.cfg → NR dies after a few frames. Keep them 0.
7. **Deus Ex: HR is the easy one.** 32-bit Daedalus engine dynamically loads dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi is picked up with no wrappers at all.
8. **ReShade overwrites LoadFromDllMain on exit** — patch ini files with the game closed.
9. **host64/ReShade.ini needs the full [RenoDX.DLSS5] tuning block** (NRStyle=2, EnableHooks=2, NeuralUplift=1, NREnableUpscaling=0 + preset/intensity/tone values) — defaults are weak.

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
