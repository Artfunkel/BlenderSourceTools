#coding=utf-8
_languages = ['ru', 'ja', 'zh']

_data = {
'vca_sequence': {
	'ja': "シクウェンスを生成します",
	'en': "Generate Sequence",
	'zh': "创建动画",
	'ru': "Создать анимацию",
},
'controllers_simple_tip': {
	'en': "Generate one flex controller per shape key",
	'ru': "Создавать по контроллеру на каждый ключ формы",
},
'vertmap_group_props': {
	'en': "Vertex Maps",
	'zh': "顶点绘制",
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
'valvesource_cloth_enable': {
	'en': "Cloth Physics Enable",
	'zh': "启用衣服物理",
},
'subdir_tip': {
	'en': "Optional path relative to scene output folder",
	'zh': "导出到哪里？（可选；默认情况下，导出到 .blend 文件所在的文件夹）",
	'ru': "Куда экспортировать? (Необязательно; по умолчанию экспортируется в ту же папку, где находится .blend-файл) ",
},
'controllers_mode': {
	'ja': "DMXフレックスのコントローラー生成",
	'en': "DMX Flex Controller generation",
	'ru': "Генерация контроллеров лицевой анимации (DMX)",
},
'scene_export': {
	'ja': "シーンをエクスポート",
	'en': "Scene Export",
	'zh': "场景导出",
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
	'en': "Avoids concave DMX faces, which are not supported by Source",
	'ru': "Избегать вогнутых полигонов в DMX-файлах (не поддерживается studiomdl)",
},
'action_filter': {
	'ja': "アクションフィルター",
	'en': "Action Filter",
	'zh': "动作过滤器",
	'ru': "Фильтр действий",
},
'vca_start_tip': {
	'en': "Scene frame at which to start recording Vertex Animation",
	'ru': "Кадр в сцене, с которого следует начать запись вершинной анимации",
},
'action_filter_tip': {
	'en': "Actions with names matching this filter pattern and which have users will be exported",
	'ru': "Будут эксортированы только те действия, имена которых подходят под этот фильтр, и которые где-либо используются",
},
'shape_stereo_sharpness_tip': {
	'en': "How sharply stereo flex shapes should transition from left to right",
	'ru': "Насколько резко будет осуществляться переход между левой и правой частью объекта",
},
'vca_sequence_tip': {
	'en': "On export, generate an animation sequence that drives this Vertex Animation",
	'ru': "При экспорте автоматически создать sequence, управляющий этой вершинной анимацией",
},
'shape_stereo_mode': {
	'en': "DMX stereo split mode",
	'ru': "Разделение на левую и правую части для стерео-контрлолеров (DMX)",
},
'dummy_bone': {
	'en': "Implicit motionless bone",
	'ru': "\"Пустая\" недвижимая кость",
},
'vca_group_props': {
	'ja': "頂点アニメーション",
	'en': "Vertex Animation",
	'zh': "顶点动画",
	'ru': "Вершинная анимация",
},
'curve_poly_side': {
	'ja': "ポリゴン生成",
	'en': "Polygon Generation",
	'zh': "生成多边形",
	'ru': "Генерация геометрии",
},
'group_merge_mech': {
	'ja': "メカニカルな局部は結合",
	'en': "Merge mechanical parts",
	'ru': "Слить вместе механические части",
},
'action_selection_mode_tip': {
	'en': "How actions are selected for export",
	'ru': "Какие действия экспортировать?",
},
'use_scene_export_tip': {
	'en': "Export this item with the scene",
	'zh': "导出此对象时导出场景",
	'ru': "Экспортировать этот объект при экспорте сцены",
},
'curve_poly_side_back': {
	'en': "Backward (inner) side",
	'ru': "Внутренняя сторона",
},
'valvesource_vertex_blend': {
	'en': "Blend Params RGB",
	'zh': "混合参数 RGB",
},
'bone_rot_legacy_tip': {
	'en': "Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",
	'ru': "Переназначить Y-ось всех костей в Z-ось для обратной совместимости с старыми импортами",
},
'controller_source': {
	'ja': "DMXフレックスのコントローラーのソースファイル ",
	'en': "DMX Flex Controller source",
	'zh': "DMX 面部动画控制器文件",
	'ru': "Файл контроллеров лицевой анимации (DMX)",
},
'group_suppress_tip': {
	'en': "Export this group's objects individually",
	'zh': "单独导出此组的对象",
	'ru': "Экспортировать объекты этой группы по отдельности",
},
'action_selection_current': {
	'ja': "現在 / NLA",
	'en': "Current / NLA",
	'zh': "当前动作/非线性动画",
	'ru': "Текущее действие / Нелинейная анимация",
},
'shape_stereo_sharpness': {
	'en': "DMX stereo split sharpness",
	'ru': "Резкость разделения в стерео-контроллерах",
},
'group_suppress': {
	'ja': "ミュート",
	'en': "Suppress",
	'zh': "忽略",
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
'valvesource_vertex_blend1': {
	'en': "Blend Params Extra (?)",
	'zh': "混合参数扩展（？）",
},
'curve_poly_side_tip': {
	'en': "Determines which side(s) of this curve will generate polygons when exported",
	'ru': "Указывает, какая сторона (стороны) выделенной кривой будет использоваться для генерации геометрии",
},
'triangulate': {
	'ja': "三角測量",
	'en': "Triangulate",
	'zh': "三角化",
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
	'zh': "动作选择",
	'ru': "Выбор действия",
},
'shape_stereo_mode_vgroup': {
	'en': "Use a vertex group to define stereo balance",
	'ru': "Использовать группу вершин для разделения стерео-контроллеров",
},
'vca_end_tip': {
	'en': "Scene frame at which to stop recording Vertex Animation",
	'ru': "Кадр в сцене, которым следует закончить запись вершинной анимации",
},
'valvesource_vertex_paint': {
	'en': "Vertex Paint",
},
'controllers_mode_tip': {
	'en': "How flex controllers are defined",
	'ru': "Способ задания контроллеров лицевой анимации",
},
'subdir': {
	'en': "Subfolder",
	'zh': "子文件夹",
	'ru': "Подпапка",
},
'dummy_bone_tip': {
	'en': "Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)",
	'ru': "Создать кость и привязать к ней вершины, которые не двигаются. (Только SMD.)",
},
'exportpanel_steam': {
	'ja': "Steam コミュニティ",
	'en': "Steam Community",
	'zh': "Steam 社区",
	'ru': "Сообщество Steam",
},
'exportables_arm_filter_result': {
	'ja': "「{0}」アクション～{1}",
	'en': "\"{0}\" actions ({1})",
	'ru': "Фильтр имён действий \"{0}\" на скелете {1}",
},
'exportables_flex_count_corrective': {
	'ja': "是正シェイプ：{0}",
	'en': "Corrective Shapes: {0}",
	'ru': "Ключей форм коррекции: {0}",
},
'exportables_curve_polyside': {
	'ja': "ポリゴン生成：",
	'en': "Polygon Generation:",
	'ru': "Генерация геометрии:",
},
'exportmenu_title': {
	'ja': "Source Tools エクスポート",
	'en': "Source Tools Export",
	'zh': "起源引擎工具导出",
	'ru': "Экспорт в Source",
},
'exportables_flex_help': {
	'ja': "フレックス・コントローラーのヘレプ",
	'en': "Flex Controller Help",
	'zh': "面部动画控制器帮助",
	'ru': "Помощь по контроллерам лицевой анимации",
},
'exportpanel_title': {
	'ja': "Source Engine エクスポート",
	'en': "Source Engine Export",
	'zh': "起源引擎导出",
	'ru': "Экспорт в Source",
},
'exportables_flex_src': {
	'ja': "コントローラーのソースファイル ",
	'en': "Controller Source",
	'ru': "Файл настроек контроллеров",
},
'exportmenu_invalid': {
	'en': "Cannot export selection",
	'zh': "无法导出选中项",
	'ru': "Выделенный объект невозможно экспортировать",
},
'qc_title': {
	'ja': "Source Engine QCのコンパイル",
	'en': "Source Engine QC Compiles",
	'zh': "起源引擎 QC 编译",
	'ru': "Компиляция QC",
},
'exportables_flex_props': {
	'ja': "フレックスのプロパティ",
	'en': "Flex Properties",
	'zh': "面部动画控制器属性",
	'ru': "Свойства контроллеров лицевой анимации",
},
'exportables_flex_generate': {
	'ja': "コントローラーを生成します",
	'en': "Generate Controllers",
	'ru': "Сгенерировать контроллеры",
},
'exportables_flex_split': {
	'ja': "ステレオフルックスの差額：",
	'en': "Stereo Flex Balance:",
	'ru': "Разделение на правую и левую часть:",
},
'exportables_group_mute_suffix': {
	'ja': "(ミユト)",
	'en': "(suppressed)",
	'zh': "（已忽略）",
	'ru': "(игнорируется)",
},
'exportmenu_scene': {
	'ja': "シーンをエクスポート ({0}つファイル)",
	'en': "Scene export ({0} files)",
	'zh': "场景导出（{0} 个文件）",
	'ru': "Экспорт {0} файлов",
},
'exportpanel_dmxver': {
	'ja': "DMXのバージョン：",
	'en': "DMX Version:",
	'zh': "DMX 版本",
	'ru': "Версия DMX:",
},
'exportpanel_update': {
	'ja': "更新アドオンの確認",
	'en': "Check for updates",
	'zh': "检查更新",
	'ru': "Проверить обновления",
},
'exportables_title': {
	'ja': "Source Engineのエクスポート可能",
	'en': "Source Engine Exportables",
	'zh': "起源引擎可导出项",
	'ru': "Объекты для Source",
},
'exportables_armature_props': {
	'ja': "アーマティアのプロパティ",
	'en': "Armature Properties ({0})",
	'zh': "骨骼属性（{0}）",
	'ru': "Свойства скелета ({0})",
},
'qc_bad_enginepath': {
	'ja': "エンジンのパスが無効です",
	'en': "Invalid Engine Path",
	'zh': "无效引擎路径",
	'ru': "Некорректный путь до папки bin",
},
'qc_invalid_source2': {
	'ja': "Source Engine 2はQCファイルが使いません",
	'en': "QC files do not exist in Source 2",
	'zh': "QC 文件在起源 2 中不存在",
	'ru': "QC-файлы движком Source 2 не используются",
},
'exportmenu_selected': {
	'en': "Selected objects ({0} files)",
	'zh': "选中的对象（{0}个文件）",
	'ru': "Выбранные объекты ({0} файлов)",
},
'exportables_group_props': {
	'ja': "グループのプロパティ",
	'en': "Group Properties",
	'zh': "组属性",
	'ru': "Свойства групп",
},
'qc_no_enginepath': {
	'ja': "エンジンのパスはありません",
	'en': "No Engine Path provided",
	'zh': "未提供引擎路径",
	'ru': "Не указан путь до папки bin",
},
'exportables_curve_props': {
	'ja': "カーブのプロパティ",
	'en': "Curve Properties",
	'ru': "Свойства сплайна",
},
'exportables_flex_count': {
	'ja': "シェイプ：{0}",
	'en': "Shapes: {0}",
	'ru': "Ключей формы: {0}",
},
'bl_info_author': {
	'ja': "トム・エドワーズ～グリゴリ・レヴジン",
	'en': "Tom Edwards (translators: Grigory Revzin)",
	'zh': "汤姆·艾德华（翻译者：IBRS）",
	'ru': "Том Эдвардс (переводили: Григорий Ревзин)",
},
'activate_dependency_shapes': {
	'en': "Activate dependency shapes",
	'ru': "Активировать зависимые ключи формы",
},
'settings_prop': {
	'en': "Blender Source Tools settings",
	'zh': "Blender 起源引擎工具设置",
	'ru': "Настройки Blender Source Tools",
},
'bl_info_description': {
	'en': "Importer and exporter for Valve Software's Source Engine. Supports SMD\\VTA, DMX and QC.",
	'zh': "维尔福软件公司的起源引擎的导入和导出工具。支持 SMD\\VTA，DMX 和 QC 文件。",
	'ru': "Экспорт и импорт для движка Source. Поддерживаемые форматы: SMD/VTA, DMX, QC.",
},
'export_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx)",
	'zh': "起源引擎（.smd，.vta，.dmx）",
	'ru': "Движок Source (.smd, .vta, .dmx)",
},
'help': {
	'ja': "ヘレプ",
	'en': "Help",
	'zh': "帮助",
	'ru': "Помощь",
},
'bl_info_location': {
	'ja': "ファイル > インポート / エクスポート、シーンのプロパティ",
	'en': "File > Import/Export, Scene properties",
	'zh': "文件 > 导入/导出，场景属性",
	'ru': "Файл > Импортировать/Экспортировать, свойства сцены",
},
'import_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx, .qc)",
	'zh': "起源引擎（.smd，.vta，.dmx，.qc）",
	'ru': "Движок Source (.smd, .vta, .dmx, .qc)",
},
'exporter_err_nogroupitems': {
	'en': "Nothing in Group \"{0}\" is enabled for export",
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
	'zn': "对象 {0} 没有多边形，正在跳过",
	'ru': "Пропуск объекта {0}: нет геометрии",
},
'exporter_err_hidden': {
	'en': "Skipping {0}: object cannot be selected, probably due to being hidden by an animation driver.",
},
'exporter_err_arm_nonuniform': {
	'en': "Armature \"{0}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.",
	'ru': "Скелет {0} масштабирован непропорционально. В движке Source скелет будет работать неправильно.",
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
	'zh': "导出了 {0} 根骨骼，但 SMD 最高只支持 {1} 根骨骼！",
	'ru': "Экспортировано {0} костей, но SMD поддерживает только {1}!",
},
'exporter_err_unmergable': {
	'en': "Skipping vertex animations on Group \"{0}\", which could not be merged into a single DMX object due to its envelope. To fix this, either ensure that the entire Group has the same bone parent or remove all envelopes.",
	'ru': "Пропуск вершинной анимации для группы «{0}», которую не удаётся слить в DMX-модель из-за огибающих. Проверьте, что у всей группы одна и та же кость-родитель или удалите все огибающие.",
},
'exporter_warn_source2names': {
	'en': "Consider renaming \"{0}\": in Source 2, model names can contain only lower-case characters, digits, and/or underscores.",
},
'exporter_warn_unicode': {
	'ja': "{0}「{1}」の名前はUnicode文字を含みます。間違ってコンパイルすることが可能です。",
	'en': "Name of {0} \"{1}\" contains Unicode characters. This may not compile correctly!",
},
'exporter_err_flexctrl_loadfail': {
	'en': "Could not load flex controllers. Python reports: {0}",
	'ru': "Загрузить контроллеры из указанного DMX-файла не удалось. Ошибка Python: {0}",
},
'qc_compile_err_nofiles': {
	'en': "Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.",
	'ru': "Нет QC-файлов, нечего компилировать. Blender Source Tools не генерируют QC-файлы.",
},
'exporter_err_missing_corrective_target': {
	'en': "Found corrective shape key \"{0}\", but not target shape \"{1}\"",
	'zh': "发现了修正形态键“{0}”，但没有目标形态“{1}”。",
},
'qc_compile_complete': {
	'ja': "{0}つ「{1}」QCがコンパイルしました",
	'en': "Compiled {0} {1} QCs",
	'zh': "已编译 {0} 个 {1} QC 文件。",
	'ru': "Скомпилировано {0} QC для движка {1}.",
},
'exporter_err_shapes_decimate': {
	'en': "Cannot export shape keys from \"{0}\" because it has a '{1}' Decimate modifier. Only Un-Subdivide mode is supported.",
	'ru': "Невзможно экспортировать ключи формы для {0}, потому что активен модификатор \"Аппроксимация\" в режиме {1}. Поддерживается только режим \"Снять подразделение\"",
},
'exporterr_goldsrc_multiweights': {
	'en': "{0} verts on \"{1}\" have multiple weight links. GoldSrc does not support this!",
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
	'ja': "QCコンパイル",
	'en': "Compile QC",
	'zh': "编译 QC",
	'ru': "Скомпилировать QC-файл",
},
'exporter_err_noexportables': {
	'en': "Found no valid objects for export",
	'ru': "Не найдено подходящих для экспорта объектов",
},
'exporter_warn_sanitised_filename': {
	'en': "Sanitised exportable name \"{0}\" to \"{1}\"",
},
'exporter_warn_correctiveshape_duplicate': {
	'en': "Corrective shape key \"{0}\" has the same activation conditions ({1}) as \"{2}\". Skipping.",
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
'exporter_warn_source2smdsupport': {
	'en': "Source 2 no longer supports SMD.",
	'zh': "起源 2 不再支持 SMD。",
},
'exporter_tip': {
	'en': "Export and compile Source Engine models",
	'ru': "Экспортирует и компилирует модели для движка Source",
},
'exporter_warn_weightlinks_culled': {
	'en': "{0} excess weight links beneath scene threshold of {1:0.2} culled on \"{2}\".",
	'ru': "На «{2}» удалено {0} излишних привязок к костям: предел веса, заданный для сцены, {1:0.2}",
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
	'ja': "グループの名前",
	'en': "Group Name",
	'zh': "组名称",
	'ru': "Имя группы",
},
'qc_compile_tip': {
	'en': "Compile QCs with the Source SDK",
	'zh': "使用起源 SDK 编译 QC 文件",
	'ru': "Компилирует QC-файлы с помощью studiomdl",
},
'exporter_report_suffix': {
	'en': " with {0} Errors and {1} Warnings",
	'zh': "错误：{0}，警告：{1}",
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
	'ja': "エクスポートにグループの名前",
	'en': "Name of the Group to export",
	'ru': "Имя группы для экспорта",
},
'exporter_warn_multiarmature': {
	'en': "Multiple armatures detected",
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
'exporter_warn_weightlinks_excess': {
	'en': "{0} verts on \"{1}\" have over {2} weight links. Source does not support this!",
	'ru': "На «{1}» {0} вершин имеют привязку к более {2} костей. Source не поддерживает такое коилчество привязок.",
},
'exporter_err_noframes': {
	'en': "Armature {0} has no animation frames to export",
},
'exporter_report_menu': {
	'ja': "レポート：Source Tools エラー",
	'en': "Source Tools Error Report",
	'zh': "起源引擎工具错误报告",
	'ru': "Отчёт о ошибках Source Tools",
},
'exporter_report': {
	'ja': "{0}つファイルは{1}秒エクスポート",
	'en': "{0} files exported in {1} seconds",
	'zh': "在 {1} 秒内导出了 {0} 个文件。",
	'ru': "Файлов экспортировано: {0}. Прошло секунд: {1};",
},
'exporter_err_groupmuted': {
	'ja': "ゲルーポ「{0}」はミュートです",
	'en': "Group {0} is suppressed",
	'zh': "组 {0} 已忽略",
	'ru': "Свойства группы {0} \"пересилены\"",
},
'exporter_title': {
	'ja': "SMD/VTA/DMXをエクスポート",
	'en': "Export SMD/VTA/DMX",
	'zh': "导出 SMD/VTA/DMX",
	'ru': "Экспорт SMD/VTA/DMX",
},
'qc_compile_err_unknown': {
	'en': "Compile of {0} failed. Check the console for details",
	'zh': "编译 {0} 失败。查看控制台了解详细信息。",
	'ru': "Не удалось скомпилировать QC-файл {0}. Ошибка описана в консоли",
},
'exporter_err_splitvgroup_missing': {
	'en': "Could not find stereo split Vertex Group \"{0}\" on object \"{1}\"",
	'ru': "Не найдена группа веришн {0} для разделения на левую и правую части стерео-контроллеров на объекте {1}",
},
'importer_complete': {
	'en': "Imported {0} files in {1} seconds",
	'zh': "在 {1} 秒内导入了 {0} 个文件。",
	'ru': "Импортировано файлов: {0}. Прошло секунд: {1}.",
},
'importer_bonemode': {
	'ja': "ボーンカスタムシェイプ",
	'en': "Bone shapes",
	'zh': "骨骼样式",
	'ru': "Отображение костей",
},
'importer_err_nofile': {
	'ja': "選択ファイルはありません",
	'en': "No file selected",
	'zh': "未选中文件",
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
'importer_bones_validate_desc': {
	'en': "Report new bones as missing without making any changes to the target Armature",
	'zh': "在不更改目标骨骼的情况下，将新骨骼报告为缺失",
},
'importer_tip': {
	'en': "Imports uncompiled Source Engine model data",
	'zh': "导入未编译的起源引擎模型数据文件",
	'ru': "Импортирует промежуточные файлы Source",
},
'importer_title': {
	'ja': "インポート SMD/VTA, DMX, QC",
	'en': "Import SMD/VTA, DMX, QC",
	'zh': "导入 SMD/VTA，DMX，QC",
	'ru': "Импорт SMD/VTA, DMX, QC",
},
'importer_makecamera': {
	'ja': "$originにカメラを生成",
	'en': "Make Camera At $origin",
	'zh': "在 $origin 处生成相机",
	'ru': "Создать камеру по координатам, указанным в $origin",
},
'importer_bone_parent_miss': {
	'en': "Parent mismatch for bone \"{0}\": \"{1}\" in Blender, \"{2}\" in {3}.",
	'ru': "Не совпадают родители у кости \"{0}\": \"{1}\" в Blender, \"{2}\" в файле \"{3}\".",
},
'importer_makecamera_tip': {
	'en': "For use in viewmodel editing; if not set, an Empty will be created instead",
	'zh': "用于第一人称模型编辑；如果未设置，将创建一个空值",
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
'importer_skipremdoubles_tip': {
	'en': "Import raw, disconnected polygons from SMD files; these are harder to edit but a closer match to the original mesh",
},
'importer_balance_group': {
	'en': "DMX Stereo Balance",
	'ru': "Разделение стерео-контроллеров",
},
'importer_bones_mode_desc': {
	'en': "How to behave when a reference mesh import introduces new bones to the target Armature (ignored for QCs)",
	'zh': "参考网格导入时，将新骨骼引入目标骨骼的行为（QC 文件忽略此选项）",
},
'importer_rotmode': {
	'ja': "回転モード",
	'en': "Rotation mode",
	'zh': "旋转模式",
	'ru': "Способ задания вращения",
},
'importer_skipremdoubles': {
	'ja': "SMDのポリゴンと法線を保持",
	'en': "Preserve SMD Polygons & Normals",
},
'importer_bonemode_tip': {
	'en': "How bones in new Armatures should be displayed",
	'zh': "如何显示新骨架中的骨骼",
	'ru': "Как будут выглядеть кости в импортированном скелете?",
},
'importer_bones_append': {
	'ja': "対象で追加",
	'en': "Append to Target",
	'zh': "追加至目标",
},
'importer_err_qci': {
	'en': "Could not open QC $include file \"{0}\" - skipping!",
	'zh': "无法打开 QC 的 $include 文件“{0}” - 正在跳过！",
	'ru': "Пропуск файла \"{0}\" из команды $include: не удалсь открыть.",
},
'importer_up_tip': {
	'en': "Which axis represents 'up' (ignored for QCs)",
	'ru': "Какая из осей соответствует направлению \"вврех\"?",
},
'importer_err_namelength': {
	'en': "{0} name \"{1}\" is too long to import. Truncating to \"{2}\"",
	'zh': "名为“{1}”的{0}名称太长。缩短为“{2}”",
},
'importer_bones_append_desc': {
	'en': "Add new bones to the target Armature",
	'zh': "将新骨骼添加到目标骨骼",
},
'importer_err_unmatched_mesh': {
	'en': "{0} VTA vertices ({1}%) were not matched to a mesh vertex! An object with a vertex group has been created to show where the VTA file's vertices are.",
	'ru': "{0} вершин ({1}%) не удалось привязать к объекту при импорте VTA. Создан объект с группой вершин, показывающей, где заданные в VTA вершины.",
},
'importer_bones_validate': {
	'ja': "対象で確認",
	'en': "Validate Against Target",
	'zh': "针对目标对象",
},
'importer_name_nomat': {
	'ja': "UndefinedMaterial",
	'en': "UndefinedMaterial",
	'zh': "UndefinedMaterial",
	'ru': "UndefinedMaterial",
},
'importer_bones_newarm_desc': {
	'en': "Make a new Armature for this import",
	'zh': "为此次导入的文件创建新的骨骼",
},
'importer_err_refanim': {
	'en': "Found animation in reference mesh \"{0}\", ignoring!",
	'ru': "Пропуск анимации в файле с позой по умолчанию (\"{0}\")",
},
'importer_bones_mode': {
	'ja': "ボーンの追加がモード",
	'en': "Bone Append Mode",
	'zh': "骨骼追加模式",
},
'importer_err_badweights': {
	'en': "{0} vertices weighted to invalid bones on {1}",
	'ru': "{0} вершин привязаны к неверным костям на объекте {1}",
},
'importer_err_bonelimit_smd': {
	'en': "SMD only supports 128 bones!",
	'zh': "SMD 只支持 128 根骨骼！",
	'ru': "Движок SMD не поддерживает больше 128 костей!",
},
'importer_err_badfile': {
	'en': "Format of {0} not recognised",
	'ru': "Не распознан формат файла \"{0}\"",
},
'importer_err_smd_ver': {
	'en': "Unrecognised/invalid SMD file. Import will proceed, but may fail!",
	'ru': "Не удалось распознать SMD-файл. Импорт будет продолжен до первой ошибки.",
},
'importer_doanims': {
	'ja': "アニメーションをインポート",
	'en': "Import Animations",
	'zh': "导入动画",
	'ru': "Импортировать анимации",
},
'importer_use_collections':{
	'en': "Create Collections",	
	'zh': "创建集合",
},
'importer_use_collections_tip':{
	'en': "Create a Blender collection for each imported mesh file. This retains the original file structure (important for DMX) and makes it easy to switch between LODs etc. with the number keys",
	'zh': "为每个导入的网格文件创建 Blender 集合。这保留了原始的文件结构（对 DMX 文件很重要），并让数字键切换 LOD 等更轻松",
},
'importer_err_missingbones': {
	'en': "{0} contains {1} bones not present in {2}. Check the console for a list.",
	'ru': "{1} костей из {0} не найдены в {2}.",
},
'importer_err_noanimationbones': {
	'en': "No bones imported for animation {0}",
},
'importer_name_unmatchedvta': {
	'en': "Unmatched VTA",
	'ru': "Несопоставленные вершины VTA",
},
'importer_bones_newarm': {
	'ja': "アーマティアを生成",
	'en': "Make New Armature",
	'zh': "创建新的骨架",
},
'qc_warn_noarmature': {
	'en': "Skipping {0}; no armature found.",
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
	'ja': "DMXフレックスのコントローラーの抜粋を生成します",
	'en': "Generate DMX Flex Controller block",
	'ru': "Сгенерировать настройки контроллеров лицевой анимации",
},
'vca_add_tip': {
	'en': "Add a Vertex Animation to the active Source Tools exportable",
	'ru': "Добавить к текущему экспортируемому объекту Source Tools вершинную анимацию",
},
'insert_uuid': {
	'en': "Insert UUID",
	'zh': "插入 UUID",
	'ru': "Вставить UUID",
},
'launch_hlmv_tip': {
	'en': "Launches Half-Life Model Viewer",
	'zh': "启动 HLMV 模型查看器",
	'ru': "Запускает просмотощик моделей Source, HLMV",
},
'vertmap_remove': {
	'en': "Remove Source 2 Vertex Map",
	'zh': "移除起源 2 顶点绘制",
},
'activate_dep_shapes_tip': {
	'en': "Activates shapes found in the name of the current shape (underscore delimited)",
	'ru': "Активирует зависимые ключи формы  (ключи формы, которые можно найти в названии данного ключа, разделённые подчёркиванием)",
},
'vca_qcgen_tip': {
	'en': "Copies a QC segment for this object's Vertex Animations to the clipboard",
	'ru': "Создать в буфере обмена фрагмент QC-файла для управления текущей вершинной анимацией",
},
'vca_remove_tip': {
	'en': "Remove the active Vertex Animation from the active Source Tools exportable",
	'ru': "Удалить текущую вершинную анимацию с экспортируемого объекта Source Tools",
},
'vca_add': {
	'en': "Add Vertex Animation",
	'ru': "Добавить вершинную анимацию",
},
'vertmap_select': {
	'en': "Select Source 2 Vertex Map",
	'zh': "选中起源 2 顶点绘制",
},
'vca_preview': {
	'ja': "頂点アニメーションを再生します",
	'en': "Preview Vertex Animation",
	'ru': "Предпросмотр вершинной анимации",
},
'activate_dep_shapes_success': {
	'en': "Activated {0} dependency shapes",
	'ru': "Активировано {0} зависимых ключей формы",
},
'launch_hlmv': {
	'ja': "HLMVを開始",
	'en': "Launch HLMV",
	'zh': "启动 HLMV",
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
	'ja': "是正シェイプキーのドライバーを生成します",
	'en': "Generate Corrective Shape Key Drivers",
	'ru': "Создать драйверы для ключей форм коррекции",
},
'apply_drivers':{
	'en': "Regenerate Shape Key Names From Drivers",
},
'apply_drivers_tip':{
	'en': "Renames corrective shape keys so that each their names are a combination of the shape keys that control them (via Blender animation drivers)",
},
'apply_drivers_success':{
	'en': "{0} shapes renamed.",
},
'vca_qcgen': {
	'ja': "QCの抜粋を生成します",
	'en': "Generate QC Segment",
	'zh': "生成 QC 片段",
	'ru': "Создать фрагмент QC-файла",
},
'vertmap_create': {
	'en': "Create Source 2 Vertex Map",
	'zh': "创建起源 2 顶点绘制",
},
'vca_preview_tip': {
	'en': "Plays the active Source Tools Vertex Animation using scene preview settings",
	'ru': "Проигрывает текущую вершинную анимацию для предпросмотра",
},
'vca_remove': {
	'en': "Remove Vertex Animation",
	'ru': "Удалить текущую вершинную анимацию с экспортируемого объекта Source Tools",
},
'gen_drivers_tip': {
	'en': "Adds Blender animation drivers to corrective Source engine shapes",
	'ru': "Создаёт драйверы для ключей форм коррекции, использующихся в Source",
},
'qc_path': {
	'ja': "QCのパス",
	'en': "QC Path",
	'zh': "QC 路径",
	'ru': "Путь до QC-файлов",
},
'engine_path': {
	'ja': "エンジンのパス",
	'en': "Engine Path",
	'zh': "引擎路径",
	'ru': "Путь до папки bin движка",
},
'game_path_tip': {
	'en': "Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",
	'zh': "包含 gameinfo.txt 的路径（如果未设置，则使用系统的 VPROJECT 环境变量）",
	'ru': "Путь до мода (где gameinfo.txt). Если не задано, то будет использована переменная среды VPROJECT",
},
'visible_only': {
	'ja': "たった可視のレイヤー",
	'en': "Visible layers only",
	'ru': "Только видимые слои",
},
'dmx_encoding': {
	'ja': "DMXの符号化",
	'en': "DMX encoding",
	'zh': "DMX 编码",
	'ru': "Способ кодирования DMX-файла",
},
'game_path': {
	'ja': "ゲームのパス",
	'en': "Game Path",
	'zh': "游戏路径",
	'ru': "Путь до мода",
},
'up_axis': {
	'ja': "対象の上昇軸",
	'en': "Target Up Axis",
	'zh': "目标向上坐标轴",
	'ru': "Направление \"Вверх\"",
},
'dmx_format': {
	'ja': "DMXのフォーマット",
	'en': "DMX format",
	'zh': "DMX 格式",
	'ru': "Формат DMX-файла",
},
'ignore_materials': {
	'ja': "Blenderのマテリアルを軽視",
	'en': "Ignore Blender Materials",
	'zh': "无视 Blender 材质",
	'ru': "Игнорировать материалы Blender",
},
'visible_only_tip': {
	'en': "Ignore objects in hidden layers",
	'ru': "Не экспортировать объекты, расположенные на выключенных слоях",
},
'active_exportable': {
	'ja': "アクティブ・エクスポート可能",
	'en': "Active exportable",
	'zh': "激活此可导出项",
	'ru': "Активный объект для экспорта",
},
'exportroot_tip': {
	'en': "The root folder into which SMD and DMX exports from this scene are written",
	'zh': "从该场景导出的 SMD 和 DMX 文件将写入的根文件夹",
	'ru': "Папка, куда будут экспортироваться SMD и DMX из текущей сцены",
},
'qc_compilenow': {
	'ja': "今全てはコンパイル",
	'en': "Compile All Now",
	'zh': "立刻编译全部",
	'ru': "Скомпилировать все QC",
},
'up_axis_tip': {
	'en': "Use for compatibility with data from other 3D tools",
	'zh': "用于与其他 3D 工具的数据兼容",
	'ru': "Используется для совместимости с экспортами из Maya и других 3D-пакетов",
},
'smd_format': {
	'ja': "対象のエンジン",
	'en': "Target Engine",
	'zh': "目标引擎",
	'ru': "мишень движка",
},
'dmx_mat_path_tip': {
	'en': "Folder relative to game root containing VMTs referenced in this scene (DMX only)",
	'ru': "Путь (относительно мода), содержащий VMT-файлы для этой модели (аналог $cdmaterials; только для DMX-файлов)",
},
'qc_compileall_tip': {
	'en': "Compile all QC files whenever anything is exported",
	'zh': "当导出任意文件时，编译所有 QC 文件",
	'ru': "Компилировать все указанные QC-файлы сразу после экспорта",
},
'qc_path_tip': {
	'en': "This scene's QC file(s); Unix wildcards supported",
	'zh': "此场景的 QC 文件；支持 Unix 通配符",
	'ru': "QC-файлы, связанные с этой сценой; поддерживаются маски для имён файлов",
},
'qc_nogamepath': {
	'en': "No Game Path and invalid VPROJECT",
	'zh': "无游戏路径，无效的 VPROJECT",
	'ru': "Не указан путь до мода; переменная VPROJECT содержит ошибочные данные",
},
'dmx_mat_path': {
	'ja': "マテリアルのパス",
	'en': "Material Path",
	'zh': "材质路径",
	'ru': "Путь до материалов",
},
'exportroot': {
	'ja': "エクスポートのパス",
	'en': "Export Path",
	'zh': "导出路径",
	'ru': "Куда экспортировать",
},
'export_format': {
	'ja': "エクスポートのフォーマット",
	'en': "Export Format",
	'zh': "导出格式",
	'ru': "Формат файла экспорта",
},
'qc_compileall': {
	'ja': "エクスポートから、みんあがコンパイル",
	'en': "Compile all on export",
	'zh': "导出后编译全部",
	'ru': "Компилировать QC-файлы после экспорта",
},
'dmx_weightlinkcull': {
	'ja': "ウェイト・リンクの間引きのしきい値",
	'en': "Weight Link Cull Threshold",
	'ru': "Порог веса привязки вершины к кости",
},
'dmx_weightlinkcull_tip': {
	'en': "The maximum strength at which a weight link can be removed to comply with Source's per-vertex link limit",
	'ru': "Если вершина связана с некоторой костью, и её вес меньше здесь указанного, то связь с этой костью будет удалена при экспорте, чтобы вписаться в ограничение движка Source. («Source не поддерживает такое количество привязок»)",
},
'dmx_encoding_tip': {
	'en': "Manual override for binary DMX encoding version",
	'zh': "手动覆盖二进制 DMX 的编码版本",
	'ru': "Версия структуры DMX-файла",
},
'dmx_format_tip': {
	'en': "Manual override for DMX model format version",
	'zh': "手动覆盖 DMX 的模型格式版本",
	'ru': "Версия формата модели (DMX-файл)",
},
'engine_path_tip': {
	'en': "Directory containing studiomdl (Source 1) or resourcecompiler (Source 2)",
	'zh': "studiomdl（起源 1）或 resourcecompiler（起源 2）所在的目录",
	'ru': "Путь до папки с studiomdl (Source 1) или resourcecompiler (Source 2)",
},
'ignore_materials_tip': {
	'en': "Only export face-assigned image filenames",
	'ru': "Называть материалы в экспортированной модели по именам текстур, а не Blender-материалов",
},
'updater_title': {
	'ja': "更新Source Toolsの確認",
	'en': "Check for Source Tools updates",
	'zh': "检查起源引擎工具更新",
	'ru': "Проверить обновления Source Tools",
},
'update_err_downloadfailed': {
	'en': "Could not complete download:",
	'zh': "无法完成下载：",
	'ru': "Не удалось завершить загрузку обновления",
},
'offerchangelog_offer': {
	'en': "Restart Blender to complete the update. Click to view the changelog.",
	'zh': "重启 Blender 以完成更新。点击查看更新日志。",
	'ru': "Перезапустите Blender для завершения обновления. Нажмите для просмотра списка изменений.",
},
'update_err_outdated': {
	'en': "The latest Source Tools require Blender {0}. Please upgrade.",
	'zh': "最新版本的起源引擎工具需要 Blender {0}。请更新 Blender。",
	'ru': "Текущая версия Source Tools требует Blender {0}. Пожалуйста, обновитесь.",
},
'update_err_unknown': {
	'en': "Could not install update:",
	'zh': "无法安装更新：",
	'ru': "Невозможно обновить Source Tools: ",
},
'offerchangelog_title': {
	'en': "Source Tools Update",
	'zh': "起源引擎工具更新",
	'ru': "Обновление Source Tools",
},
'update_err_corruption': {
	'en': "Update was downloaded, but file was not valid",
	'zh': "更新已下载，但是文件无效",
	'ru': "Не удалось обновиться: файлы обновления повреждены",
},
'update_done': {
	'en': "Installed Source Tools {0}!",
	'zh': "已安装起源引擎工具 {0}！",
	'ru': "Обновлено до Source Tools {0}!",
},
'updater_title_tip': {
	'en': "Connects to http://steamreview.org/BlenderSourceTools/latest.php",
	'zh': "连接至 http://steamreview.org/BlenderSourceTools/latest.php",
	'ru': "Смотрит обновления на http://steamreview.org/BlenderSourceTools/latest.php",
},
'update_alreadylatest': {
	'en': "The latest Source Tools ({0}) are already installed.",
	'zh': "已安装了最新的起源引擎工具（{0}）。",
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
