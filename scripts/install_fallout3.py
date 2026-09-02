# -*- coding: utf-8 -*-
# Fallout 3 (ReBuild) — DLSS 5 NR, 32-bit D3D9 → DXVK → Vulkan-слой ReShade
# ВАЖНО: НЕ dgVoodoo (валит игру), НЕ LoadFromDllMain (ломает регистрацию через слой)
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка игры (где лежит Fallout3.exe)
#   FEEDER_DIR        — распакованный DLSS5-Feeder (v0.11.0-beta.2): dlss5-feed.addon32 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (для host64/, 5,592,064 Б)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
#   DXVK_D3D9         — DXVK 3.0.2 x86 d3d9.dll (7,843,854 Б)
#   VULKAN1_X86       — локальный vulkan-1.dll x86 (из Black Mesa bin/; опционально, но рекомендуется)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

FO = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')
DXVK_D3D9 = env('DXVK_D3D9')
VULKAN1 = env('VULKAN1_X86')

# 1. DXVK D3D9.dll (перевод D3D9 → Vulkan)
shutil.copy2(DXVK_D3D9, os.path.join(FO, 'D3D9.dll'))
print('OK: D3D9.dll (DXVK 3.0.2 x86)')

# 2. Локальный vulkan-1.dll (чтобы DXVK не грузил системный)
shutil.copy2(VULKAN1, os.path.join(FO, 'vulkan-1.dll'))
print('OK: vulkan-1.dll (x86)')

# 3. Feeder addon32
shutil.copy2(os.path.join(FEEDER, 'dlss5-feed.addon32'), os.path.join(FO, 'dlss5-feed.addon32'))
print('OK: dlss5-feed.addon32')

# 4. host64/ — полный комплект
host = os.path.join(FO, 'host64')
os.makedirs(host, exist_ok=True)
shutil.copy2(os.path.join(FEEDER, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'))
shutil.copy2(RESHADE_X64, os.path.join(host, 'dxgi.dll'))  # ReShade 64-bit
shutil.copy2(RENODX, os.path.join(host, 'renodx-dlss5.addon64'))
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    shutil.copy2(os.path.join(NVNGX, f), os.path.join(host, f))
print('OK: host64/ (exe + ReShade64 + renodx 4.70 + nvngx-пачка)')

# host64/ReShade.ini — рабочий тюнинг (NRStyle=2, полный блок)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=2\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=3\r\nNRIntensity=2\r\nNRGlobalTone=2\r\nNRLocalTone=2\r\nNRLocalStructure=2\r\nNRSkinStructure=1\r\nNRUICorrection=1\r\nNRPaperWhiteScale=2.375\r\n')
print('OK: host64/ReShade.ini (рабочий тюнинг, NRStyle=2)')

# 5. reshade-shaders (полный набор: Feed + Lumenite + инклуды + ReShade.fxh)
src_sh = os.path.join(FEEDER, 'reshade-shaders')
dst_sh = os.path.join(FO, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('OK: reshade-shaders (Feed + Lumenite + инклуды)')

# 6. ReShade.ini (корень) — БЕЗ LoadFromDllMain (иначе аддон не регистрируется через слой!)
ini = (
    '[ADDON]\r\n'
    'OverlayCollapsed=\r\n'
    '\r\n'
    '[GENERAL]\r\n'
    'EffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\n'
    'NoDebugInfo=1\r\n'
    'NoEffectCache=0\r\n'
    'NoReloadOnInit=0\r\n'
    'PerformanceMode=0\r\n'
    'PreprocessorDefinitions=RESHADE_DEPTH_LINEARIZATION_FAR_PLANE=1000.0,RESHADE_DEPTH_INPUT_IS_UPSIDE_DOWN=0,RESHADE_DEPTH_INPUT_IS_REVERSED=1,RESHADE_DEPTH_INPUT_IS_LOGARITHMIC=0,DLSS5_MV_PROVIDER=3\r\n'
    'PresetPath=.\\ReShadePreset.ini\r\n'
    'PresetShortcutKeys=\r\n'
    'PresetShortcutPaths=\r\n'
    'PresetTransitionDuration=1000\r\n'
    'SkipLoadingDisabledEffects=0\r\n'
    'StartupPresetPath=\r\n'
    'TextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n'
    '\r\n'
    '[INPUT]\r\n'
    'ForceShortcutModifiers=1\r\n'
    'InputProcessing=2\r\n'
    'KeyEffects=0,0,0,0\r\n'
    'KeyOverlay=36,0,0,0\r\n'
    '\r\n'
    '[OVERLAY]\r\n'
    'TutorialProgress=0\r\n'
)
with open(os.path.join(FO, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('OK: ReShade.ini (БЕЗ LoadFromDllMain — слой-путь!)')

# 7. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
preset = (
    'Techniques=Lumenite_Kernel@lumenite_Kernel.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,Lumenite_AnamorphicBloom@lumenite_AnamorphicBloom.fx,Lumenite_Kernel@lumenite_Kernel.fx,Lumenite_LSAO@lumenite_LSAO.fx,Lumenite_QuantAO@lumenite_QuantAO.fx,Lumenite_QuantMotion@lumenite_QuantMotion.fx,Lumenite_RTAO@lumenite_RTAO.fx,LUMENITE_SSSR@lumenite_SSSR.fx,Lumenite_TRAA@lumenite_TRAA.fx\r\n'
)
with open(os.path.join(FO, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('OK: ReShadePreset.ini (Kernel + Feed)')

# 8. dlss5-feed.cfg — обязателен (без него аддон не читает конфиг)
cfg = (
    'enabled=1\r\n'
    'mode=2\r\n'
    'hdr=-1\r\n'
    'depth_inverted=-1\r\n'
    'flags=-1\r\n'
    'reset_every=0\r\n'
    'warmup_rebuild=0\r\n'
    'rebuild=0\r\n'
    'log_frames=3\r\n'
    'host_window=1\r\n'
    'work_resolution=100\r\n'
    'async_home=0\r\n'
    'mv_scale_x=1.000\r\n'
    'mv_scale_y=1.000\r\n'
)
with open(os.path.join(FO, 'dlss5-feed.cfg'), 'w', encoding='utf-8', newline='') as f:
    f.write(cfg)
print('OK: dlss5-feed.cfg (mode=2, reset_every=0)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(FO)):
    if any(k in f.lower() for k in ['d3d9', 'dxgi', 'dlss5', 'reshade', 'vulkan', 'host64']):
        p = os.path.join(FO, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
