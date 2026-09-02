# -*- coding: utf-8 -*-
# Deus Ex: Human Revolution — DLSS 5 NR, 32-bit нативный D3D11 (Daedalus Engine)
# dxhr.exe динамически грузит dxgi.dll + d3d11.dll (CreateDXGIFactory) — ReShade-dxgi подхватится
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка игры (где лежит dxhr.exe)
#   FEEDER_DIR        — распакованный DLSS5-Feeder (v0.11.0-beta.2): dlss5-feed.addon32 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   RESHADE_X86_DXGI  — ReShade x86 dxgi.dll (сборка Addon, 4,398,080 Б)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (для host64/, 5,592,064 Б)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

DX = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X86 = env('RESHADE_X86_DXGI')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')

# 1. ReShade x86 dxgi
shutil.copy2(RESHADE_X86, os.path.join(DX, 'dxgi.dll'))
print('OK: dxgi.dll (ReShade x86)')

# 2. Feeder addon32
shutil.copy2(os.path.join(FEEDER, 'dlss5-feed.addon32'), os.path.join(DX, 'dlss5-feed.addon32'))
print('OK: dlss5-feed.addon32')

# 3. host64/
host = os.path.join(DX, 'host64')
os.makedirs(host, exist_ok=True)
shutil.copy2(os.path.join(FEEDER, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'))
shutil.copy2(RESHADE_X64, os.path.join(host, 'dxgi.dll'))
shutil.copy2(RENODX, os.path.join(host, 'renodx-dlss5.addon64'))
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    shutil.copy2(os.path.join(NVNGX, f), os.path.join(host, f))
print('OK: host64/ (exe + ReShade64 + renodx 4.70 + nvngx)')

with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=2\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=2\r\nNRIntensity=2\r\nNRGlobalTone=1.61\r\nNRLocalTone=1.55\r\nNRLocalStructure=2\r\nNRSkinStructure=0.62\r\nNRPaperWhiteScale=3.225\r\n')
print('OK: host64/ReShade.ini (рабочий тюнинг, NRStyle=2)')

# 4. reshade-shaders (полный набор: Feed + Lumenite + инклуды + ReShade.fxh)
src_sh = os.path.join(FEEDER, 'reshade-shaders')
dst_sh = os.path.join(DX, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('OK: reshade-shaders')

# 5. ReShade.ini (корень)
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
with open(os.path.join(DX, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('OK: ReShade.ini (feed.addon32, MV_PROVIDER=3)')

# 6. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
preset = (
    'Techniques=Lumenite_Kernel@lumenite_Kernel.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,Lumenite_AnamorphicBloom@lumenite_AnamorphicBloom.fx,Lumenite_Kernel@lumenite_Kernel.fx,Lumenite_LSAO@lumenite_LSAO.fx,Lumenite_QuantAO@lumenite_QuantAO.fx,Lumenite_QuantMotion@lumenite_QuantMotion.fx,Lumenite_RTAO@lumenite_RTAO.fx,LUMENITE_SSSR@lumenite_SSSR.fx,Lumenite_TRAA@lumenite_TRAA.fx\r\n'
)
with open(os.path.join(DX, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('OK: ReShadePreset.ini (Kernel + Feed)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(DX)):
    if any(k in f.lower() for k in ['dxgi', 'dlss5', 'reshade', 'host64']):
        p = os.path.join(DX, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
