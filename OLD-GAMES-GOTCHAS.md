# DLSS 5 в старых играх — неочевидное (шпаргалка для Гермеса)

Собрано по факту разбора HL2 RTX, Painkiller, F.E.A.R и Max Payne 2 (2026-09).
Про очевидное (поставь ReShade, feed, host64) — не тут. Тут грабли, которые стоят часов.

## 1. Как ReShade вообще грузится в обёрнутую игру
- Игра **не импортит** `dxgi.dll`. ReShade-dxgi подхватывается так: dgVoodoo/DXVK (или системная d3d9 на WDDM) при создании D3D11-устройства **сама грузит `dxgi.dll` по имени** → поиск в папке exe находит ReShade раньше System32. Ничто в файлах не содержит строку `dxgi.dll` — это нормально.
- Значит: **нет D3D11/DXGI-вывода → ReShade-dxgi не грузится вообще.** Проверять надо не «лежит ли dxgi», а «создаётся ли D3D11-девайс».

## 2. Коллизия базового имени DLL (главная подстава)
- Правило загрузчика Windows: **если модуль с именем `d3d9.dll` уже загружен, любой последующий импорт `d3d9.dll` привязывается к нему**, независимо от пути.
- Многие старые игры при старте делают «DX9-проверку» и грузят **системную** `d3d9.dll` первой. Потом `d3d8to9`/движок импортит `d3d9.dll` → привязывается к **системной**, а папочная dgVoodoo/DXVK d3d9 **молча игнорируется** (даже если лежит рядом).
- Симптом: игра работает, но обёртка «как будто не подключена» (нет водяка dgVoodoo, ReShade не грузится). Удаление папочной d3d9 ничего не меняет.

## 3. dgVoodoo: папка `MS\` — это ОБЁРТКИ dgVoodoo, не Microsoft
- `dgvoodoo2\MS\x86\D3D8.dll`, `D3D9.dll` — это **dgVoodoo-обёртки** (FileDescription «dgVoodoo … Direct3D8/9»), собранные под DXGI/D3D11-вывод. НЕ микрософтовские оригиналы. Легко перепутать и сделать неверный вывод.
- Проверяй личность DLL по `(Get-Item x).VersionInfo.FileDescription/CompanyName`, а не по имени/размеру/md5.

## 4. Некоторые игры отвергают виртуальный адаптер обёртки
- **Max Payne 2**: «requires a Microsoft DirectX 9.0 compatible display adapter». Гейт проверяет **реальный** DX9-адаптер и **отвергает** и dgVoodoo (виртуальная карта `internal3D`), и DXVK. Проходит **только** `crosire d3d8to9 → системная d3d9` (реальная GPU).
- Как отличить гейт от других бед: гейт даёт **явный диалог** игры; краш/несовместимость — **молчаливый вылет**.
- dgVoodooCpl «select GPU» это НЕ лечит на одиночной GPU — гейт всё равно видит виртуальную карту.

## 5. ReShade может КРАШИТЬ движок (а не «не грузиться»)
- MP2: ReShade 6.8.0.2156 падает `0xc0000409` (stack-buffer-overrun) на `IDirect3D9::CreateDevice`, **тот же оффсет при любом способе загрузки** (d3d9-прокси и Vulkan-слой). Та же сборка ReShade в F.E.A.R не падает — **потому что там рантайм D3D11**.
- Вывод: **ReShade на D3D9-рантайме куда хрупче, чем на D3D11.** Одинаковый оффсет краша в разных путях = это адрес репортера GS-failure, а не место реального переполнения.
- Диагноз краша — **журнал Windows, Application, Id 1000**: даёт faulting module + exception code + offset. Незаменимо для «молчаливых вылетов».

## 6. Feed НЕ умеет D3D9
- DLSS5-Feeder поддерживает **D3D11, OpenGL, Vulkan (DXVK)** — D3D9 в списке нет. Старую D3D8/D3D9-игру **обязательно** сначала перевести в D3D11 (dgVoodoo) или Vulkan (DXVK). Чистый D3D9-рантайм для feed бесполезен.
- Отсюда «невозможная» комбинация MP2: гейт пускает только D3D9, а feed требует не-D3D9. Плюс ReShade об D3D9 падает. Три взаимоисключающих барьера → игра нерешаема этим тулингом.

## 7. Версии feed и потребитель
- Половинки feed должны совпадать: `dlss5-feed.addon32` **и** `host64\dlss5-feed-host64.exe` из ОДНОГО релиза (протокол v4→v5 менялся; смешанные молча не стартуют).
- Нейронный потребитель в `host64\` — **`renodx-dlss5.addon64`** (с «5») или `deep-fried-chicken.addon64`. **`renodx-dlss.addon64` (без «5») — это старый DLSS-апскейлер, не NR**, feed его не примет.
- `Deep Fried Chicken` на 32-bit Vulkan (DXVK) — **untested** по докам; для DXVK бери потребителем `renodx-dlss5`.
- В релизе feed есть **`Verify-DLSS5Feeder.ps1`** — гоняй рядом с exe, даёт авторский чеклист (API, версия ReShade, MV-провайдер, потребитель).
- Feed = только **DLAA (1:1)**, не апскейл: он видит уже готовый кадр экранного размера. `NREnableUpscaling=0`.

## 8. Vulkan-слой ReShade — machine-wide, автозагрузка
- `C:\ProgramData\ReShade\ReShade32.json`/`ReShade64.json` в HKLM ImplicitLayers (+ WOW6432Node) грузятся в **любое** Vulkan-приложение. Для DXVK-игры ReShade инжектится сам, отдельная установка не нужна.
- Стоковый ProgramData-ReShade **крашит Remix и часть игр** — глушить на процесс: `set DISABLE_VK_LAYER_reshade_1=1`. Свой изолированный слой — через `enable_environment` (напр. `ENABLE_VK_LAYER_reshade_pk=1`).

## 9. 32-битный Vulkan ICD регистрируется НЕ там, где ждёшь
- NVIDIA прописывает Vulkan-ICD в ключе **дисплейного адаптера**: `HKLM\SYSTEM\...\Class\{4d36e968-...}\0000\VulkanDriverName` (64-бит) и **`VulkanDriverNameWow`** (32-бит) → путь к `nv-vk64/32.json` в DriverStore.
- Классический ключ `HKLM\SOFTWARE\[WOW6432Node\]Khronos\Vulkan\Drivers` при этом может **отсутствовать** — это НЕ значит, что ICD нет. Не делай ложный вывод «32-бит Vulkan сломан» только по нему.

## 10. DXVK d3d8 — сырой
- Для D3D8-игры надёжнее `crosire d3d8to9` (D3D8→D3D9) + DXVK/dgVoodoo на D3D9→(Vulkan/D3D11), чем DXVK-d3d8 напрямую (у DXVK d3d8-поддержка экспериментальная; в MP2 не создал даже свой лог).

## Быстрая диагностика (порядок)
1. Игра стартует? Нет → журнал Windows Id 1000 (faulting module) — краш или гейт.
2. Обёртка активна? → водяк dgVoodoo / DXVK-лог `GAME_d3d9.log` / есть ли D3D11-девайс.
3. ReShade грузится? → `ReShade.log` создаётся; если краш — см. п.5.
4. feed цепляется? → `dlss5-feed.log` строка 1 (версия) + жалобы про host64/потребителя.
5. NR идёт? → `host64\dlss5-feed-host.log`, «600 frames / MV probe / Depth probe».

## Вердикт по MP2 (кейс «когда невозможно»)
Гейт → только реальная d3d9 (D3D9). Feed → не-D3D9. ReShade → падает на D3D9. Три несовместимых требования. Оставлен играбельным на `crosire d3d8to9` без инъекции.

## 11. OpenMW (Morrowind ReBuild) — OpenGL-путь Feeder (работает, 02.09)
- **Схема**: `opengl32.dll` = ReShade64 (тот же бинарник, имя определяет API) + `dlss5-feed.addon64` 0.11.0-beta.2 + `renodx-dlss5.addon64` + полная nvngx-пачка + VORT. OpenMW 0.51.0, 64-bit, OpenGL 4.6, Vulkan-строк в exe нет.
- **renodx-dlss5 4.70 НЕ РАБОТАЕТ на OpenGL-транспорте**: fenced workset pool (новая фича 4.7) не ресайклится → ровно 4 успешных NR-кадра (`NR workset pool exhausted; preserving game output`), потом STANDBY/FAILED. **Ставить 4.60** (без fenced pool).
- **VORT вместо Lumenite**: Lumenite на OpenGL-пути даёт 0% non-zero MV. VORT: `DLSS5_MV_PROVIDER=2`, инклуды класть в `Shaders/Includes/` (БОЛЬШАЯ буква — препроцессор чувствителен к регистру, Lumenite использует `include/`), техника `vort_MotionEffects` ПЕРВОЙ в `Techniques=` (выше DLSS5_Feed).
- **dlss5-feed.cfg**: `reset_every=0`, `rebuild=0`, `warmup_rebuild=0` (диагностические 1/2/180 валят NR).
- **ReShade затирает LoadFromDllMain** (NUL-разделитель) при выходе — патчить при закрытой игре.
- **MV probe 0% non-zero при стоящей камере — норма** (VORT честно считает нули); проверять при движении.
- **Сейвы**: openmw-essimporter НЕ конвертит .ess (unknown record REGN/CONT — неполный); только родные .omwsave. User data dir = корень игры, сейвы в `saves/`.

## 12. Fallout 3 (ReBuild) — Gamebryo 32-bit D3D9, DXVK-путь (работает, 02.09)
- **dgVoodoo НЕ работает** (игра выходит штатно через ~1.2 сек, без краша в журнале — контрольный тест без наших файлов: чистая игра работает). Только **DXVK 3.0.2 x86** (как Black Mesa).
- **Схема**: `D3D9.dll` = DXVK + ReShade через **глобальный слой** (`C:\ProgramData\ReShade\ReShade32.dll`) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 4.70, NRStyle=0). Локальный `dxgi.dll` НЕ нужен (DXVK идёт в Vulkan, dxgi не грузится).
- **ГЛАВНЫЕ ГРАБЛИ — `LoadFromDllMain=dlss5-feed.addon32` ЛОМАЕТ регистрацию через слой**: аддон грузится в DllMain слоя ДО инициализации ReShade-рантайма → `No add-on was registered ... Unloading again` → выгружается, NR-панели нет. **Фикс: УБРАТЬ LoadFromDllMain из ReShade.ini** — аддон подхватывается сканированием папки ПОСЛЕ инициализации рантайма и регистрируется. (В Black Mesa LoadFromDllMain работал — другая последовательность загрузки движка; в FO3/Gamebryo — нет.)
- **`dlss5-feed.cfg` обязателен** (без него аддон не читает конфиг — в логе нет строки `config:`): `enabled=1 mode=2 reset_every=0 warmup_rebuild=0 rebuild=0`.
- **Локальный `vulkan-1.dll` в корне НЕ помог** (DXVK всё равно грузил два модуля: локальный + системный, адреса 0x61bc1760/0x5fed1760) — решающим был именно LoadFromDllMain-фикс.
- **Симптомы при работе**: `vkCreateDevice #1: app asked for 46 extension(s), added 5` + `shared set ready (Vulkan): 3840x2160` + `frame N delivered`; host64: `feature ready: 3840x2160 DLAA` + `frame N evaluated`; host64 сам открывает оверлей (key 36).
- FOSE: в сборке только `fose_1_7.dll`/`fose_1_7ng.dll`, **нет fose_loader.exe** — FOSE-моды не подхватятся, игра запускается.
- **ПОДТВЕРЖДЕНО РАБОТОЙ (02.09)**: NR оценивает кадры, счётчик растёт, оверлей host64 открывается сам. Сейвы: `%USERPROFILE%\Documents\My Games\Fallout3\Saves\` (формат `.fos`, родной; lonebullet Chordian: Save 2 Vault 101, 11 Big Town, 12 Rivet City, 34 Test Labs, 60 Megaton — города с НПС для теста NR). Сборка с модами — ванильные сейвы могут не загрузиться; запасной путь: `coc Megaton` + консоль.

## 13. Deus Ex: Human Revolution — 32-bit нативный D3D11, БЕЗ обёрток (работает, 02.09)
- **Daedalus Engine, 32-bit, нативный D3D11**: `dxhr.exe` НЕ импортирует d3d статически, но **динамически грузит `dxgi.dll` + `d3d11.dll`** (строка `CreateDXGIFactory` в exe) → ReShade-dxgi (x86) подхватывается при создании D3D11-устройства. **Обёртки (dgVoodoo/DXVK) НЕ нужны** — в отличие от F.E.A.R/FO3.
- **Схема**: `dxgi.dll` (ReShade x86) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 4.70, NRStyle=0) + Lumenite (`DLSS5_MV_PROVIDER=3`, Kernel ВЫШЕ Feed). `LoadFromDllMain=dlss5-feed.addon32` РАБОТАЕТ (локальный dxgi, не слой — FO3-грабли не применимы).
- Путь: папка игры (Steam-репак, steam_appid 28050). Ярлык «Deus Ex Human Revolution - DLSS 5» → dxhr.exe.
- **Диагностика API**: если exe не импортирует d3d — искать строки `dxgi.dll`/`d3d11.dll`/`CreateDXGIFactory` в бинарнике (динамическая загрузка = ReShade-dxgi подхватится).

## 14. Quake III Arena — GOG грузит system32 opengl32, нужен ioq3 (работает, 03.09)
- **ГЛАВНАЯ ГРАБЛЯ**: GOG-версия грузит `opengl32.dll` из **system32**, игнорируя локальный (подтверждено модулями процесса через 32-bit PowerShell). ReShade не загружается вообще — `ReShade.log` не создаётся, ini не переписывается. Это известный кейс на ReShade-форуме: «quake3 always tries to use system32\opengl32.dll».
- **Фикс: ioq3** (ioquake3.org, 64-bit). Рендерер грузит GL через `SDL264.dll` → `opengl32.dll` из папки приложения → ReShade подхватывается. Схема = OpenMW-паттерн: `opengl32.dll` (ReShade64) + `dlss5-feed.addon64` + `renodx-dlss5.addon64` **4.60** + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=renodx-dlss5.addon64\x00dlss5-feed.addon64\x00` (NUL).
- **Проверка**: `feature 18 created via the signed snippet after DLSS/DLAA for NR input 3840x2160`, `inline feature 18 evaluation succeeded (count=1 → count=60)`, MV probe 100% non-zero.
- **4K**: `baseq3/q3config.cfg` — `r_mode "-1"`, `r_customwidth 3840`, `r_customheight 2160`, `r_fullscreen 1`, `cg_fov 105`.
- **Меню ReShade может пропадать через 5-7 сек** (DirectInput 3 хуки) — известный кейс; фикс `RESHADE_DISABLE_INPUT_HOOK=1` (но тогда клики в оверлее не работают).
- **«Abnormal Exit» диалог ioq3** при некорректном выходе — «Нет» сохраняет настройки.

## 15. Serious Sam: The First Encounter — 32-bit OpenGL, 4K через конфиг (работает, 03.09)
- **Схема**: `opengl32.dll` = ReShade x86 (имя файла определяет API) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`). `LoadFromDllMain=dlss5-feed.addon32` РАБОТАЕТ (локальный opengl32, не слой).
- **4K без модов**: движок перечисляет режимы через `EnumDisplaySettingsA` → `Scripts\PersistentSymbols.ini`: `sam_iScreenSizeI=3840`, `sam_iScreenSizeJ=2160`, `sam_bWideScreen=0`, `plr_fFOV=105`.
- **«Widescreen» в меню — это letterbox, НЕ растяжение** (GOG-форум: «dont enable the widescreen option at all. just edit the screensize and fov»). Картинка «обрезана сверху/снизу» = включённый Widescreen → `sam_bWideScreen=0`.
- **DPI**: exe не DPI-aware (AppliedDPI=120 при 125% масштабе) → картинка смещается вниз/вправо. Фикс: `HIGHDPIAWARE` через AppCompatFlags (`fix_ss_dpi.ps1`).
- **ReShade умирает при смене видеорежима в меню** (`game device destroyed; shutting down` — пересоздание GL-контекста убивает стек). Разрешение выставлять в конфиге ДО запуска, в меню не трогать.
- **CD-check**: GOG-версия просит диск (`PLEASE INSERT GAME CD?` + `GetDriveTypeA`). MDF→ISO конвертация (8-байт заголовок Alcohol + сектора 2352→2048), монтирование через Mount-DiskImage как DRIVE_CDROM проходит.
- **Steamify-патч** (archive.org, `ss-tfe-steamifyupdate`) — Steam-бинарники с Hor+ FOV, чинит растяжение/сдвиг.

## 16. Far Cry 2004 — CryEngine 1, D3D9 → DXVK (работает, 03.09)
- **Схема** = Fallout 3-паттерн: `D3D9.dll` = DXVK 3.0.2 x86 + глобальный Vulkan-слой ReShade + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.70** + nvngx) + Lumenite (`MV_PROVIDER=3`).
- **ReShade.ini БЕЗ LoadFromDllMain** (слой-путь, FO3-грабли — аддон не регистрируется через слой).
- **32-bit лаунчер** `FarCry.exe` (32 КБ, без импортов) — рендереры `XRenderD3D9.dll`/`XRenderOGL.dll` (оба 32-bit), `system.cfg` → D3D9. WidescreenFix (version.dll + .asi) не конфликтует.
- **4K**: DXVK отдаёт все режимы EnumDisplaySettings — в меню игры выбирается 3840×2160.

## 17. Jedi Knight: Jedi Academy — 32-bit OpenGL, тот же id Tech 3 (работает, 03.09)
- **Схема** = Serious Sam: `opengl32.dll` (ReShade x86) + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=dlss5-feed.addon32`.
- **В отличие от Quake III**: GOG-версия JA грузит ЛОКАЛЬНЫЙ opengl32.dll (проверено ReShade.log: `loaded from '...\GameData\opengl32.DLL'`) — ioq3/OpenJK не нужен.
- **Стек в `GameData\`** (рядом с jamp.exe/jasp.exe), не в корне.
- **4K**: `base\jaconfig.cfg` (SP) + `base\jampconfig.cfg` (MP) — `r_mode "-1"`, `r_customwidth 3840`, `r_customheight 2160`, `cg_fov 105`.
- **renodx 4.60** (не 4.70) — OpenGL-транспорт, fenced pool (см. п.11).

## 18. Riddick: Assault on Dark Athena (GOG, Starbreeze/Ogier, 32-bit OpenGL) — запуск, 4K, DLSS 5 (работает, 04.09)
- **Стартовое ЗАВИСАНИЕ (не краш!) на современных NVIDIA** (RTX 5070 Ti проверено): GLSL bias-синтаксис в `System\GL\HLInclude_GLSL.xrg` — `texture2D(_tex,_st,_bias)`/`textureCube(_tex,_str,_bias)` современный драйвер не компилит. **Фикс**: убрать `,_bias` из тела обеих функций `tex2DBias`/`texCubeBias` (сигнатуру не трогать). Это п. «Game crashes at startup on modern Nvidia» на PCGW (`CRenderContextGL::GLSL_LoadSrc`, `MRndrGL_GLSL.cpp(829)`).
- **Симптом запуска-до-фикса**: процесс жив, окно есть, но не отвечает → в журнале Application **Hang 1002**, а НЕ Application Error 1000. Молчаливых крашей не даёт — верь Hang-событию.
- **4K: ТОЛЬКО `VID_MODE=desktop`** в `%LOCALAPPDATA%\Atari\The Chronicles of Riddick - Assault on Dark Athena\Environment.cfg` (windowed, размер десктопа; рендерит 3840×2071 — заголовок окна). Старт с `VID_MODE=3840 2160 32 144` = чёрное окно ~1600×1024 + тихий вылет (движок не находит точный режим в списке драйвера, падает в фолбэк). Меню применяет 4K, но движок молча грузит ближайший поддерживаемый режим — картинка остаётся не-4K (WSGF: «altering the line to an unsupported resolution results in the game loading the closest officially supported resolution»).
- **Фолбэк-улика**: после неудачного старта игра переписывает `VID_MODE` на `1600 1024 32 120`, а `VID_DWIDTH/VID_DHEIGHT` оставляет как есть (сама не обновляет при смене режима — глюк движка).
- **`VID_PIXELASPECT=1.333333` (4:3)** застревает от старого фолбэка → искажённые пропорции. Лечится `VID_PIXELASPECT=1.000000` (Normal; Auto растягивает — WSGF-тред).
- **Маркер успеха**: после первого удачного входа в меню появляется `GAME_LASTVALIDPROFILE=xx` — признак, что игра прошла инициализацию графики.
- **DLSS 5-схема** = Serious Sam-паттерн (32-bit OpenGL): `opengl32.dll` = ReShade x86 (RndrGL.dll статически импортирует opengl32 — перехват гарантирован) + `dlss5-feed.addon32` (0.11.0-beta.2) + `host64\` (renodx-dlss5 **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), `LoadFromDllMain=dlss5-feed.addon32` РАБОТАЕТ (локальный opengl32, не слой). Стек в `System\Win32_x86\`.
- **`NRStyle=2` в host64/ReShade.ini → чёрный экран при включении фида** (32-bit схемы): ставить `NRStyle=0` (блок тюнинга с NRStyle=2 — для 64-bit схем).
- **Проверка**: `dlss5-feed.log` — `shared set ready (OpenGL): 3840x2071` + `frame N delivered`; `host64\dlss5-feed-host.log` — `feature ready: 3840x2071 DLAA` + `frame N evaluated`; `host64\ReShade.log` — `feature 18 created via the signed snippet` + `inline feature 18 evaluation succeeded`. Безвредные артефакты: `Failed to find NVSDK_NGX_D3D12_EvaluateFeature_C` (evaluation идёт через fallback) + WARN про reshade-shaders в host64 (эффекты не нужны — только аддон).
- Свойства exe: `HIGHDPIAWARE` в AppCompatFlags стоит (и без него DPI-скейлинг ломает разрешения — Steam-тред про 4K ссылается на Override High DPI). Железо не проверяет — это не MP2-гейт.

## 19. BloodRayne 2 Terminal Cut (GOG, 2004→2026) — 32-bit D3D8→D3D9 бандл-мост → DXVK (работает, 04.09)
- **Схема** = Fallout 3-паттерн: `D3D9.dll` = DXVK 3.0.2 x86 + глобальный Vulkan-слой ReShade + `dlss5-feed.addon32` + `host64\` (renodx-dlss5 **4.70** + nvngx) + Lumenite (`MV_PROVIDER=3`). ReShade.ini БЕЗ LoadFromDllMain (слой-путь).
- **Бандл-обёртка**: кастомная `d3d8.dll` (279 КБ) в корне импортирует `d3d9.dll` — Terminal Cut конвертирует D3D8→D3D9 нативно, поэтому перехват идёт через d3d9 от обёртки. d3d8.dll НЕ заменять.
- **Проверка**: `feature 18 created via the signed snippet` + `inline feature 18 evaluation succeeded` (host64/ReShade.log), `frame N evaluated` (host64 log), 16k+ кадров. Подтверждено пользователем 04.09 («бладрейн все хорошо»).

## 20. Dark Messiah: Might and Magic (2006, Source, RUNE) — 32-bit D3D9 → DXVK (работает, 04.09)
- **Схема** = Fallout 3-паттерн: `D3D9.dll` = DXVK 3.0.2 x86 **в корень И в bin/** (Source грузит GameBin первым) + слой + addon32 + host64 (renodx 4.70) + Lumenite. БЕЗ LoadFromDllMain.
- **Запуск**: `mm.exe` — лаунчер, обязательные args `-novid +map_background +exec dm.cfg`.
- **Проверка**: feature 18 + 54k оценок (host64 log), 4K 3840×2160.

## 21. DOOM 2016 (GOG) — 64-bit Vulkan, БЕЗ host64 (работает, 04.09)
- **Схема**: `DOOMx64vk.exe` (Vulkan) + глобальный слой + `dlss5-feed.addon64` + `renodx-dlss5.addon64` 4.70 + Lumenite (`MV_PROVIDER=3`). **host64 НЕ нужен** — addon64 сам создаёт D3D12-устройство (64-bit путь).
- **LoadFromDllMain=renodx-dlss5.addon64** работает (слой-путь, но аддон 64-bit регистрируется — в отличие от addon32 через слой).
- **v0.13.1-beta.1 НЕ ставить** (регрессия CreateFeature 0xC0000005, зависание) — только v0.11.0-beta.2 (md5 addon64 `3140914fbb0f`).
- **Проверка**: feature 18 + evaluation succeeded (ReShade.log в корне, не host64).

## 22. Half-Life 2 (Steam) — 32-bit D3D11, БЕЗ обёрток (работает, 04.09)
- **Схема**: `dxgi.dll` = ReShade x86 + `dlss5-feed.addon32` + `host64\` (renodx 4.70) + Lumenite (`MV_PROVIDER=3`). LoadFromDllMain=addon32 (локальный dxgi, не слой).
- **Source 2013 грузит D3D11 динамически** (ReShade.log: `Redirecting CreateDXGIFactory1`, `Installing delayed hooks for d3d11.dll (Just loaded via LoadLibrary)`) — dgVoodoo/DXVK НЕ нужны, в отличие от HL2-классики.
- **Проверка**: `shared set ready: 3840x2160 (100%)` + `frame N delivered` (dlss5-feed.log), `frame N evaluated` (host64 log). Подтверждено 04.09: frame 14400 evaluated.
- **Питфолл**: `mode=1` — транспортный тест (копирует кадр БЕЗ NGX) — выглядит как «работает», но NR не идёт. Всегда проверять host64-лог на `transport-only` и `mode=2` в cfg.

## 23. Серия NFS (Underground / Underground 2 / Most Wanted 2005) — 32-bit D3D9 → DXVK (работает, 04.09)
- **Схема** = Fallout 3-паттерн: `D3D9.dll` = DXVK 3.0.2 x86 + глобальный Vulkan-слой ReShade + `dlss5-feed.addon32` + `host64\` (renodx 4.70) + Lumenite (`MV_PROVIDER=3`). ReShade.ini БЕЗ LoadFromDllMain (слой-путь).
- **Все три — 32-bit D3D9** (`Direct3DCreate9` в exe, динамическая загрузка). UG/UG2 имеют строки d3d8.dll + d3d9.dll, MW — только d3d9.dll.
- **Проверка**: `shared set ready (Vulkan): 3840x2160` + `feature ready: 3840x2160 DLAA` + `frame N evaluated` (host64 log, DLSS GPU ~16.3 ms/frame). Подтверждено 04.09: UG frame 19800, UG2 frame 32400, MW frame 18000.
- **Сейвы — в неожиданных местах**: UG → `C:\ProgramData\NFS Underground` (файлы профиля `<имя>.ugd` + `<имя>.cfg/.opt`); UG2 → `%LOCALAPPDATA%\NFS Underground 2` (слоты — ПАПКИ `<имя>\<имя>`, `NAME DVD 1\NAME DVD 1`); MW → `Documents\NFS Most Wanted\<имя>\`. Игра при первом запуске создаёт свой профиль (имя из ввода) — переименовать скачанные сейвы под него.
- **NFS UG: разрешение — индекс режима** (`RES: N` в `<профиль>.cfg` = индекс EnumDisplaySettings: 0 = 640×480@59, 789 = 3840×2160@60). exe уже пропатчен под 4K (uniws: `mov eax,3840; mov esi,2160` — сигнатура 640×480 отсутствует), но игра всё равно стартует в 640×480 — разрешение выбирать в меню игры (Options → Display).
- **NFS MW: widescreen-фикс** — `dinput8.dll` (обёртки D3D8/D3D9/DInput, стиль ThirteenAG) + `scripts\NFSMW2005_widescreen_fix.asi` + `scripts\nfsmw_res.ini` (ResX/ResY = 3840/2160). UG/UG2 — ThirteenAG WidescreenFixesPack (`dinput8.dll` + `scripts\*.asi`), 4K через меню игры.
- **uniws.exe** в UG/UG2 — Universal Widescreen Patcher (GUI, патчит exe по сигнатурам из patches.ini); exe уже пропатчены.

## 24. DOOM 3 BFG Edition — 32-bit OpenGL (работает, 04.09)
- **Схема** = Serious Sam-паттерн: `opengl32.dll` = ReShade x86 + `dlss5-feed.addon32` + `host64\` (renodx **4.60** + nvngx) + VORT (`MV_PROVIDER=2`), LoadFromDllMain=addon32.
- **Проверка**: `shared set ready (OpenGL): 3840x2160` + `frame N evaluated` (host64 log, frame 30600). Подтверждено 04.09.

## 25. Mass Effect Legendary Edition (ME1/ME2/ME3) — 64-bit D3D11, БЕЗ host64 (работает, 02.09)
- **Схема**: `dxgi.dll` = ReShade x64 + `dlss5-feed.addon64` + `renodx-dlss5.addon64` 4.70 + Lumenite (`MV_PROVIDER=3`). **host64 НЕ нужен** — 64-bit путь (addon64 сам создаёт D3D12-устройство).
- **Проверка**: `frame N delivered (3840x2160)` + MV probe 100% non-zero (dlss5-feed.log). Подтверждено 02.09: frame 40200.
