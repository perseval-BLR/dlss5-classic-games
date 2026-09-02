# -*- coding: utf-8 -*-
# Black Mesa (32-bit Source 2013, D3D9) — DLSS 5 NR через DXVK + Vulkan-слой ReShade
# ВАЖНО: dgVoodoo НЕ работает (краши LockVertex/LockIndexBuffer) — только DXVK
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка игры (где лежит hl2.exe / bms.exe)
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

BM = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')
DXVK_D3D9 = env('DXVK_D3D9')
VULKAN1 = env('VULKAN1_X86')

def cp(src, dst):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {os.path.basename(dst)}')
    return True

print('=== Black Mesa DLSS 5 stack ===')

# 1. DXVK: D3D9.dll (x86) в корень И в bin/ (Source резолвит GameBin первым)
cp(DXVK_D3D9, os.path.join(BM, 'D3D9.dll'))
cp(DXVK_D3D9, os.path.join(BM, 'bin', 'D3D9.dll'))
# локальный vulkan-1.dll (x86) — чтобы DXVK не грузил системный
cp(VULKAN1, os.path.join(BM, 'vulkan-1.dll'))
cp(VULKAN1, os.path.join(BM, 'bin', 'vulkan-1.dll'))

# 2. Feeder addon32
cp(os.path.join(FEEDER, 'dlss5-feed.addon32'), os.path.join(BM, 'dlss5-feed.addon32'))

# 3. Шейдеры: DLSS5_Feed.fx + Lumenite (свежий mainline)
shd = os.path.join(BM, 'reshade-shaders', 'Shaders')
txt = os.path.join(BM, 'reshade-shaders', 'Textures')
cp(os.path.join(FEEDER, 'reshade-shaders', 'Shaders', 'DLSS5_Feed.fx'), os.path.join(shd, 'DLSS5_Feed.fx'))
for fn in os.listdir(os.path.join(FEEDER, 'reshade-shaders', 'Shaders')):
    if fn.endswith('.fx') and fn != 'DLSS5_Feed.fx':
        cp(os.path.join(FEEDER, 'reshade-shaders', 'Shaders', fn), os.path.join(shd, fn))
for fn in os.listdir(os.path.join(FEEDER, 'reshade-shaders', 'Shaders', 'include')):
    cp(os.path.join(FEEDER, 'reshade-shaders', 'Shaders', 'include', fn), os.path.join(shd, 'include', fn))
cp(os.path.join(FEEDER, 'reshade-shaders', 'Textures', 'lumenite_bluenoise256.png'), os.path.join(txt, 'lumenite_bluenoise256.png'))

# 4. host64: host64.exe + dxgi x64 + renodx 4.70 + полный nvngx
host = os.path.join(BM, 'host64')
cp(os.path.join(FEEDER, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'))
cp(RESHADE_X64, os.path.join(host, 'dxgi.dll'))
cp(RENODX, os.path.join(host, 'renodx-dlss5.addon64'))
for dll in ['nvngx_dlss.dll', 'nvngx_dlssg.dll', 'nvngx_dlssd.dll', 'nvngx_dlssnr.dll']:
    cp(os.path.join(NVNGX, dll), os.path.join(host, dll))

# host64/ReShade.ini — рабочий тюнинг (NRStyle=2, полный блок)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=2\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=1\r\nNRIntensity=2\r\nNRGlobalTone=1.68\r\nNRLocalTone=1.48\r\nNRLocalStructure=2\r\nNRSkinStructure=1\r\nNRPaperWhiteScale=3.225\r\n')
print('  + host64/ReShade.ini (рабочий тюнинг, NRStyle=2)')

# 5. ReShade.ini (без BOM!) для игры: addon32 + Lumenite провайдер
ini = (
    '[ADDON]\r\n'
    'LoadFromDllMain=dlss5-feed.addon32\r\n'
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
with open(os.path.join(BM, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('  + ReShade.ini (без BOM, provider=3)')

# 6. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
preset = (
    'Techniques=Lumenite_Kernel@lumenite_Kernel.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,Lumenite_AnamorphicBloom@lumenite_AnamorphicBloom.fx,Lumenite_Kernel@lumenite_Kernel.fx,Lumenite_LSAO@lumenite_LSAO.fx,Lumenite_QuantAO@lumenite_QuantAO.fx,Lumenite_QuantMotion@lumenite_QuantMotion.fx,Lumenite_RTAO@lumenite_RTAO.fx,LUMENITE_SSSR@lumenite_SSSR.fx,Lumenite_TRAA@lumenite_TRAA.fx\r\n'
)
with open(os.path.join(BM, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('  + ReShadePreset.ini (Kernel + Feed)')

# 7. dlss5-feed.cfg
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
    'async_home=1\r\n'
    'mv_scale_x=1.000\r\n'
    'mv_scale_y=1.000\r\n'
)
with open(os.path.join(BM, 'dlss5-feed.cfg'), 'w', encoding='utf-8', newline='') as f:
    f.write(cfg)
print('  + dlss5-feed.cfg (mode=2, reset_every=0)')

print('Готово.')
