# -*- coding: utf-8 -*-
# Гоночная четвёрка (Split/Second, Race Driver: GRID, NFS: Shift, NFS: ProStreet) — DLSS 5 NR, 32-bit D3D9 → DXVK → Vulkan-слой
# Паттерн: NFS-трилогия / Fallout 3 (проверен). dgVoodoo НЕ используется.
#
# Использование (переменные окружения):
#   GAME_DIR          — папка игры
#   DXVK_DONOR        — рабочая D3D9-установка-донор (Fallout 3): D3D9.dll + dlss5-feed.addon32 + host64/ + reshade-shaders/ + ReShadePreset.ini + dlss5-feed.cfg
#   FEEDER_DIR        — распакованный DLSS5-Feeder: dlss5-feed.addon32 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (для host64/)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
#   DXVK_D3D9         — (опционально) спец. DXVK для GRID: 2.7.1 addon_fix от xatornet (чинит 4K-краш). Если не задан — берётся D3D9.dll донора.
#   DXVK_CONF         — (опционально) dxvk.conf для GRID (d3d9.forceRefreshRate=144). Копируется в GAME_DIR.
import os, shutil

def env(name, required=True):
    v = os.environ.get(name)
    if required and not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if v and not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

G = env('GAME_DIR')
FO = env('DXVK_DONOR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')
DXVK_D3D9 = env('DXVK_D3D9', required=False)
DXVK_CONF = env('DXVK_CONF', required=False)

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

print(f'===== {os.path.basename(G)} =====')

# 1. DXVK D3D9.dll (перевод D3D9 → Vulkan); для GRID — спец. сборка 2.7.1 addon_fix
if DXVK_D3D9:
    cp(DXVK_D3D9, os.path.join(G, 'D3D9.dll'), 'D3D9.dll (DXVK 2.7.1 addon_fix — GRID 4K-фикс)')
else:
    cp(os.path.join(FO, 'D3D9.dll'), os.path.join(G, 'D3D9.dll'), 'D3D9.dll (DXVK 3.0.2 x86)')

# 1b. dxvk.conf (GRID: forceRefreshRate под частоту монитора)
if DXVK_CONF:
    cp(DXVK_CONF, os.path.join(G, 'dxvk.conf'), 'dxvk.conf (forceRefreshRate)')

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

# host64/ReShade.ini — БЕЗ [RenoDX.DLSS5] (дефолты аддона — правило пользователя 05.09)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n')
print('  + host64/ReShade.ini (БЕЗ тюнинга — дефолты)')

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
