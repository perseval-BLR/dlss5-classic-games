# -*- coding: utf-8 -*-
# Quake III Arena + Jedi Knight: Jedi Academy — DLSS 5 NR, 32-bit OpenGL → Feeder
# Паттерн: Serious Sam (проверен 03.09: shared set ready 3840x2160, кадры доставляются)
# Стек копируется из рабочей установки Serious Sam (opengl32 + addon32 + host64 + VORT + renodx 4.60)
#
# ВАЖНО про Quake III: ванильный GOG-бинарь грузит opengl32.dll из system32 — ReShade не встаёт.
# Для Quake III используй ioq3 (install_ioq3.py). Этот скрипт ставит стек в папку ванильной игры
# (работает для Jedi Academy; для Quake III — только если игра грузит локальный opengl32).
#
# Использование (переменные окружения, все обязательны):
#   GAME_DIR_Q3  — папка Quake III (куда будет установлен стек)
#   GAME_DIR_JA  — папка Jedi Academy (GameData, где лежат jamp.exe/jasp.exe)
#   X86_DONOR    — рабочая 32-bit OpenGL установка (Serious Sam): opengl32.dll (ReShade x86),
#                  dlss5-feed.addon32, host64\ (exe + ReShade64 + renodx 4.60 + nvngx),
#                  reshade-shaders (VORT), ReShade.ini, ReShadePreset.ini, dlss5-feed.cfg
import os, shutil

def env(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f'!!! Задай {name} (переменная окружения)')
    if not os.path.exists(v):
        raise SystemExit(f'!!! НЕТ ПУТИ: {name}={v}')
    return v

SS = env('X86_DONOR')  # донор: проверенный 32-bit OpenGL стек
Q3 = env('GAME_DIR_Q3')
JA = env('GAME_DIR_JA')

def cp(src, dst, name):
    if not os.path.exists(src):
        print(f'  !!! НЕТ ИСТОЧНИКА: {src}')
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f'  + {name}')

def install_stack(dst_dir, label):
    print(f'===== {label} =====')
    # 1. opengl32.dll (ReShade x86)
    cp(os.path.join(SS, 'opengl32.dll'), os.path.join(dst_dir, 'opengl32.dll'), 'opengl32.dll (ReShade x86)')
    # 2. Feeder addon32
    cp(os.path.join(SS, 'dlss5-feed.addon32'), os.path.join(dst_dir, 'dlss5-feed.addon32'), 'dlss5-feed.addon32 (0.12.0)')
    # 3. host64/ (полный комплект)
    host = os.path.join(dst_dir, 'host64')
    for f in ['dlss5-feed-host64.exe', 'dxgi.dll', 'renodx-dlss5.addon64', 'ReShade.ini',
              'nvngx_dlss.dll', 'nvngx_dlssd.dll', 'nvngx_dlssg.dll', 'nvngx_dlssnr.dll']:
        cp(os.path.join(SS, 'host64', f), os.path.join(host, f), f'host64/{f}')
    # 4. reshade-shaders (Feed + VORT + инклуды + ReShade.fxh)
    src_sh = os.path.join(SS, 'reshade-shaders')
    dst_sh = os.path.join(dst_dir, 'reshade-shaders')
    if os.path.exists(dst_sh):
        shutil.rmtree(dst_sh)
    shutil.copytree(src_sh, dst_sh)
    print('  + reshade-shaders (Feed + VORT + инклуды)')
    # 5. ReShade.ini
    cp(os.path.join(SS, 'ReShade.ini'), os.path.join(dst_dir, 'ReShade.ini'), 'ReShade.ini (addon32, MV_PROVIDER=2)')
    # 6. ReShadePreset.ini
    cp(os.path.join(SS, 'ReShadePreset.ini'), os.path.join(dst_dir, 'ReShadePreset.ini'), 'ReShadePreset.ini (VORT + Feed)')
    # 7. dlss5-feed.cfg
    cp(os.path.join(SS, 'dlss5-feed.cfg'), os.path.join(dst_dir, 'dlss5-feed.cfg'), 'dlss5-feed.cfg (mode=2)')
    print()

# === Quake III: стек в корень (рядом с quake3.exe) ===
install_stack(Q3, 'Quake III Arena')

# === Jedi Academy: стек в GameData (рядом с jamp.exe/jasp.exe) ===
install_stack(JA, 'Jedi Knight: Jedi Academy')

# === 4K в конфиги ===
print('===== 4K в конфиги =====')

# Quake III: baseq3/q3config.cfg
q3cfg = os.path.join(Q3, 'baseq3', 'q3config.cfg')
q3_4k = (
    '// DLSS 5 test: 4K\n'
    'seta r_mode "-1"\n'
    'seta r_customwidth "3840"\n'
    'seta r_customheight "2160"\n'
    'seta r_fullscreen "1"\n'
    'seta r_swapInterval "0"\n'
    'seta cg_fov "105"\n'
)
with open(q3cfg, 'w', encoding='utf-8', newline='') as f:
    f.write(q3_4k)
print('  + Quake III: q3config.cfg (3840x2160, r_mode -1, FOV 105)')

# Jedi Academy: base/jaconfig.cfg (SP) + base/jampconfig.cfg (MP)
jacfg = os.path.join(JA, 'base', 'jaconfig.cfg')
ja_4k = (
    '// DLSS 5 test: 4K\n'
    'seta r_mode "-1"\n'
    'seta r_customwidth "3840"\n'
    'seta r_customheight "2160"\n'
    'seta r_fullscreen "1"\n'
    'seta r_swapInterval "0"\n'
    'seta cg_fov "105"\n'
)
with open(jacfg, 'w', encoding='utf-8', newline='') as f:
    f.write(ja_4k)
print('  + Jedi Academy: jaconfig.cfg (3840x2160, r_mode -1, FOV 105)')

# jampconfig.cfg (MP) — создаём, если нет
jampcfg = os.path.join(JA, 'base', 'jampconfig.cfg')
if not os.path.exists(jampcfg):
    with open(jampcfg, 'w', encoding='utf-8', newline='') as f:
        f.write(ja_4k)
    print('  + Jedi Academy: jampconfig.cfg создан (3840x2160)')
else:
    print('  = Jedi Academy: jampconfig.cfg уже есть, не трогаю')

print()
print('Готово.')
