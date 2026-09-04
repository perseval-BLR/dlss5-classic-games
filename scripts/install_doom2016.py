# -*- coding: utf-8 -*-
# DOOM 2016 (GOG) — DLSS 5 NR, 64-bit Vulkan → Feeder (addon64, БЕЗ host64)
# Схема: DOOMx64vk.exe (Vulkan) + глобальный ReShade Vulkan-слой + dlss5-feed.addon64
#        + renodx-dlss5.addon64 (4.70) + Lumenite (MV_PROVIDER=3)
# ВАЖНО: 64-bit схема — host64 НЕ нужен (аддон сам создаёт D3D12-устройство).
#        LoadFromDllMain=renodx-dlss5.addon64 (локальный dxgi-путь не используется — слой).
#        v0.13.1-beta.1 НЕ ставить (регрессия CreateFeature 0xC0000005) — только v0.11.0-beta.2.
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка игры (где DOOMx64vk.exe)
#   FEEDER_DIR        — распакованный DLSS5-Feeder (v0.11.0-beta.2): dlss5-feed.addon64 + reshade-shaders/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.70)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

DM = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
NVNGX = env('NVNGX_DIR')

# 1. Feeder addon64
shutil.copy2(os.path.join(FEEDER, 'dlss5-feed.addon64'), os.path.join(DM, 'dlss5-feed.addon64'))
print('OK: dlss5-feed.addon64 (0.11.0-beta.2)')

# 2. renodx-dlss5.addon64 (4.70)
shutil.copy2(RENODX, os.path.join(DM, 'renodx-dlss5.addon64'))
print('OK: renodx-dlss5.addon64 (4.70)')

# 3. nvngx-пачка (полный комплект — правило пользователя)
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    shutil.copy2(os.path.join(NVNGX, f), os.path.join(DM, f))
print('OK: nvngx-пачка (SR/FG/RR/NR)')

# 4. reshade-shaders (полный набор: Feed + Lumenite + инклуды + ReShade.fxh)
src_sh = os.path.join(FEEDER, 'reshade-shaders')
dst_sh = os.path.join(DM, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('OK: reshade-shaders (Feed + Lumenite + инклуды)')

# 5. ReShade.ini — LoadFromDllMain=renodx-dlss5.addon64, MV_PROVIDER=3 (Lumenite)
ini = (
    '[ADDON]\r\n'
    'LoadFromDllMain=renodx-dlss5.addon64\r\n'
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
    '\r\n'
    '[RenoDX.DLSS5]\r\n'
    'EnableHooks=2\r\n'
    'NeuralUplift=1\r\n'
    'NRAutoMask=1\r\n'
    'NREnableUpscaling=1\r\n'
    'NRGlobalTone=1.57\r\n'
    'NRIntensity=1.98\r\n'
    'NRLocalStructure=1.39\r\n'
    'NRLocalTone=1.58\r\n'
    'NRPreset=2\r\n'
    'NRSkinStructure=1.45\r\n'
    'NRStyle=1\r\n'
)
with open(os.path.join(DM, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('OK: ReShade.ini (LoadFromDllMain=renodx, MV_PROVIDER=3)')

# 6. ReShadePreset.ini — Lumenite_Kernel ВЫШЕ DLSS5_Feed
preset = (
    'Techniques=Lumenite_Kernel@lumenite_Kernel.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,Lumenite_AnamorphicBloom@lumenite_AnamorphicBloom.fx,Lumenite_Kernel@lumenite_Kernel.fx,Lumenite_LSAO@lumenite_LSAO.fx,Lumenite_QuantAO@lumenite_QuantAO.fx,Lumenite_QuantMotion@lumenite_QuantMotion.fx,Lumenite_RTAO@lumenite_RTAO.fx,LUMENITE_SSSR@lumenite_SSSR.fx,Lumenite_TRAA@lumenite_TRAA.fx\r\n'
)
with open(os.path.join(DM, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
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
    'warmup_rebuild=180\r\n'
    'rebuild=0\r\n'
    'log_frames=3\r\n'
    'create_delay=60\r\n'
    'preset=0\r\n'
    'work_resolution=100\r\n'
    'gpu_timeout_ms=2000\r\n'
    'buffer_home=1\r\n'
    'async_home=0\r\n'
    'sync_home=0\r\n'
    'mv_scale_x=1.000\r\n'
    'mv_scale_y=1.000\r\n'
)
with open(os.path.join(DM, 'dlss5-feed.cfg'), 'w', encoding='utf-8', newline='') as f:
    f.write(cfg)
print('OK: dlss5-feed.cfg (mode=2)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(DM)):
    if any(k in f.lower() for k in ['dlss5', 'reshade', 'renodx', 'nvngx']):
        p = os.path.join(DM, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
