# -*- coding: utf-8 -*-
# NFS серия (Underground, Underground 2, Most Wanted) — DLSS 5 NR, 32-bit D3D9 → DXVK → Vulkan-слой
# Паттерн: Fallout 3 / Far Cry (проверен). dgVoodoo НЕ используется.
#
# Использование (переменные окружения):
#   GAME_DIR          — папка игры (NFS Underground / Underground 2 / Most Wanted)
#   DXVK_DONOR        — рабочая D3D9-установка-донор (Fallout 3): D3D9.dll + dlss5-feed.addon32 + host64/ + reshade-shaders/ + ReShadePreset.ini + dlss5-feed.cfg
#   FEEDER_DIR        — распакованный DLSS5-Feeder: dlss5-feed.addon32 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (для host64/)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

G = env('GAME_DIR')
FO = env('DXVK_DONOR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

print(f'===== {os.path.basename(G)} =====')

# 1. DXVK D3D9.dll (перевод D3D9 → Vulkan)
cp(os.path.join(FO, 'D3D9.dll'), os.path.join(G, 'D3D9.dll'), 'D3D9.dll (DXVK 3.0.2 x86)')

# 2. Feeder addon32
cp(os.path.join(FEEDER, 'dlss5-feed.addon32'), os.path.join(G, 'dlss5-feed.addon32'), 'dlss5-feed.addon32')

# 3. host64/ — полный комплект
host = os.path.join(G, 'host64')
os.makedirs(host, exist_ok=True)
cp(os.path.join(FEEDER, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'), 'host64/dlss5-feed-host64.exe')
cp(RESHADE_X64, os.path.join(host, 'dxgi.dll'), 'host64/dxgi.dll (ReShade 64-bit)')
cp(RENODX, os.path.join(host, 'renodx-dlss5.addon64'), 'host64/renodx-dlss5.addon64 (4.70)')
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    cp(os.path.join(NVNGX, f), os.path.join(host, f), f'host64/{f}')

# host64/ReShade.ini — рабочий тюнинг (NRStyle=2, полный блок)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=2\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=3\r\nNRIntensity=2\r\nNRGlobalTone=2\r\nNRLocalTone=2\r\nNRLocalStructure=2\r\nNRSkinStructure=1\r\nNRUICorrection=1\r\nNRPaperWhiteScale=2.375\r\n')
print('  + host64/ReShade.ini (рабочий тюнинг, NRStyle=2)')

# 4. reshade-shaders (полный набор: Feed + Lumenite + инклуды + ReShade.fxh)
src_sh = os.path.join(FO, 'reshade-shaders')
dst_sh = os.path.join(G, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('  + reshade-shaders (Feed + Lumenite + инклуды)')

# 5. ReShade.ini (корень) — БЕЗ LoadFromDllMain (слой-путь!), MV_PROVIDER=3
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
with open(os.path.join(G, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('  + ReShade.ini (БЕЗ LoadFromDllMain, MV_PROVIDER=3)')

# 6. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
cp(os.path.join(FO, 'ReShadePreset.ini'), os.path.join(G, 'ReShadePreset.ini'), 'ReShadePreset.ini (Kernel + Feed)')

# 7. dlss5-feed.cfg — обязателен, mode=2
cp(os.path.join(FO, 'dlss5-feed.cfg'), os.path.join(G, 'dlss5-feed.cfg'), 'dlss5-feed.cfg (mode=2, reset_every=0)')

print()
print('Готово.')
