# DLSS 5 in old games — the non-obvious (troubleshooting cheat sheet)

Collected from HL2 RTX, Painkiller, F.E.A.R, Max Payne 2 and the classic-games series (2026-09).
The obvious stuff (install ReShade, feed, host64) is not here. These are the gotchas that cost hours.

## 1. How ReShade actually loads into a wrapped game
- The game does **not import** `dxgi.dll`. ReShade-dxgi gets picked up like this: dgVoodoo/DXVK (or the system d3d9 on WDDM) **loads `dxgi.dll` by name itself** when creating a D3D11 device → the exe-folder search finds ReShade before System32. Nothing in the files contains the string `dxgi.dll` — that is normal.
- Therefore: **no D3D11/DXGI output → ReShade-dxgi never loads.** Check not "is dxgi present" but "is a D3D11 device created".

## 2. DLL base-name collision (the main trap)
- Windows loader rule: **if a module named `d3d9.dll` is already loaded, any later import of `d3d9.dll` binds to it**, regardless of path.
- Many old games do a "DX9 check" at startup and load the **system** `d3d9.dll` first. Then `d3d8to9`/the engine imports `d3d9.dll` → binds to the **system** one, and the folder dgVoodoo/DXVK d3d9 is **silently ignored** (even if it sits right there).
- Symptom: the game runs, but the wrapper "seems not connected" (no dgVoodoo watermark, ReShade not loading). Deleting the folder d3d9 changes nothing.

## 3. dgVoodoo: the `MS\` folder is dgVoodoo WRAPPERS, not Microsoft
- `dgvoodoo2\MS\x86\D3D8.dll`, `D3D9.dll` are **dgVoodoo wrappers** (FileDescription "dgVoodoo … Direct3D8/9"), built for DXGI/D3D11 output. NOT Microsoft originals. Easy to confuse and draw the wrong conclusion.
- Identify a DLL by `(Get-Item x).VersionInfo.FileDescription/CompanyName`, not by name/size/md5.

## 4. Some games reject the wrapper's virtual adapter
- **Max Payne 2**: "requires a Microsoft DirectX 9.0 compatible display adapter". The gate checks the **real** DX9 adapter and **rejects** both dgVoodoo (virtual card `internal3D`) and DXVK. Only `crosire d3d8to9 → system d3d9` (real GPU) passes.
- Gate vs other trouble: the gate shows an **explicit game dialog**; crash/incompatibility is a **silent exit**.
- dgVoodooCpl "select GPU" does NOT fix this on a single GPU — the gate still sees the virtual card.

## 5. ReShade can CRASH the engine (not just "not load")
- MP2: ReShade 6.8.0.2156 crashes `0xc0000409` (stack-buffer-overrun) at `IDirect3D9::CreateDevice`, **same offset for any load path** (d3d9 proxy and Vulkan layer). The same ReShade build does not crash in F.E.A.R — **because that runtime is D3D11**.
- Conclusion: **ReShade on a D3D9 runtime is far more fragile than on D3D11.** The same crash offset across paths = the GS-failure reporter address, not the real overflow site.
- Crash diagnosis — **Windows Event Log, Application, Id 1000**: gives faulting module + exception code + offset. Indispensable for "silent exits".

## 6. Feed does NOT do D3D9
- DLSS5-Feeder supports **D3D11, OpenGL, Vulkan (DXVK)** — D3D9 is not in the list. An old D3D8/D3D9 game **must** first be translated to D3D11 (dgVoodoo) or Vulkan (DXVK). A pure D3D9 runtime is useless for feed.
- Hence the "impossible" MP2 combination: the gate only allows D3D9, feed requires non-D3D9, and ReShade crashes on D3D9. Three mutually exclusive barriers → the game is unsolvable with this tooling.

## 7. Feed versions and the consumer
- Feed halves must match: `dlss5-feed.addon32` **and** `host64\dlss5-feed-host64.exe` from the SAME release (protocol v4→v5 changed; mixed halves silently fail to start).
- The neural consumer in `host64\` is **`renodx-dlss5.addon64`** (with "5") or `deep-fried-chicken.addon64`. **`renodx-dlss.addon64` (without "5") is the old DLSS upscaler, not NR** — feed will not accept it.
- `Deep Fried Chicken` on 32-bit Vulkan (DXVK) is **untested** per docs; for DXVK use `renodx-dlss5` as the consumer.
- The feed release ships **`Verify-DLSS5Feeder.ps1`** — run it next to the exe, it gives the author's checklist (API, ReShade version, MV provider, consumer).
- Feed = only **DLAA (1:1)**, not upscaling: it sees the already-final screen-sized frame. `NREnableUpscaling=0`.

## 8. ReShade Vulkan layer — machine-wide, auto-loads
- `C:\ProgramData\ReShade\ReShade32.json`/`ReShade64.json` in HKLM ImplicitLayers (+ WOW6432Node) load into **any** Vulkan app. For a DXVK game ReShade injects itself; no separate install needed.
- Stock ProgramData-ReShade **crashes Remix and some games** — silence per-process: `set DISABLE_VK_LAYER_reshade_1=1`. An isolated layer of your own — via `enable_environment` (e.g. `ENABLE_VK_LAYER_reshade_pk=1`).

## 9. The 32-bit Vulkan ICD is registered NOT where you expect
- NVIDIA registers the Vulkan ICD in the **display adapter** key: `HKLM\SYSTEM\...\Class\{4d36e968-...}\0000\VulkanDriverName` (64-bit) and **`VulkanDriverNameWow`** (32-bit) → path to `nv-vk64/32.json` in DriverStore.
- The classic key `HKLM\SOFTWARE\[WOW6432Node\]Khronos\Vulkan\Drivers` may be **absent** — that does NOT mean there is no ICD. Don't conclude "32-bit Vulkan is broken" from it alone.

## 10. DXVK d3d8 is raw
- For a D3D8 game prefer `crosire d3d8to9` (D3D8→D3D9) + DXVK/dgVoodoo on D3D9→(Vulkan/D3D11) over DXVK-d3d8 directly (DXVK d3d8 support is experimental; in MP2 it did not even create its own log).

## Quick diagnostics (order)
1. Does the game start? No → Windows log Id 1000 (faulting module) — crash or gate.
2. Is the wrapper active? → dgVoodoo watermark / DXVK log `GAME_d3d9.log` / is there a D3D11 device.
3. Does ReShade load? → `ReShade.log` is created; if crash — see §5.
4. Does feed attach? → `dlss5-feed.log` line 1 (version) + complaints about host64/consumer.
5. Is NR running? → `host64\dlss5-feed-host.log`, "600 frames / MV probe / Depth probe".

## MP2 verdict (the "impossible" case)
Gate → only real d3d9 (D3D9). Feed → non-D3D9. ReShade → crashes on D3D9. Three incompatible requirements. Left playable on `crosire d3d8to9` without injection.

## 11. OpenMW (Morrowind ReBuild) — Feeder OpenGL path (works, 02.09)
- **Scheme**: `opengl32.dll` = ReShade64 (same binary, the name defines the API) + `dlss5-feed.addon64` 0.11.0-beta.2 + `renodx-dlss5.addon64` + full nvngx pack + VORT. OpenMW 0.51.0, 64-bit, OpenGL 4.6, no Vulkan strings in exe.
- **renodx-dlss5 4.70 DOES NOT WORK on the OpenGL transport**: the fenced workset pool (new in 4.7) does not recycle → exactly 4 successful NR frames (`NR workset pool exhausted; preserving game output`), then STANDBY/FAILED. **Use 4.60** (no fenced pool).
- **VORT instead of Lumenite**: Lumenite gives 0% non-zero MV on the OpenGL path. VORT: `DLSS5_MV_PROVIDER=2`, includes go into `Shaders/Includes/` (capital I — the preprocessor is case-sensitive; Lumenite uses `include/`), technique `vort_MotionEffects` FIRST in `Techniques=` (above DLSS5_Feed).
- **dlss5-feed.cfg**: `reset_every=0`, `rebuild=0`, `warmup_rebuild=0` (diagnostic 1/2/180 kill NR).
- **ReShade overwrites LoadFromDllMain** (NUL separator) on exit — patch with the game closed.
- **MV probe 0% non-zero with a static camera is normal** (VORT honestly counts zeros); check while moving.
- **Saves**: openmw-essimporter does NOT convert .ess (unknown record REGN/CONT — incomplete); only native .omwsave. User data dir = game root, saves in `saves/`.

## 12. Fallout 3 (ReBuild) — Gamebryo 32-bit D3D9, DXVK path (works, 02.09)
- **dgVoodoo does NOT work** (the game exits cleanly after ~1.2 s, no crash in the log — control test without our files: clean game runs). Only **DXVK 3.0.2 x86** (like Black Mesa).
- **Scheme**: `D3D9.dll` = DXVK + ReShade via the **global layer** (`C:\ProgramData\ReShade\ReShade32.dll`) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 4.70, NRStyle=0). Local `dxgi.dll` NOT needed (DXVK goes Vulkan, dxgi never loads).
- **THE MAIN GOTCHA — `LoadFromDllMain=dlss5-feed.addon32` BREAKS registration through the layer**: the add-on loads in the layer's DllMain BEFORE the ReShade runtime initializes → `No add-on was registered ... Unloading again` → unloaded, no NR panel. **Fix: REMOVE LoadFromDllMain from ReShade.ini** — the add-on is picked up by folder scanning AFTER runtime init and registers. (Black Mesa tolerated LoadFromDllMain — different engine load order; FO3/Gamebryo — no.)
- **`dlss5-feed.cfg` is mandatory** (without it the add-on does not read the config — no `config:` line in the log): `enabled=1 mode=2 reset_every=0 warmup_rebuild=0 rebuild=0`.
- **Local `vulkan-1.dll` in the root did NOT help** (DXVK still loaded two modules: local + system, addresses 0x61bc1760/0x5fed1760) — the LoadFromDllMain fix was the decisive one.
- **Working symptoms**: `vkCreateDevice #1: app asked for 46 extension(s), added 5` + `shared set ready (Vulkan): 3840x2160` + `frame N delivered`; host64: `feature ready: 3840x2160 DLAA` + `frame N evaluated`; host64 opens its own overlay (key 36).
- FOSE: the build has only `fose_1_7.dll`/`fose_1_7ng.dll`, **no fose_loader.exe** — FOSE mods won't load, the game runs.
- **CONFIRMED WORKING (02.09)**: NR evaluates frames, the counter grows, the host64 overlay opens itself. Saves: `%USERPROFILE%\Documents\My Games\Fallout3\Saves\` (.fos native; lonebullet Chordian: Save 2 Vault 101, 11 Big Town, 12 Rivet City, 34 Test Labs, 60 Megaton — cities with NPCs for NR testing). Modded build — vanilla saves may not load; fallback: `coc Megaton` + console.

## 13. Deus Ex: Human Revolution — 32-bit native D3D11, NO wrappers (works, 02.09)
- **Daedalus Engine, 32-bit, native D3D11**: `dxhr.exe` does not import d3d statically, but **dynamically loads `dxgi.dll` + `d3d11.dll`** (the string `CreateDXGIFactory` is in the exe) → ReShade-dxgi (x86) is picked up when the D3D11 device is created. **Wrappers (dgVoodoo/DXVK) NOT needed** — unlike F.E.A.R/FO3.
- **Scheme**: `dxgi.dll` (ReShade x86) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 4.70, NRStyle=0) + Lumenite (`DLSS5_MV_PROVIDER=3`, Kernel ABOVE Feed). `LoadFromDllMain=dlss5-feed.addon32` WORKS (local dxgi, not a layer — the FO3 gotcha does not apply).
- Path: game folder (Steam repack, steam_appid 28050). Shortcut "Deus Ex Human Revolution - DLSS 5" → dxhr.exe.
- **API diagnostics**: if the exe does not import d3d — look for `dxgi.dll`/`d3d11.dll`/`CreateDXGIFactory` strings in the binary (dynamic loading = ReShade-dxgi will be picked up).

## 14. Quake III Arena — GOG loads system32 opengl32, ioq3 required (works, 03.09)
- **THE MAIN GOTCHA**: the GOG build loads `opengl32.dll` from **system32**, ignoring the local one (confirmed via process modules through 32-bit PowerShell). ReShade never loads — `ReShade.log` is not created, the ini is not rewritten. Known case on the ReShade forum: "quake3 always tries to use system32\opengl32.dll".
- **Fix: ioq3** (ioquake3.org, 64-bit). The renderer loads GL via `SDL264.dll` → `opengl32.dll` from the app folder → ReShade is picked up. Scheme = OpenMW pattern: `opengl32.dll` (ReShade64) + `dlss5-feed.addon64` + `renodx-dlss5.addon64` **4.60** + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=renodx-dlss5.addon64\x00dlss5-feed.addon64\x00` (NUL).
- **Verify**: `feature 18 created via the signed snippet after DLSS/DLAA for NR input 3840x2160`, `inline feature 18 evaluation succeeded (count=1 → count=60)`, MV probe 100% non-zero.
- **4K**: `baseq3/q3config.cfg` — `r_mode "-1"`, `r_customwidth 3840`, `r_customheight 2160`, `r_fullscreen 1`, `cg_fov 105`.
- **The ReShade menu may vanish after 5-7 s** (DirectInput 3 hooks) — known case; fix `RESHADE_DISABLE_INPUT_HOOK=1` (but then overlay clicks stop working).
- **ioq3 "Abnormal Exit" dialog** on unclean exit — "No" keeps the settings.

## 15. Serious Sam: The First Encounter — 32-bit OpenGL, 4K via config (works, 03.09)
- **Scheme**: `opengl32.dll` = ReShade x86 (the name defines the API) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`). `LoadFromDllMain=dlss5-feed.addon32` WORKS (local opengl32, not a layer).
- **4K without mods**: the engine enumerates modes via `EnumDisplaySettingsA` → `Scripts\PersistentSymbols.ini`: `sam_iScreenSizeI=3840`, `sam_iScreenSizeJ=2160`, `sam_bWideScreen=0`, `plr_fFOV=105`.
- **The in-game "Widescreen" option is a letterbox, NOT stretching** (GOG forum: "dont enable the widescreen option at all. just edit the screensize and fov"). "Image cropped top/bottom" = Widescreen enabled → `sam_bWideScreen=0`.
- **DPI**: the exe is not DPI-aware (AppliedDPI=120 at 125% scale) → the image shifts down/right. Fix: `HIGHDPIAWARE` via AppCompatFlags (`fix_ss_dpi.ps1`).
- **ReShade dies on video mode change in the menu** (`game device destroyed; shutting down` — GL context recreation kills the stack). Set the resolution in the config BEFORE launch; don't touch it in the menu.
- **CD-check**: the GOG build asks for the disc (`PLEASE INSERT GAME CD?` + `GetDriveTypeA`). MDF→ISO conversion (8-byte Alcohol header + sectors 2352→2048), mount via Mount-DiskImage as DRIVE_CDROM passes.
- **Steamify patch** (archive.org, `ss-tfe-steamifyupdate`) — Steam binaries with Hor+ FOV, fixes stretching/shifting.

## 16. Far Cry 2004 — CryEngine 1, D3D9 → DXVK (works, 03.09)
- **Scheme** = Fallout 3 pattern: `D3D9.dll` = DXVK 3.0.2 x86 + global ReShade Vulkan layer + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.70** + nvngx) + Lumenite (`MV_PROVIDER=3`).
- **ReShade.ini WITHOUT LoadFromDllMain** (layer path, FO3 gotcha — the add-on does not register through the layer).
- **32-bit launcher** `FarCry.exe` (32 KB, no imports) — renderers `XRenderD3D9.dll`/`XRenderOGL.dll` (both 32-bit), `system.cfg` → D3D9. WidescreenFix (version.dll + .asi) does not conflict.
- **4K**: DXVK exposes all EnumDisplaySettings modes — 3840×2160 is selectable in the game menu.

## 17. Jedi Knight: Jedi Academy — 32-bit OpenGL, same id Tech 3 (works, 03.09)
- **Scheme** = Serious Sam: `opengl32.dll` (ReShade x86) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=dlss5-feed.addon32`.
- **Unlike Quake III**: the GOG build loads the LOCAL opengl32.dll (verified in ReShade.log: `loaded from '...\GameData\opengl32.DLL'`) — ioq3/OpenJK not needed.
- **Stack in `GameData\`** (next to jamp.exe/jasp.exe), not the root.
- **4K**: `base\jaconfig.cfg` (SP) + `base\jampconfig.cfg` (MP) — `r_mode "-1"`, `r_customwidth 3840`, `r_customheight 2160`, `cg_fov 105`.
- **renodx 4.60** (not 4.70) — OpenGL transport, fenced pool (see §11).

## 18. Riddick: Assault on Dark Athena (GOG, Starbreeze/Ogier, 32-bit OpenGL) — launch, 4K, DLSS 5 (works, 04.09)
- **Startup HANG (not crash!) on modern NVIDIA** (RTX 5070 Ti verified): GLSL bias syntax in `System\GL\HLInclude_GLSL.xrg` — `texture2D(_tex,_st,_bias)`/`textureCube(_tex,_str,_bias)` the modern driver cannot compile. **Fix**: remove `,_bias` from the bodies of both `tex2DBias`/`texCubeBias` functions (leave the signatures). This is the "Game crashes at startup on modern Nvidia" PCGW entry (`CRenderContextGL::GLSL_LoadSrc`, `MRndrGL_GLSL.cpp(829)`).
- **Pre-fix startup symptom**: process alive, window exists but unresponsive → Event Log Application **Hang 1002**, NOT Application Error 1000. It gives no silent crashes — trust the Hang event.
- **4K: ONLY `VID_MODE=desktop`** in `%LOCALAPPDATA%\Atari\The Chronicles of Riddick - Assault on Dark Athena\Environment.cfg` (windowed, desktop size; renders 3840×2071 — the window title). Starting with `VID_MODE=3840 2160 32 144` = black window ~1600×1024 + silent exit (the engine cannot find the exact mode in the driver list, falls back). The menu applies 4K, but the engine silently loads the nearest supported mode — the image stays non-4K (WSGF: "altering the line to an unsupported resolution results in the game loading the closest officially supported resolution").
- **Fallback clue**: after a failed start the game rewrites `VID_MODE` to `1600 1024 32 120`, leaving `VID_DWIDTH/VID_DHEIGHT` as-is (it does not update them on mode change — engine quirk).
- **`VID_PIXELASPECT=1.333333` (4:3)** sticks from an old fallback → distorted proportions. Fixed by `VID_PIXELASPECT=1.000000` (Normal; Auto stretches — WSGF thread).
- **Success marker**: after the first successful menu entry `GAME_LASTVALIDPROFILE=xx` appears — the game passed graphics init.
- **DLSS 5 scheme** = Serious Sam pattern (32-bit OpenGL): `opengl32.dll` = ReShade x86 (RndrGL.dll statically imports opengl32 — interception guaranteed) + `dlss5-feed.addon32` (0.11.0-beta.2) + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=dlss5-feed.addon32` WORKS (local opengl32, not a layer). Stack in `System\Win32_x86\`.
- **`NRStyle=2` in host64/ReShade.ini → black screen when the feed is enabled** (32-bit schemes): use `NRStyle=0` (the NRStyle=2 tuning block is for 64-bit schemes).
- **Verify**: `dlss5-feed.log` — `shared set ready (OpenGL): 3840x2071` + `frame N delivered`; `host64\dlss5-feed-host.log` — `feature ready: 3840x2071 DLAA` + `frame N evaluated`; `host64\ReShade.log` — `feature 18 created via the signed snippet` + `inline feature 18 evaluation succeeded`. Harmless artifacts: `Failed to find NVSDK_NGX_D3D12_EvaluateFeature_C` (evaluation goes through the fallback) + WARN about reshade-shaders in host64 (effects not needed — only the add-on).
- exe properties: `HIGHDPIAWARE` in AppCompatFlags is set (without it DPI scaling breaks resolutions — the Steam 4K thread references Override High DPI). It does not check hardware — not an MP2 gate.

## 19. BloodRayne 2 Terminal Cut (GOG, 2004→2026) — 32-bit D3D8→D3D9 bundled bridge → DXVK (works, 04.09)
- **Scheme** = Fallout 3 pattern: `D3D9.dll` = DXVK 3.0.2 x86 + global ReShade Vulkan layer + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.70** + nvngx) + Lumenite (`MV_PROVIDER=3`). ReShade.ini WITHOUT LoadFromDllMain (layer path).
- **Bundled wrapper**: a custom `d3d8.dll` (279 KB) in the root imports `d3d9.dll` — Terminal Cut converts D3D8→D3D9 natively, so interception goes through the wrapper's d3d9. Do NOT replace d3d8.dll.
- **Verify**: `feature 18 created via the signed snippet` + `inline feature 18 evaluation succeeded` (host64/ReShade.log), `frame N evaluated` (host64 log), 16k+ frames. Confirmed by the user 04.09 ("бладрейн все хорошо").

## 20. Dark Messiah: Might and Magic (2006, Source, RUNE) — 32-bit D3D9 → DXVK (works, 04.09)
- **Scheme** = Fallout 3 pattern: `D3D9.dll` = DXVK 3.0.2 x86 **in the root AND in bin/** (Source loads GameBin first) + layer + addon32 + host64 (renodx 4.70) + Lumenite. WITHOUT LoadFromDllMain.
- **Launch**: `mm.exe` — launcher, mandatory args `-novid +map_background +exec dm.cfg`.
- **Verify**: feature 18 + 54k evaluations (host64 log), 4K 3840×2160.

## 21. DOOM 2016 (GOG) — 64-bit Vulkan, NO host64 (works, 04.09)
- **Scheme**: `DOOMx64vk.exe` (Vulkan) + global layer + `dlss5-feed.addon64` + `renodx-dlss5.addon64` 4.70 + Lumenite (`MV_PROVIDER=3`). **host64 NOT needed** — addon64 creates its own D3D12 device (64-bit path).
- **LoadFromDllMain=renodx-dlss5.addon64** works (layer path, but the 64-bit add-on registers — unlike addon32 through the layer).
- **Do NOT install v0.13.1-beta.1** (CreateFeature 0xC0000005 regression, hang) — only v0.11.0-beta.2 (addon64 md5 `3140914fbb0f`).
- **Verify**: feature 18 + evaluation succeeded (ReShade.log in the root, not host64).

## 22. Half-Life 2 (Steam) — 32-bit D3D11, NO wrappers (works, 04.09)
- **Scheme**: `dxgi.dll` = ReShade x86 + `dlss5-feed.addon32` + `host64\` (renodx 4.70) + Lumenite (`MV_PROVIDER=3`). LoadFromDllMain=addon32 (local dxgi, not a layer).
- **Source 2013 loads D3D11 dynamically** (ReShade.log: `Redirecting CreateDXGIFactory1`, `Installing delayed hooks for d3d11.dll (Just loaded via LoadLibrary)`) — dgVoodoo/DXVK NOT needed, unlike classic HL2.
- **Verify**: `shared set ready: 3840x2160 (100%)` + `frame N delivered` (dlss5-feed.log), `frame N evaluated` (host64 log). Confirmed 04.09: frame 14400 evaluated.
- **Pitfall**: `mode=1` — transport test (copies the frame WITHOUT NGX) — looks like "it works" but NR is not running. Always check the host64 log for `transport-only` and `mode=2` in the cfg.

## 23. NFS series (Underground / Underground 2 / Most Wanted 2005) — 32-bit D3D9 → DXVK (works, 04.09)
- **Scheme** = Fallout 3 pattern: `D3D9.dll` = DXVK 3.0.2 x86 + global ReShade Vulkan layer + `dlss5-feed.addon32` + `host64\` (renodx 4.70) + Lumenite (`MV_PROVIDER=3`). ReShade.ini WITHOUT LoadFromDllMain (layer path).
- **All three are 32-bit D3D9** (`Direct3DCreate9` in the exe, dynamic loading). UG/UG2 have d3d8.dll + d3d9.dll strings, MW only d3d9.dll.
- **Verify**: `shared set ready (Vulkan): 3840x2160` + `feature ready: 3840x2160 DLAA` + `frame N evaluated` (host64 log, DLSS GPU ~16.3 ms/frame). Confirmed 04.09: UG frame 19800, UG2 frame 32400, MW frame 18000.
- **Saves live in unexpected places**: UG → `C:\ProgramData\NFS Underground` (profile files `<name>.ugd` + `<name>.cfg/.opt`); UG2 → `%LOCALAPPDATA%\NFS Underground 2` (slots are FOLDERS `<name>\<name>`, `NAME DVD 1\NAME DVD 1`); MW → `Documents\NFS Most Wanted\<name>\`. The game creates its own profile on first launch (name from input) — rename downloaded saves to match it.
- **NFS UG: resolution is a mode index** (`RES: N` in `<profile>.cfg` = EnumDisplaySettings index: 0 = 640×480@59, 789 = 3840×2160@60). The exe is already patched for 4K (uniws: `mov eax,3840; mov esi,2160` — the 640×480 signature is gone), but the game still starts at 640×480 — pick the resolution in the in-game options (Options → Display).
- **NFS MW: widescreen fix** — `dinput8.dll` (D3D8/D3D9/DInput wrappers, ThirteenAG style) + `scripts\NFSMW2005_widescreen_fix.asi` + `scripts\nfsmw_res.ini` (ResX/ResY = 3840/2160). UG/UG2 — ThirteenAG WidescreenFixesPack (`dinput8.dll` + `scripts\*.asi`), 4K via the game menu.
- **uniws.exe** in UG/UG2 — Universal Widescreen Patcher (GUI, patches the exe by signatures from patches.ini); the exes are already patched.

## 24. DOOM 3 BFG Edition — 32-bit OpenGL (works, 04.09)
- **Scheme** = Serious Sam pattern: `opengl32.dll` = ReShade x86 + `dlss5-feed.addon32` + `host64\` (renodx **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), LoadFromDllMain=addon32.
- **Verify**: `shared set ready (OpenGL): 3840x2160` + `frame N evaluated` (host64 log, frame 30600). Confirmed 04.09.

## 25. Mass Effect Legendary Edition (ME1/ME2/ME3) — 64-bit D3D11, NO host64 (works, 02.09)
- **Scheme**: `dxgi.dll` = ReShade x64 + `dlss5-feed.addon64` + `renodx-dlss5.addon64` 4.70 + Lumenite (`MV_PROVIDER=3`). **host64 NOT needed** — 64-bit path (addon64 creates its own D3D12 device).
- **Verify**: `frame N delivered (3840x2160)` + MV probe 100% non-zero (dlss5-feed.log). Confirmed 02.09: frame 40200.
