# -*- coding: utf-8 -*-
# Serious Sam: The First Encounter (RC2, 2001) — DLSS 5 NR, 32-bit OpenGL → Feeder
# Паттерн: OpenMW (OpenGL-путь: VORT + renodx 4.60) × 32-bit схема (addon32 + host64)
#
# Схема:
#   opengl32.dll = ReShade x86 (имя файла определяет API)
#   dlss5-feed.addon32 (0.12.0) + host64\ (renodx-dlss5 4.60 + nvngx-пачка)
#   VORT (MV_PROVIDER=2) — Lumenite на OpenGL даёт 0% векторов
#   renodx 4.60 — 4.70 не работает на OpenGL-транспорте (fenced pool)
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR       — папка Serious Sam (куда будет установлен стек, обычно <игра>\Bin)
#   OPENGL_DONOR   — рабочая 64-bit OpenGL установка (OpenMW): renodx-dlss5.addon64 (4.60!),
#                    reshade-shaders (VORT + инклуды), dlss5-feed.cfg
#   X86_DONOR      — рабочая 32-bit установка (Deus Ex: HR): dxgi.dll (ReShade x86),
#                    dlss5-feed.addon32, host64\ (dlss5-feed-host64.exe, dxgi.dll ReShade64, nvngx-пачка)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

SS = env('GAME_DIR')
MW = env('OPENGL_DONOR')      # OpenGL-донор: VORT, cfg, пресет, renodx 4.60
DX = env('X86_DONOR')         # 32-bit донор: addon32, ReShade x86, host64 exe

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

print('=== Serious Sam DLSS 5 stack (32-bit OpenGL) ===')

# 1. opengl32.dll = ReShade x86 (4,398,080 Б — тот же бинарник, имя определяет API)
cp(os.path.join(DX, 'dxgi.dll'), os.path.join(SS, 'opengl32.dll'), 'opengl32.dll (ReShade x86)')

# 2. Feeder addon32 (0.12.0)
cp(os.path.join(DX, 'dlss5-feed.addon32'), os.path.join(SS, 'dlss5-feed.addon32'), 'dlss5-feed.addon32 (0.12.0)')

# 3. host64/ — полный комплект
host = os.path.join(SS, 'host64')
cp(os.path.join(DX, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'), 'host64/dlss5-feed-host64.exe (0.12.0)')
cp(os.path.join(DX, 'host64', 'dxgi.dll'), os.path.join(host, 'dxgi.dll'), 'host64/dxgi.dll (ReShade 64-bit)')
cp(os.path.join(MW, 'renodx-dlss5.addon64'), os.path.join(host, 'renodx-dlss5.addon64'), 'host64/renodx-dlss5.addon64 (4.60 — OpenGL!)')
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    cp(os.path.join(DX, 'host64', f), os.path.join(host, f), f'host64/{f}')

# host64/ReShade.ini — тюнинг (NRStyle=2, полный блок)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=2\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=3\r\nNRIntensity=2\r\nNRGlobalTone=2\r\nNRLocalTone=2\r\nNRLocalStructure=2\r\nNRSkinStructure=1\r\nNRUICorrection=1\r\nNRPaperWhiteScale=2.375\r\n')
print('  + host64/ReShade.ini (тюнинг, NRStyle=2)')

# 4. reshade-shaders: DLSS5_Feed.fx + VORT + инклуды + ReShade.fxh/UI.fxh
shd = os.path.join(SS, 'reshade-shaders', 'Shaders')
txt = os.path.join(SS, 'reshade-shaders', 'Textures')
cp(os.path.join(MW, 'reshade-shaders', 'Shaders', 'DLSS5_Feed.fx'), os.path.join(shd, 'DLSS5_Feed.fx'), 'Shaders/DLSS5_Feed.fx (0.12.0)')
cp(os.path.join(MW, 'reshade-shaders', 'Shaders', 'vort_Motion.fx'), os.path.join(shd, 'vort_Motion.fx'), 'Shaders/vort_Motion.fx')
cp(os.path.join(MW, 'reshade-shaders', 'Shaders', 'ReShade.fxh'), os.path.join(shd, 'ReShade.fxh'), 'Shaders/ReShade.fxh')
cp(os.path.join(MW, 'reshade-shaders', 'Shaders', 'ReShadeUI.fxh'), os.path.join(shd, 'ReShadeUI.fxh'), 'Shaders/ReShadeUI.fxh')
# VORT-инклуды (регистр Includes/ — БОЛЬШАЯ буква!)
src_inc = os.path.join(MW, 'reshade-shaders', 'Shaders', 'Includes')
dst_inc = os.path.join(shd, 'Includes')
if os.path.isdir(src_inc):
    os.makedirs(dst_inc, exist_ok=True)
    for f in os.listdir(src_inc):
        if 'vort' in f.lower():
            shutil.copy2(os.path.join(src_inc, f), os.path.join(dst_inc, f))
    print(f'  + Shaders/Includes/ (VORT: {len([f for f in os.listdir(dst_inc)])} файлов)')
# VORT-текстуры
for f in ['vort_BlueNoise.png', 'vort_MLUT.png']:
    cp(os.path.join(MW, 'reshade-shaders', 'Textures', f), os.path.join(txt, f), f'Textures/{f}')

# 5. ReShade.ini (корень) — LoadFromDllMain=addon32 (локальный opengl32, не слой), MV_PROVIDER=2 (VORT)
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
)
with open(os.path.join(SS, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('  + ReShade.ini (LoadFromDllMain=addon32, MV_PROVIDER=2=VORT)')

# 6. ReShadePreset.ini — VORT ПЕРВОЙ, потом Feed
preset = (
    'Techniques=vort_MotionEffects@vort_Motion.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,vort_MotionEffects@vort_Motion.fx\r\n'
)
with open(os.path.join(SS, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('  + ReShadePreset.ini (VORT + Feed)')

# 7. dlss5-feed.cfg — из OpenMW (mode=2, reset_every=0)
cp(os.path.join(MW, 'dlss5-feed.cfg'), os.path.join(SS, 'dlss5-feed.cfg'), 'dlss5-feed.cfg (mode=2, reset_every=0)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(SS)):
    if any(k in f.lower() for k in ['opengl32', 'dlss5', 'reshade', 'host64']):
        p = os.path.join(SS, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
