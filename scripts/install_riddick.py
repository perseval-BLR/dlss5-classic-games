# -*- coding: utf-8 -*-
# The Chronicles of Riddick: Assault on Dark Athena (GOG, 2009) — DLSS 5 NR, 32-bit OpenGL → Feeder
# Паттерн: Serious Sam (32-bit OpenGL: opengl32 = ReShade x86 + addon32 + host64 + VORT)
#
# Схема:
#   opengl32.dll = ReShade x86 (имя файла определяет API; RndrGL.dll статически импортирует opengl32)
#   dlss5-feed.addon32 (0.11.0-beta.2) + host64\ (renodx-dlss5 4.60 + nvngx-пачка)
#   VORT (MV_PROVIDER=2) — Lumenite на OpenGL даёт 0% векторов
#   renodx 4.60 — 4.70 не работает на OpenGL-транспорте (fenced pool)
#   NRStyle=0 в host64/ReShade.ini — NRStyle=2 даёт чёрный экран на 32-bit схемах
#
# ВАЖНО (4K): разрешение задаётся ТОЛЬКО через %LOCALAPPDATA%\Atari\The Chronicles of Riddick -
# Assault on Dark Athena\Environment.cfg. VID_MODE=desktop (windowed, размер десктопа) — рабочий
# способ получить 4K: старт с VID_MODE=3840 2160 32 144 = чёрное окно ~1600x1024 + тихий вылет
# (движок не находит точный режим). VID_DWIDTH/VID_DHEIGHT=3840/2160.
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR       — папка System\Win32_x86 игры (куда ставится стек)
#   X86_DONOR      — рабочая 32-bit OpenGL установка (Serious Sam\Bin): opengl32.dll (ReShade x86),
#                    dlss5-feed.addon32, host64\ (dlss5-feed-host64.exe, dxgi.dll ReShade64, nvngx-пачка)
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

RD = env('GAME_DIR')
SS = env('X86_DONOR')         # 32-bit OpenGL донор: opengl32, addon32, host64 exe, nvngx

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

print('=== Riddick: AODA DLSS 5 stack (32-bit OpenGL) ===')

# 1. opengl32.dll = ReShade x86 (4,398,080 Б — тот же бинарник, имя определяет API)
cp(os.path.join(SS, 'opengl32.dll'), os.path.join(RD, 'opengl32.dll'), 'opengl32.dll (ReShade x86)')

# 2. Feeder addon32 (0.11.0-beta.2)
cp(os.path.join(SS, 'dlss5-feed.addon32'), os.path.join(RD, 'dlss5-feed.addon32'), 'dlss5-feed.addon32 (0.11.0-beta.2)')

# 3. host64/ — полный комплект
host = os.path.join(RD, 'host64')
cp(os.path.join(SS, 'host64', 'dlss5-feed-host64.exe'), os.path.join(host, 'dlss5-feed-host64.exe'), 'host64/dlss5-feed-host64.exe (0.11.0-beta.2)')
cp(os.path.join(SS, 'host64', 'dxgi.dll'), os.path.join(host, 'dxgi.dll'), 'host64/dxgi.dll (ReShade 64-bit)')
cp(os.path.join(SS, 'host64', 'renodx-dlss5.addon64'), os.path.join(host, 'renodx-dlss5.addon64'), 'host64/renodx-dlss5.addon64 (4.60 — OpenGL!)')
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    cp(os.path.join(SS, 'host64', f), os.path.join(host, f), f'host64/{f}')

# host64/ReShade.ini — тюнинг (NRStyle=0 — критично для 32-bit схем!)
with open(os.path.join(host, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write('[GENERAL]\r\nLoadFromDllMain=renodx-dlss5.addon64\r\nEffectSearchPaths=.\\reshade-shaders\\Shaders\\**\r\nTextureSearchPaths=.\\reshade-shaders\\Textures\\**\r\n[INPUT]\r\nKeyOverlay=36,0,0,0\r\n[RenoDX.DLSS5]\r\nNRStyle=0\r\nEnableHooks=2\r\nNeuralUplift=1\r\nNREnableUpscaling=0\r\nNRToggleKey=0\r\nNRScreenshotKey=0\r\nNRPreset=1\r\nNRIntensity=2\r\nNRGlobalTone=1.84\r\nNRLocalTone=1.79\r\nNRLocalStructure=1.64\r\nNRSkinStructure=1\r\nNRUICorrection=1\r\nNRPaperWhiteScale=3.224\r\n')
print('  + host64/ReShade.ini (тюнинг, NRStyle=0)')

# 4. reshade-shaders: DLSS5_Feed.fx + VORT + инклуды + ReShade.fxh/UI.fxh
shd = os.path.join(RD, 'reshade-shaders', 'Shaders')
txt = os.path.join(RD, 'reshade-shaders', 'Textures')
cp(os.path.join(SS, 'reshade-shaders', 'Shaders', 'DLSS5_Feed.fx'), os.path.join(shd, 'DLSS5_Feed.fx'), 'Shaders/DLSS5_Feed.fx (0.11.0-beta.2)')
cp(os.path.join(SS, 'reshade-shaders', 'Shaders', 'vort_Motion.fx'), os.path.join(shd, 'vort_Motion.fx'), 'Shaders/vort_Motion.fx')
cp(os.path.join(SS, 'reshade-shaders', 'Shaders', 'ReShade.fxh'), os.path.join(shd, 'ReShade.fxh'), 'Shaders/ReShade.fxh')
cp(os.path.join(SS, 'reshade-shaders', 'Shaders', 'ReShadeUI.fxh'), os.path.join(shd, 'ReShadeUI.fxh'), 'Shaders/ReShadeUI.fxh')
# VORT-инклуды (регистр Includes/ — БОЛЬШАЯ буква!)
src_inc = os.path.join(SS, 'reshade-shaders', 'Shaders', 'Includes')
dst_inc = os.path.join(shd, 'Includes')
if os.path.isdir(src_inc):
    os.makedirs(dst_inc, exist_ok=True)
    for f in os.listdir(src_inc):
        if 'vort' in f.lower():
            shutil.copy2(os.path.join(src_inc, f), os.path.join(dst_inc, f))
    print(f'  + Shaders/Includes/ (VORT: {len([f for f in os.listdir(dst_inc)])} файлов)')
# VORT-текстуры
for f in ['vort_BlueNoise.png', 'vort_MLUT.png']:
    cp(os.path.join(SS, 'reshade-shaders', 'Textures', f), os.path.join(txt, f), f'Textures/{f}')

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
with open(os.path.join(RD, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('  + ReShade.ini (LoadFromDllMain=addon32, MV_PROVIDER=2=VORT)')

# 6. ReShadePreset.ini — VORT ПЕРВОЙ, потом Feed
preset = (
    'Techniques=vort_MotionEffects@vort_Motion.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,vort_MotionEffects@vort_Motion.fx\r\n'
)
with open(os.path.join(RD, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('  + ReShadePreset.ini (VORT + Feed)')

# 7. dlss5-feed.cfg — из донора (mode=2)
cp(os.path.join(SS, 'dlss5-feed.cfg'), os.path.join(RD, 'dlss5-feed.cfg'), 'dlss5-feed.cfg (mode=2)')

print()
print('=== Итог ===')
for f in sorted(os.listdir(RD)):
    if any(k in f.lower() for k in ['opengl32', 'dlss5', 'reshade', 'host64']):
        p = os.path.join(RD, f)
        print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p)} Б)')
