# -*- coding: utf-8 -*-
# OpenMW (Morrowind ReBuild) — DLSS 5 NR через OpenGL-путь Feeder (64-bit)
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR          — папка OpenMW (где лежит openmw.exe)
#   FEEDER_DIR        — распакованный DLSS5-Feeder (v0.11.0-beta.2): dlss5-feed.addon64 + host64/
#   RENODX_ADDON      — renodx-dlss5.addon64 (4.60 для OpenGL-транспорта! 4.70 НЕ работает)
#   RESHADE_X64_DXGI  — ReShade x64 dxgi.dll (5,592,064 Б; будет переименован в opengl32.dll)
#   NVNGX_DIR         — папка с nvngx_dlss.dll / nvngx_dlssd.dll / nvngx_dlssg.dll / nvngx_dlssnr.dll (310.8.0)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

MW = env('GAME_DIR')
FEEDER = env('FEEDER_DIR')
RENODX = env('RENODX_ADDON')
RESHADE_X64 = env('RESHADE_X64_DXGI')
NVNGX = env('NVNGX_DIR')

# 1. opengl32.dll = ReShade 64-bit (тот же бинарник, имя определяет API)
shutil.copy2(RESHADE_X64, os.path.join(MW, 'opengl32.dll'))
print('OK: opengl32.dll (ReShade 64-bit, 5,592,064 Б)')

# 2. Аддоны
shutil.copy2(os.path.join(FEEDER, 'dlss5-feed.addon64'), os.path.join(MW, 'dlss5-feed.addon64'))
print('OK: dlss5-feed.addon64 (0.11.0-beta.2)')
shutil.copy2(RENODX, os.path.join(MW, 'renodx-dlss5.addon64'))
print('OK: renodx-dlss5.addon64 (4.60)')

# 3. nvngx-пачка (полный комплект)
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    shutil.copy2(os.path.join(NVNGX, f), os.path.join(MW, f))
print('OK: nvngx-пачка (SR/FG/RR/NR 310.8.0)')

# 4. reshade-shaders (полный набор: Feed + VORT + инклуды + ReShade.fxh)
src_sh = os.path.join(FEEDER, 'reshade-shaders')
dst_sh = os.path.join(MW, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('OK: reshade-shaders (Feed + VORT + инклуды)')

# 5. ReShade.ini (NUL-разделители, полный PreprocessorDefinitions, без BOM)
ini = (
    '[ADDON]\r\n'
    'LoadFromDllMain=renodx-dlss5.addon64\x00dlss5-feed.addon64\x00\r\n'
    'OverlayCollapsed=\r\n'
    '\r\n'
    '[GENERAL]\r\n'
    'EffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\n'
    'NoDebugInfo=1\r\n'
    'NoEffectCache=0\r\n'
    'NoReloadOnInit=0\r\n'
    'PerformanceMode=0\r\n'
    'PreprocessorDefinitions=RESHADE_DEPTH_LINEARIZATION_FAR_PLANE=1000.0,RESHADE_DEPTH_INPUT_IS_UPSIDE_DOWN=0,RESHADE_DEPTH_INPUT_IS_REVERSED=1,RESHADE_DEPTH_INPUT_IS_LOGARITHMIC=0,DLSS5_MV_PROVIDER=2\r\n'
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
    'NRColorStrength=0.53\r\n'
    'NRDiffuseWhiteNits=201\r\n'
    'NREnableUpscaling=0\r\n'
    'NRGlobalTone=1.89\r\n'
    'NRIntensity=2\r\n'
    'NRLocalStructure=1.7\r\n'
    'NRLocalTone=1.8\r\n'
    'NRPaperWhiteScale=5.319\r\n'
    'NRPreset=3\r\n'
    'NRSkinStructure=2\r\n'
    'NRStyle=2\r\n'
    'NRUICorrection=1\r\n'
)
with open(os.path.join(MW, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('OK: ReShade.ini (LoadFromDllMain=renodx-dlss5+feed, MV_PROVIDER=2=VORT, тюнинг NR)')

# 6. ReShadePreset.ini — VORT_MotionEffects ПЕРВОЙ, потом Feed
preset = (
    'Techniques=vort_MotionEffects@vort_Motion.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,vort_MotionEffects@vort_Motion.fx\r\n'
)
with open(os.path.join(MW, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('OK: ReShadePreset.ini (VORT + Feed)')

# 7. dlss5-feed.cfg — диагностические флаги ВЫКЛЮЧЕНЫ (иначе NR валится)
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
with open(os.path.join(MW, 'dlss5-feed.cfg'), 'w', encoding='utf-8', newline='') as f:
    f.write(cfg)
print('OK: dlss5-feed.cfg (reset_every=0, rebuild=0)')

print()
print('=== Итог OpenMW/ ===')
for f in sorted(os.listdir(MW)):
    if any(k in f.lower() for k in ['opengl32', 'dlss5', 'renodx', 'nvngx', 'reshade']):
        p = os.path.join(MW, f)
        print(f'  {f} ({os.path.getsize(p)} Б)' if os.path.isfile(p) else f'  {f}/')
