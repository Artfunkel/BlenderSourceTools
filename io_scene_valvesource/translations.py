#coding=utf-8
_languages = ['ru']

_data = {
'controllers_simple_tip': {
	'en': "Generate one flex controller per shape key",
	'ru': "Создавать по контроллеру на каждый ключ формы",
},
'action_selection_filter_tip': {
	'en': "All actions that match the armature's filter term and have users",
	'ru': "Все действия, которые подходят под фильтр имён действий и где-либо используются",
},
'curve_poly_side_fwd': {
	'en': "Forward (outer) side",
	'ru': "Внешняя сторона",
},
'action_selection_current_tip': {
	'en': "The armature's currently assigned action or NLA tracks",
	'ru': "Текущее действие (или нелинейная анимация) скелета",
},
'subdir_tip': {
	'en': "Optional path relative to scene output folder",
	'ru': "Куда экспортировать? (Необязательно; по умолчанию экспортируется в ту же папку, где находится .blend-файл) ",
},
'controllers_mode': {
	'en': "DMX Flex Controller generation",
	'ru': "Генерация контроллеров лицевой анимации (DMX)",
},
'scene_export': {
	'en': "Scene Export",
	'ru': "Экспорт всей сцены",
},
'shape_stereo_mode_tip': {
	'en': "How stereo split balance should be defined",
	'ru': "Способ разделения объекта на левую и правую части для стерео-контроллеров",
},
'bone_rot_legacy': {
	'en': "Legacy rotation",
	'ru': "Обратная совместимость вращения костей",
},
'controllers_advanced_tip': {
	'en': "Insert the flex controllers of an existing DMX file",
	'ru': "Вставить блок контроллеров лицевой анимации",
},
'triangulate_tip': {
	'en': "Avoids concave DMX faces, which are not supported by studiomdl",
	'ru': "Избегать вогнутых полигонов в DMX-файлах (не поддерживается studiomdl)",
},
'action_filter': {
	'en': "Action Filter",
	'ru': "Фильтр действий",
},
'action_filter_tip': {
	'en': "Actions with names matching this filter pattern and have users will be exported",
	'ru': "Будут эксортированы только те действия, имена которых подходят под этот фильтр, и которые где-либо используются",
},
'shape_stereo_sharpness_tip': {
	'en': "How sharply stereo flex shapes should transition from left to right",
	'ru': "Насколько резко будет осуществляться переход между левой и правой частью объекта",
},
'shape_stereo_mode': {
	'en': "DMX stereo split mode",
	'ru': "Разделение на левую и правую части для стерео-контрлолеров (DMX)",
},
'dummy_bone': {
	'en': "Implicit motionless bone",
	'ru': "\"Пустая\" недвижимая кость",
},
'curve_poly_side': {
	'en': "Polygon Generation",
	'ru': "Генерация геометрии",
},
'group_merge_mech': {
	'en': "Merge mechanical parts",
	'ru': "Слить вместе механические части",
},
'action_selection_mode_tip': {
	'en': "How actions are selected for export",
	'ru': "Какие действия экспортировать?",
},
'use_scene_export_tip': {
	'en': "Export this item with the scene",
	'ru': "Экспортировать этот объект при экспорте сцены",
},
'curve_poly_side_back': {
	'en': "Backward (inner) side",
	'ru': "Внутренняя сторона",
},
'bone_rot_legacy_tip': {
	'en': "Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",
	'ru': "Переназначить Y-ось всех костей в Z-ось для обратной совместимости с старыми импортами",
},
'controller_source': {
	'en': "DMX Flex Controller source",
	'ru': "Файл контроллеров лицевой анимации (DMX)",
},
'group_suppress_tip': {
	'en': "Export this group's objects individually",
	'ru': "Экспортировать объекты этой группы по отдельности",
},
'action_selection_current': {
	'en': "Current / NLA",
	'ru': "Текущее действие / Нелинейная анимация",
},
'shape_stereo_sharpness': {
	'en': "DMX stereo split sharpness",
	'ru': "Резкость разделения в стерео-контроллерах",
},
'group_suppress': {
	'en': "Suppress",
	'ru': "\"Пересиливание\"",
},
'shape_stereo_vgroup': {
	'en': "DMX stereo split vertex group",
	'ru': "Группа вешин разделения для стерео-контроллеров",
},
'shape_stereo_vgroup_tip': {
	'en': "The vertex group that defines stereo balance (0=Left, 1=Right)",
	'ru': "Группа вершин для автоматического деления ключей формы на левую и правую часть. 0 = Левая часть, 1 = Правая часть.",
},
'controllers_source_tip': {
	'en': "A DMX file (or Text datablock) containing flex controllers",
	'ru': "DMX-файл или внутренний текст в Blender, содержащий настройки контроллеров лицевой анимации",
},
'curve_poly_side_tip': {
	'en': "Determines which side(s) of this curve will generate polygons when exported",
	'ru': "Указывает, какая сторона (стороны) выделенной кривой будет использоваться для генерации геометрии",
},
'triangulate': {
	'en': "Triangulate",
	'ru': "Преобразовывать все многоугольники в треугольники",
},
'curve_poly_side_both': {
	'en': "Both sides",
	'ru': "Обе стороны",
},
'group_merge_mech_tip': {
	'en': "Optimises DMX export of meshes sharing the same parent bone",
	'ru': "Оптимизиция экспорт объектов, имеющих общих родителей",
},
'action_selection_mode': {
	'en': "Action Selection",
	'ru': "Выбор действия",
},
'shape_stereo_mode_vgroup': {
	'en': "Use a vertex group to define stereo balance",
	'ru': "Использовать группу вершин для разделения стерео-контроллеров",
},
'controllers_mode_tip': {
	'en': "How flex controllers are defined",
	'ru': "Способ задания контроллеров лицевой анимации",
},
'subdir': {
	'en': "Subfolder",
	'ru': "Подпапка",
},
'dummy_bone_tip': {
	'en': "Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)",
	'ru': "Создать кость и привязать к ней вершины, которые не двигаются. (Только SMD.)",
},
'exportpanel_steam': {
	'en': "Steam Community",
	'ru': "Сообщество Steam",
},
'exportables_arm_filter_result': {
	'en': "\"{0}\" actions ({1})",
	'ru': "Фильтр имён действий \"{0}\" на скелете {1}",
},
'exportables_flex_count_corrective': {
	'en': "Corrective Shapes: {0}",
	'ru': "Ключей форм коррекции: {0}",
},
'exportables_curve_polyside': {
	'en': "Polygon Generation:",
	'ru': "Генерация геометрии:",
},
'exportmenu_title': {
	'en': "Source Tools Export",
	'ru': "Экспорт в Source",
},
'exportables_flex_help': {
	'en': "Flex Controller Help",
	'ru': "Помощь по контроллерам лицевой анимации",
},
'exportpanel_title': {
	'en': "Source Engine Export",
	'ru': "Экспорт в Source",
},
'exportables_flex_src': {
	'en': "Controller Source",
	'ru': "Файл настроек контроллеров",
},
'exportmenu_invalid': {
	'en': "Cannot export selection",
	'ru': "Выделенный объект невозможно экспортировать",
},
'qc_title': {
	'en': "Source Engine QC Complies",
	'ru': "Компиляция QC",
},
'exportables_flex_props': {
	'en': "Flex Properties",
	'ru': "Свойства контроллеров лицевой анимации",
},
'exportables_flex_generate': {
	'en': "Generate Controllers",
	'ru': "Сгенерировать контроллеры",
},
'exportables_flex_split': {
	'en': "Stereo Flex Balance:",
	'ru': "Разделение на правую и левую часть:",
},
'exportables_group_mute_suffix': {
	'en': "(suppressed)",
	'ru': "(игнорируется)",
},
'exportmenu_scene': {
	'en': "Scene export ({0} files)",
	'ru': "Экспорт {0} файлов",
},
'exportpanel_dmxver': {
	'en': "DMX Version:",
	'ru': "Версия DMX:",
},
'exportpanel_update': {
	'en': "Check for updates",
	'ru': "Проверить обновления",
},
'exportables_title': {
	'en': "Source Engine Exportables",
	'ru': "Объекты для Source",
},
'exportables_armature_props': {
	'en': "Armature Properties ({0})",
	'ru': "Свойства скелета ({0})",
},
'qc_bad_enginepath': {
	'en': "Invalid Engine Path",
	'ru': "Некорректный путь до папки bin",
},
'exportmenu_selected': {
	'en': "Selected objects ({0} files)",
	'ru': "Выбранные объекты ({0} файлов)",
},
'exportables_group_props': {
	'en': "Group Properties",
	'ru': "Свойства групп",
},
'qc_no_enginepath': {
	'en': "No Engine Path provided",
	'ru': "Не указан путь до папки bin",
},
'exportables_curve_props': {
	'en': "Curve Properties",
	'ru': "Свойства сплайна",
},
'exportables_flex_count': {
	'en': "Shapes: {0}",
	'ru': "Ключей формы: {0}",
},
'bl_info_author': {
	'en': "Tom Edwards (translators: Grigory Revzin)",
	'ru': "Том Эдвардс (переводили: Григорий Ревзин)",
},
'activate_dependency_shapes': {
	'en': "Activate dependency shapes",
	'ru': "Активировать зависимые ключи формы",
},
'settings_prop': {
	'en': "Blender Source Tools settings",
	'ru': "Настройки Blender Source Tools",
},
'bl_info_description': {
	'en': "Importer and exporter for Valve Software's Source Engine. Supports SMD\\VTA, DMX and QC.",
	'ru': "Экспорт и импорт для движка Source. Поддерживаемые форматы: SMD/VTA, DMX, QC.",
},
'export_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx)",
	'ru': "Движок Source (.smd, .vta, .dmx)",
},
'help': {
	'en': "Help",
	'ru': "Помощь",
},
'bl_info_location': {
	'en': "File > Import/Export, Scene properties",
	'ru': "Файл > Импортировать/Экспортировать, свойства сцены",
},
'import_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx, .qc)",
	'ru': "Движок Source (.smd, .vta, .dmx, .qc)",
},
'exporter_report_qc': {
	'en': "{0} files exported and {2} QCs compiled ({3}/{4}) in {1} seconds",
	'ru': "Экспортировано файлов: {0}. Скомпилировано QC-файлов: {2} (движок {3}, мод {4}). Прошло секунд: {1};",
},
'exporter_err_relativeunsaved': {
	'en': "Cannot export to a relative path until the blend file has been saved.",
	'ru': "Невозможно экспортировать по относительному пути, пока файл .blend не сохранён.",
},
'exporter_err_nopolys': {
	'en': "Object {0} has no polygons, skipping",
	'ru': "Пропуск объекта {0}: нет геометрии",
},
'exporter_err_arm_nonuniform': {
	'en': "Armature \"{0}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.",
	'ru': "Скелет {0} масштабирован непропорционально. В движке Source скелет будет работать неправильно.",
},
'exporter_err_vtadist': {
	'en': "Shape \"{0}\" has {1} vertex movements that exceed eight units. Source does not support this!",
	'ru': "Ключ формы \"{0}\" содержит слишком большие перемещения вершин (не больше восмьи единиц!)",
},
'exporter_err_facesnotex_ormat': {
	'en': "{0} faces on {1} did not have a Material or Texture assigned",
	'ru': "{0} полигонам на {1} не присвоен ни материал, ни текстура",
},
'exporter_err_arm_noanims': {
	'en': "Couldn't find any animation for Armature \"{0}\"",
	'ru': "Нет анимации для скелета {0}",
},
'exporter_err_dupeenv_arm': {
	'en': "Armature modifier \"{0}\" found on \"{1}\", which already has a bone parent or constraint. Ignoring.",
	'ru': "Пропуск модификатора \"Скелет\" ({0}) на объекте {1}: он уже имеет кость-родителя или ограничение",
},
'exporter_err_bonelimit': {
	'en': "Exported {0} bones, but SMD only supports {1}!",
	'ru': "Экспортировано {0} костей, но SMD поддерживает только {1}!",
},
'exporter_err_flexctrl_loadfail': {
	'en': "Could not load flex controllers. Python reports: {0}",
	'ru': "Загрузить контроллеры из указанного DMX-файла не удалось. Ошибка Python: {0}",
},
'qc_compile_err_nofiles': {
	'en': "Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.",
	'ru': "Нет QC-файлов, нечего компилировать. Blender Source Tools не генерируют QC-файлы.",
},
'qc_compile_complete': {
	'en': "\"Compiled {0} {1} QCs\"",
	'ru': "Скомпилировано {0} QC для движка {1}.",
},
'exporter_err_shapes_decimate': {
	'en': "Cannot export shape keys from \"{0}\" because it has a '{1}' Decimate modifier. Only Un-Subdivide mode is supported.",
	'ru': "Невзможно экспортировать ключи формы для {0}, потому что активен модификатор \"Аппроксимация\" в режиме {1}. Поддерживается только режим \"Снять подразделение\"",
},
'exporter_err_splitvgroup_undefined': {
	'en': "Object \"{0}\" uses Vertex Group stereo split, but does not define a Vertex Group to use.",
	'ru': "На объекте {0} задан режим стерео-разделения по группе вершин, но не задана группа вершин.",
},
'exporter_err_open': {
	'en': "Could not create {0} file. Python reports: {1}.",
	'ru': "Не удалось создать файл {0}. Ошибка Python: {1}",
},
'qc_compile_title': {
	'en': "Compile QC",
	'ru': "Скомпилировать QC-файл",
},
'exporter_err_noexportables': {
	'en': "Found no valid objects for export",
	'ru': "Не найдено подходящих для экспорта объектов",
},
'exporter_err_flexctrl_missing': {
	'en': "No flex controller defined for shape {0}.",
	'ru': "Для ключа формы {0} не задано ни одного контроллера",
},
'qc_compile_err_compiler': {
	'en': "Could not execute studiomdl from \"{0}\"",
	'ru': "Не удалось запустить studiomdl, проверьте путь: {1}",
},
'exporter_err_facesnotex': {
	'en': "{0} faces on {1} did not have a Texture assigned",
	'ru': "Для {0} граней на объекте {1} не задана текстура",
},
'exporter_err_flexctrl_undefined': {
	'en': "Could not find flex controllers for \"{0}\"",
	'ru': "Не удалось найти контроллеры лицевой анимации для объекта {0}",
},
'exporter_tip': {
	'en': "Export and compile Source Engine models",
	'ru': "Экспортирует и компилирует модели для движка Source",
},
'exporter_prop_scene_tip': {
	'en': "Export all items selected in the Source Engine Exportables panel",
	'ru': "Экспортировать все объекты, заданные в панели \"Объекты для Source\"",
},
'exporter_err_dmxenc': {
	'en': "DMX format \"Model {0}\" requires DMX encoding \"Binary 3\" or later",
	'ru': "Формат DMX-файла \"Model {0}\" требует структуру DMX-файла не более старую, чем \"Binary 3\".",
},
'exporter_prop_group': {
	'en': "Group Name",
	'ru': "Имя группы",
},
'qc_compile_tip': {
	'en': "Compile QCs with the Source SDK",
	'ru': "Компилирует QC-файлы с помощью studiomdl",
},
'exporter_report_suffix': {
	'en': " with {0} Errors and {1} Warnings",
	'ru': " ошибок: {0}, предупреждений: {1}.",
},
'exporter_err_groupempty': {
	'en': "Group {0} has no active objects",
	'ru': "В группе {0} нет активных объектов",
},
'exporter_err_dmxother': {
	'en': "Cannot export DMX. Resolve errors with the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
	'ru': "Невозможно экспортировать DMX-файлы. Проверьте панель \"Экспорт в Source\"",
},
'exporter_prop_group_tip': {
	'en': "Name of the Group to export",
	'ru': "Имя группы для экспорта",
},
'exporter_err_solidifyinside': {
	'en': "Curve {0} has the Solidify modifier with rim fill, but is still exporting polys on both sides.",
	'ru': "На кривой {0} включён модификатор Объёмность с заполнением обода, однако всё равно экспортируется двусторонняя геометрия",
},
'exporter_err_dupeenv_con': {
	'en': "Bone constraint \"{0}\" found on \"{1}\", which already has a bone parent. Ignoring.",
	'ru': "Пропук ограничения кости {0}  на объекте {1}: для неё уже задана кость-родитель.",
},
'exporter_err_unconfigured': {
	'en': "Scene unconfigured. See the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
	'ru': "Требуется скофигурировать сцену для экспорта в Source. Проверьте панель \"Экcпорт в Source\"",
},
'exporter_err_makedirs': {
	'en': "Could not create export folder. Python reports: {0}",
	'ru': "Не удалось создать папку для экспорта. Ошибка Python: {0}",
},
'exporter_err_weightlinks': {
	'en': "{0} verts on \"{1}\" have over 3 weight links. Studiomdl does not support this!",
	'ru': "{0} вершин на объекте {1} привязаны к более чем трём костям. Studiomdl не сможет скомпилировать такой файл..",
},
'exporter_report_menu': {
	'en': "Source Tools Error Report",
	'ru': "Отчёт о ошибках Source Tools",
},
'exporter_report': {
	'en': "{0} files exported in {1} seconds",
	'ru': "Файлов экспортировано: {0}. Прошло секунд: {1};",
},
'exporter_err_groupmuted': {
	'en': "Group {0} is suppressed",
	'ru': "Свойства группы {0} \"пересилены\"",
},
'exporter_title': {
	'en': "Export SMD/VTA/DMX",
	'ru': "Экспорт SMD/VTA/DMX",
},
'qc_compile_err_unknown': {
	'en': "Compile of {0} failed. Check the console for details",
	'ru': "Не удалось скомпилировать QC-файл {0}. Ошибка описана в консоли",
},
'exporter_err_splitvgroup_missing': {
	'en': "Could not find stereo split Vertex Group \"{0}\" on object \"{1}\"",
	'ru': "Не найдена группа веришн {0} для разделения на левую и правую части стерео-контроллеров на объекте {1}",
},
'importer_complete': {
	'en': "Imported {0} files in {1} seconds",
	'ru': "Импортировано файлов: {0}. Прошло секунд: {1}.",
},
'importer_bonemode': {
	'en': "Bone shapes",
	'ru': "Отображение костей",
},
'importer_err_nofile': {
	'en': "No file selected",
	'ru': "Файл не выбран",
},
'importer_err_smd': {
	'en': "Could not open SMD file \"{0}\": {1}",
	'ru': "Невозможно открыть файл {0}. Ошибка Python: {1}",
},
'importer_qc_macroskip': {
	'en': "Skipping macro in QC {0}",
	'ru': "Пропуск QC-команды в файле {0}",
},
'importer_tip': {
	'en': "Imports uncompiled Source Engine model data",
	'ru': "Импортирует промежуточные файлы Source",
},
'importer_title': {
	'en': "Import SMD/VTA, DMX, QC",
	'ru': "Импорт SMD/VTA, DMX, QC",
},
'importer_makecamera': {
	'en': "Make Camera At $origin",
	'ru': "Создать камеру по координатам, указанным в $origin",
},
'importer_bone_parent_miss': {
	'en': "Parent mismatch for bone \"{0}\": \"{1}\" in Blender, \"{2}\" in {3}.",
	'ru': "Не совпадают родители у кости \"{0}\": \"{1}\" в Blender, \"{2}\" в файле \"{3}\".",
},
'importer_makecamera_tip': {
	'en': "For use in viewmodel editing; if not set, an Empty will be created instead",
	'ru': "Помогает в редактировании v_model-ов. Если не задано, будет создан пустой объект",
},
'importer_err_shapetarget': {
	'en': "Could not import shape keys: no valid target object found",
	'ru': "Невозможно импортировать ключи формы: не найден подходящий объект",
},
'importer_rotmode_tip': {
	'en': "Determines the type of rotation Keyframes created when importing bones or animation",
	'ru': "Задаёт тип создаваемых при экспорте ключевых кадров с вращением",
},
'importer_balance_group': {
	'en': "DMX Stereo Balance",
	'ru': "Разделение стерео-контроллеров",
},
'importer_rotmode': {
	'en': "Rotation mode",
	'ru': "Способ задания вращения",
},
'importer_bonemode_tip': {
	'en': "How bones in new Armatures should be displayed",
	'ru': "Как будут выглядеть кости в импортированном скелете?",
},
'importer_err_qci': {
	'en': "Could not open QC $include file \"{0}\" - skipping!",
	'ru': "Пропуск файла \"{0}\" из команды $include: не удалсь открыть.",
},
'importer_up_tip': {
	'en': "Which axis represents 'up' (ignored for QCs)",
	'ru': "Какая из осей соответствует направлению \"вврех\"?",
},
'importer_err_unmatched_mesh': {
	'en': "{0} VTA vertices ({1}%) were not matched to a mesh vertex! An object with a vertex group has been created to show where the VTA file's vertices are.",
	'ru': "{0} вершин ({1}%) не удалось привязать к объекту при импорте VTA. Создан объект с группой вершин, показывающей, где заданные в VTA вершины.",
},
'importer_name_nomat': {
	'en': "UndefinedMaterial",
	'ru': "UndefinedMaterial",
},
'importer_append_tip': {
	'en': "Whether imports will latch onto an existing armature or create their own",
	'ru': "Будут ли импортируемые модели добавляться к существующему скелету или будет создан новый скелет?",
},
'importer_err_refanim': {
	'en': "Found animation in reference mesh \"{0}\", ignoring!",
	'ru': "Пропуск анимации в файле с позой по умолчанию (\"{0}\")",
},
'importer_err_badweights': {
	'en': "{0} vertices weighted to invalid bones on {1}",
	'ru': "{0} вершин привязаны к неверным костям на объекте {1}",
},
'importer_err_bonelimit_smd': {
	'en': "Source only supports 128 bones!",
	'ru': "Движок Source не поддерживает больше 128 костей!",
},
'importer_err_badfile': {
	'en': "Format of {0} not recognised",
	'ru': "Не распознан формат файла \"{0}\"",
},
'importer_err_smd_ver': {
	'en': "Unrecognised/invalid SMD file. Import will proceed, but may fail!",
	'ru': "Не удалось распознать SMD-файл. Импорт будет продолжен до первой ошибки.",
},
'importer_err_cleancurves': {
	'en': "Unable to clean keyframe handles, animations might be jittery.",
	'ru': "Не удалось очистить ручки ключевых кадров, анимации могут содержать \"тряску\"",
},
'importer_append': {
	'en': "Append To Existing Model",
	'ru': "Дополнять существующую модель",
},
'importer_doanims': {
	'en': "Import Animations",
	'ru': "Импортировать анимации",
},
'importer_err_missingbones': {
	'en': "{0} contains {1} bones not present in {2}: {3}",
	'ru': "{1} костей из {0} не найдены в {2}: {3}",
},
'importer_name_unmatchedvta': {
	'en': "Unmatched VTA",
	'ru': "Несопоставленные вершины VTA",
},
'exportstate_pattern_tip': {
	'en': "Visible objects with this string in their name will be affected",
	'ru': "Будут обработаны видимые объекты, содержащие в своём названии эту строку",
},
'exportstate': {
	'en': "Set Source Tools export state",
	'ru': "Задать состояние экспорта Source Tools",
},
'activate_dep_shapes': {
	'en': "Activate Dependency Shapes",
	'ru': "Активировать зависимые ключи формы",
},
'gen_block_success': {
	'en': "DMX written to text block \"{0}\"",
	'ru': "Настройки контроллеров лицевой анимации записаны в {0}",
},
'gen_block': {
	'en': "Generate DMX Flex Controller block",
	'ru': "Сгенерировать настройки контроллеров лицевой анимации",
},
'insert_uuid': {
	'en': "Insert UUID",
	'ru': "Вставить UUID",
},
'launch_hlmv_tip': {
	'en': "Launches Half-Life Model Viewer",
	'ru': "Запускает просмотощик моделей Source, HLMV",
},
'activate_dep_shapes_tip': {
	'en': "Activates shapes found in the name of the current shape (underscore delimited)",
	'ru': "Активирует зависимые ключи формы  (ключи формы, которые можно найти в названии данного ключа, разделённые подчёркиванием)",
},
'activate_dep_shapes_success': {
	'en': "Activated {0} dependency shapes",
	'ru': "Активировано {0} зависимых ключей формы",
},
'launch_hlmv': {
	'en': "Launch HLMV",
	'ru': "Запустить HLMV",
},
'exportstate_pattern': {
	'en': "Search pattern",
	'ru': "Маска поиска",
},
'insert_uuid_tip': {
	'en': "Inserts a random UUID at the current location",
	'ru': "Вставить новый UUID",
},
'gen_block_tip': {
	'en': "Generate a simple Flex Controller DMX block",
	'ru': "Генерирует простой блок контроллеров лицевой анимации, по контроллеру на один ключ формы",
},
'gen_drivers': {
	'en': "Generate Corrective Shape Key Drivers",
	'ru': "Создать драйверы для ключей форм коррекции",
},
'gen_drivers_tip': {
	'en': "Adds Blender animation drivers to corrective Source engine shapes",
	'ru': "Создаёт драйверы для ключей форм коррекции, использующихся в Source",
},
'qc_path': {
	'en': "QC Path",
	'ru': "Путь до QC-файлов",
},
'engine_path': {
	'en': "Engine Path",
	'ru': "Путь до папки bin движка",
},
'game_path_tip': {
	'en': "Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",
	'ru': "Путь до мода (где gameinfo.txt). Если не задано, то будет использована переменная среды VPROJECT",
},
'visible_only': {
	'en': "Visible layers only",
	'ru': "Только видимые слои",
},
'dmx_encoding': {
	'en': "DMX encoding",
	'ru': "Способ кодирования DMX-файла",
},
'game_path': {
	'en': "Game Path",
	'ru': "Путь до мода",
},
'up_axis': {
	'en': "Target Up Axis",
	'ru': "Направление \"Вверх\"",
},
'dmx_format': {
	'en': "DMX format",
	'ru': "Формат DMX-файла",
},
'ignore_materials': {
	'en': "Ignore Blender Materials",
	'ru': "Игнорировать материалы Blender",
},
'visible_only_tip': {
	'en': "Ignore objects in hidden layers",
	'ru': "Не экспортировать объекты, расположенные на выключенных слоях",
},
'active_exportable': {
	'en': "Active exportable",
	'ru': "Активный объект для экспорта",
},
'exportroot_tip': {
	'en': "The root folder into which SMD and DMX exports from this scene are written",
	'ru': "Папка, куда будут экспортироваться SMD и DMX из текущей сцены",
},
'qc_compilenow': {
	'en': "Compile All Now",
	'ru': "Скомпилировать все QC",
},
'up_axis_tip': {
	'en': "Use for compatibility with data from other 3D tools",
	'ru': "Используется для совместимости с экспортами из Maya и других 3D-пакетов",
},
'dmx_mat_path_tip': {
	'en': "Folder relative to game root containing VMTs referenced in this scene (DMX only)",
	'ru': "Путь (относительно мода), содержащий VMT-файлы для этой модели (аналог $cdmaterials; только для DMX-файлов)",
},
'qc_compileall_tip': {
	'en': "Compile all QC files whenever anything is exported",
	'ru': "Компилировать все указанные QC-файлы сразу после экспорта",
},
'qc_path_tip': {
	'en': "This scene's QC file(s); Unix wildcards supported",
	'ru': "QC-файлы, связанные с этой сценой; поддерживаются маски для имён файлов",
},
'qc_nogamepath': {
	'en': "No Game Path and invalid VPROJECT",
	'ru': "Не указан путь до мода; переменная VPROJECT содержит ошибочные данные",
},
'dmx_mat_path': {
	'en': "Material Path",
	'ru': "Путь до материалов",
},
'exportroot': {
	'en': "Export Path",
	'ru': "Куда экспортировать",
},
'export_format': {
	'en': "Export Format",
	'ru': "Формат файла экспорта",
},
'qc_compileall': {
	'en': "Compile all on export",
	'ru': "Компилировать QC-файлы после экспорта",
},
'dmx_encoding_tip': {
	'en': "Manual override for binary DMX encoding version",
	'ru': "Версия структуры DMX-файла",
},
'dmx_format_tip': {
	'en': "Manual override for DMX model format version",
	'ru': "Версия формата модели (DMX-файл)",
},
'engine_path_tip': {
	'en': "Directory containing studiomdl",
	'ru': "Путь до studiomdl",
},
'ignore_materials_tip': {
	'en': "Only export face-assigned image filenames",
	'ru': "Называть материалы в экспортированной модели по именам текстур, а не Blender-материалов",
},
'updater_title': {
	'en': "Check for Source Tools updates",
	'ru': "Проверить обновления Source Tools",
},
'update_err_downloadfailed': {
	'en': "Could not complete download:",
	'ru': "Не удалось завершить загрузку обновления",
},
'offerchangelog_offer': {
	'en': "View changelog?",
	'ru': "Список изменений",
},
'update_err_outdated': {
	'en': "The latest Source Tools require Blender {0}. Please upgrade.",
	'ru': "Текущая версия Source Tools требует Blender {0}. Пожалуйста, обновитесь.",
},
'update_err_unknown': {
	'en': "Could not install update:",
	'ru': "Невозможно обновить Source Tools: ",
},
'offerchangelog_title': {
	'en': "Source Tools Update",
	'ru': "Обновление Source Tools",
},
'update_err_corruption': {
	'en': "Update was downloaded, but file was not valid",
	'ru': "Не удалось обновиться: файлы обновления повреждены",
},
'update_done': {
	'en': "Upgraded to Source Tools {0}!",
	'ru': "Успешно обновлено до Blender Source Tools {0}",
},
'updater_title_tip': {
	'en': "Connects to http://steamreview.org/BlenderSourceTools/latest.php",
	'ru': "Смотрит обновления на http://steamreview.org/BlenderSourceTools/latest.php",
},
'update_alreadylatest': {
	'en': "The latest Source Tools ({0}) are already installed.",
	'ru': "Уже установлена самая последняя версия Blender Source Tools ({0}).",
},
}

def _get_ids():	
	ids = {}
	for id,values in _data.items():
		ids[id] = values['en']
	return ids
ids = _get_ids()

def _get_translations():
	import collections
	translations = collections.defaultdict(dict)
	for lang in _languages:
		for id,values in _data.items():
			value = values.get(lang)
			if value: translations[lang][(None, ids[id])] = value
	return translations
translations = _get_translations()
