# -*- coding: utf-8 -*-
# BloodRayne 2 Terminal Cut (GOG, 2004→2026) — DLSS 5 NR, 32-bit D3D8→D3D9 (бандл-обёртка) → DXVK
# Схема: кастомная d3d8.dll (279 КБ, бандл-мост D3D8→D3D9) → D3D9.dll = DXVK 3.0.2 x86 → Vulkan
#        → глобальный ReShade Vulkan-слой + dlss5-feed.addon32 + host64\ (renodx 4.70) + Lumenite
# ВАЖНО: НЕ LoadFromDllMain (слой-путь, FO3-грабли), НЕ dgVoodoo (валит игру)
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка игры (где лежит d3d8.dll/бандл)
#   FEEDER_DIR        — распакованный DLSS5-Feeder (v0.11.0-beta.2): dlss5-feed.addon32 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (для host64/, 5,592,064 Б)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
#   DXVK_D3D9         — DXVK 3.0.2 x86 d3d9.dll (7,843,854 Б)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

BR = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')
DXVK_D3D9 = env('DXVK_D3D9')

# 1. DXVK D3D9.dll (перевод D3D9 → Vulkan; бандл-d3d8 грузит d3d9 из папки)
shutil.copy2(DXVK_D3D9, os.path.join(BR, 'D3D9.dll'))
print('OK: D3D9.dll (DXVK 3.0.2 x86)')

# 2. Feeder addon32
shutil.copy2(os.path.join(FEEDER, 'dlss5-feed.addon32'), os.path.join(BR, 'dlss5-feed.addon32'))
print('OK: dlss5-feed.addon32')

# 3. host64/ — полный комплект
host = os.path.join(BR, 'host64')
os.makedirs(host, exist_ok=True)
shutil.copy2(os.path.join(FEEDER, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'))
shutil.copy2(RESHADE_X64, os.path.join(host, 'dxgi.dll'))
shutil.copy2(RENODX, os.path.join(host, 'renodx-dlss5.addon64'))
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    shutil.copy2(os.path.join(NVNGX, f), os.path.join(host, f))
print('OK: host64/ (exe + ReShade64 + renodx 4.70 + nvngx-пачка)')

# host64/ReShade.ini — рабочий тюнинг (NRStyle=1, полный блок)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=1\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=1\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=2\r\nNRIntensity=2\r\nNRGlobalTone=1.94\r\nNRLocalTone=1.8\r\nNRLocalStructure=2\r\nNRSkinStructure=1\r\nNRUICorrection=1\r\nNRDiffuseWhiteNits=271\r\nNRPaperWhiteScale=3.375\r\n')
print('OK: host64/ReShade.ini (рабочий тюнинг, NRStyle=1)')

# 4. reshade-shaders (полный набор: Feed + Lumenite + инклуды + ReShade.fxh)
src_sh = os.path.join(FEEDER, 'reshade-shaders')
dst_sh = os.path.join(BR, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('OK: reshade-shaders (Feed + Lumenite + инклуды)')

# 5. ReShade.ini (корень) — БЕЗ LoadFromDllMain (слой-путь!)
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
with open(os.path.join(BR, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('OK: ReShade.ini (БЕЗ LoadFromDllMain — слой-путь!)')

# 6. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
preset = (
    'Techniques=Lumenite_Kernel@lumenite_Kernel.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,Lumenite_AnamorphicBloom@lumenite_AnamorphicBloom.fx,Lumenite_Kernel@lumenite_Kernel.fx,Lumenite_LSAO@lumenite_LSAO.fx,Lumenite_QuantAO@lumenite_QuantAO.fx,Lumenite_QuantMotion@lumenite_QuantMotion.fx,Lumenite_RTAO@lumenite_RTAO.fx,LUMENITE_SSSR@lumenite_SSSR.fx,Lumenite_TRAA@lumenite_TRAA.fx\r\n'
)
with open(os.path.join(BR, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('OK: ReShadePreset.ini (Kernel + Feed)')

# 7. dlss5-feed.cfg — обязателен (mode=2)
cfg = (
    'enabled=1\r\n'
    'mode=2\r\n'
    'hdr=-1\r\n'
    'depth_inverted=-1\r\n'
    'flags=-1\r\n'
    'reset_every=1\r\n'
    'log_frames=3\r\n'
    'host_window=1\r\n'
    'work_resolution=100\r\n'
    'async_home=0\r\n'
    'mv_scale_x=1.000\r\n'
    'mv_scale_y=1.000\r\n'
)
with open(os.path.join(BR, 'dlss5-feed.cfg'), 'w', encoding='utf-8', newline='') as f:
    f.write(cfg)
print('OK: dlss5-feed.cfg (mode=2)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(BR)):
    if any(k in f.lower() for k in ['d3d9', 'dxgi', 'dlss5', 'reshade', 'host64']):
        p = os.path.join(BR, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
