# -*- coding: utf-8 -*-
# Quake III Arena через ioq3 (64-bit) + DLSS 5 NR — 64-bit OpenGL-путь (паттерн OpenMW)
# ioq3 рендерер грузит GL через SDL264.dll -> opengl32.dll из папки приложения (наш ReShade подхватится)
# ВАЖНО: ванильный GOG-бинарь грузит opengl32.dll из system32 — ReShade не встаёт. Только ioq3.
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR       — папка Quake III (куда будет установлен ioq3/)
#   IOQ3_SRC       — распакованные бинарники ioq3 (ioquake3.x86_64.exe, renderer_opengl1/2_x86_64.dll, SDL264.dll)
#   OPENGL_DONOR   — рабочая 64-bit OpenGL установка (OpenMW): opengl32.dll (ReShade64), dlss5-feed.addon64,
#                    renodx-dlss5.addon64 (4.60!), nvngx-пачка, reshade-shaders, dlss5-feed.cfg
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

Q3 = env('GAME_DIR')
IOQ3_SRC = env('IOQ3_SRC')
MW = env('OPENGL_DONOR')
DEST = os.path.join(Q3, 'ioq3')

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

print('=== ioq3 + DLSS 5 stack ===')

# 1. ioq3 бинарники
os.makedirs(DEST, exist_ok=True)
for f in ['ioquake3.x86_64.exe', 'renderer_opengl1_x86_64.dll', 'renderer_opengl2_x86_64.dll', 'SDL264.dll']:
    cp(os.path.join(IOQ3_SRC, f), os.path.join(DEST, f), f'ioq3/{f}')

# 2. 64-bit OpenGL стек (из OpenMW)
cp(os.path.join(MW, 'opengl32.dll'), os.path.join(DEST, 'opengl32.dll'), 'opengl32.dll (ReShade 64-bit)')
cp(os.path.join(MW, 'dlss5-feed.addon64'), os.path.join(DEST, 'dlss5-feed.addon64'), 'dlss5-feed.addon64 (0.12.0)')
cp(os.path.join(MW, 'renodx-dlss5.addon64'), os.path.join(DEST, 'renodx-dlss5.addon64'), 'renodx-dlss5.addon64 (4.60 — OpenGL!)')
for f in ['nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
    cp(os.path.join(MW, f), os.path.join(DEST, f), f'{f}')

# 3. reshade-shaders (Feed + VORT + инклуды + ReShade.fxh)
src_sh = os.path.join(MW, 'reshade-shaders')
dst_sh = os.path.join(DEST, 'reshade-shaders')
if os.path.exists(dst_sh):
    shutil.rmtree(dst_sh)
shutil.copytree(src_sh, dst_sh)
print('  + reshade-shaders (Feed + VORT + инклуды)')

# 4. ReShade.ini — LoadFromDllMain=renodx+feed (NUL), MV_PROVIDER=2 (VORT)
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
with open(os.path.join(DEST, 'ReShade.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(ini)
print('  + ReShade.ini (renodx+feed, MV_PROVIDER=2, тюнинг NR)')

# 5. ReShadePreset.ini — VORT ПЕРВОЙ, потом Feed
preset = (
    'Techniques=vort_MotionEffects@vort_Motion.fx,DLSS5_Feed@DLSS5_Feed.fx\r\n'
    'TechniqueSorting=DLSS5_Feed@DLSS5_Feed.fx,DLSS5_Feed_Debug@DLSS5_Feed.fx,vort_MotionEffects@vort_Motion.fx\r\n'
)
with open(os.path.join(DEST, 'ReShadePreset.ini'), 'w', encoding='utf-8', newline='') as f:
    f.write(preset)
print('  + ReShadePreset.ini (VORT + Feed)')

# 6. dlss5-feed.cfg
cp(os.path.join(MW, 'dlss5-feed.cfg'), os.path.join(DEST, 'dlss5-feed.cfg'), 'dlss5-feed.cfg (mode=2)')

# 7. 4K в конфиг ioq3 (baseq3/q3config.cfg — общий с ванилью)
q3cfg = os.path.join(Q3, 'baseq3', 'q3config.cfg')
if os.path.exists(q3cfg):
    with open(q3cfg, 'a', encoding='utf-8', newline='') as f:
        f.write('\n// DLSS 5 test: 4K\nseta r_mode "-1"\nseta r_customwidth "3840"\nseta r_customheight "2160"\nseta r_fullscreen "1"\nseta r_swapInterval "0"\nseta cg_fov "105"\n')
    print('  + baseq3/q3config.cfg: 4K (r_mode -1, 3840x2160, FOV 105)')
else:
    print('  ! baseq3/q3config.cfg не найден — 4K пропиши вручную (r_mode -1, r_customwidth 3840, r_customheight 2160)')

print()
print('=== Итог ioq3/ ===')
for f in sorted(os.listdir(DEST)):
    p = os.path.join(DEST, f)
    print(f'  {f}/' if os.path.isdir(p) else f'  {f} ({os.path.getsize(p):,} Б)')
