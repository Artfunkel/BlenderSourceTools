#coding=utf-8
_languages = ['ja', 'es']

_data = {
'vca_sequence': {
	'ja': "シクウェンスを生成します",
	'en': "Generate Sequence",
	'es': "Generar secuencia",
},
'controllers_simple_tip': {
	'en': "Generate one flex controller per shape key",
	'es': "Generar un controlador flex por forma clave",
},
'vertmap_group_props': {
	'en': "Vertex Maps",
	'es': "Mapas de vértices",
},
'action_selection_filter_tip': {
	'en': "All actions that match the armature's filter term and have users",
	'es': "Todas las acciones que coincidan con el filtro y tengan usuarios",
},
'curve_poly_side_fwd': {
	'en': "Forward (outer) side",
	'es': "Lado frontal (exterior)",
},
'action_selection_current_tip': {
	'en': "The armature's currently assigned action or NLA tracks",
	'es': "La acción asignada actualmente o pistas NLA del armature",
},
'action_slot_selection_current_tip': {
	'en': "The armature's active action slot",
	'es': "Ranura de acción activa del armature",
},
'valvesource_cloth_enable': {
	'en': "Cloth Physics Enable",
	'es': "Activar física de tela",
},
'subdir_tip': {
	'en': "Optional path relative to scene output folder",
	'es': "Ruta opcional relativa a la carpeta de salida",
},
'controllers_mode': {
	'ja': "DMXフレックスのコントローラー生成",
	'en': "DMX Flex Controller generation",
	'es': "Generación de controladores flex DMX",
},
'scene_export': {
	'ja': "シーンをエクスポート",
	'en': "Scene Export",
	'es': "Exportar escena",
},
'shape_stereo_mode_tip': {
	'en': "How stereo split balance should be defined",
	'es': "Cómo definir el balance de división estéreo",
},
'bone_rot_legacy': {
	'en': "Legacy rotation",
	'es': "Rotación heredada",
},
'controllers_advanced_tip': {
	'en': "Insert the flex controllers of an existing DMX file",
	'es': "Insertar controladores flex de un archivo DMX existente",
},
'triangulate_tip': {
	'en': "Avoids concave DMX faces, which are not supported by Source",
	'es': "Evita caras DMX cóncavas (no soportadas por Source)",
},
'action_filter': {
	'ja': "アクションフィルター",
	'en': "Action Filter",
	'es': "Filtro de acciones",
},
'slot_filter': {
	'en': "Slot Filter",
	'es': "Filtro de ranuras",
},
'vca_start_tip': {
	'en': "Scene frame at which to start recording Vertex Animation",
	'es': "Fotograma donde comenzar la animación de vértices",
},
'action_filter_tip': {
	'en': "Actions with names matching this filter pattern and which have users will be exported",
	'es': "Exportar acciones con nombres que coincidan y tengan usuarios",
},
'slot_filter_tip': {
	'en': "Slots of the assigned Action with names matching this wildcard filter pattern will be exported (blank to export everything)",
	'es': "Se exportarán ranuras que coincidan con el patrón (dejar en blanco para todo)",
},
'shape_stereo_sharpness_tip': {
	'en': "How sharply stereo flex shapes should transition from left to right",
	'es': "Transición entre formas estéreo izquierda/derecha",
},
'vca_sequence_tip': {
	'en': "On export, generate an animation sequence that drives this Vertex Animation",
	'es': "Generar secuencia de animación para esta animación de vértices",
},
'shape_stereo_mode': {
	'en': "DMX stereo split mode",
	'es': "Modo de división estéreo DMX",
},
'dummy_bone': {
	'en': "Implicit motionless bone",
	'es': "Hueso estático implícito",
},
'vca_group_props': {
	'ja': "頂点アニメーション",
	'en': "Vertex Animation",
	'es': "Animación de vértices",
},
'curve_poly_side': {
	'ja': "ポリゴン生成",
	'en': "Polygon Generation",
	'es': "Generación de polígonos",
},
'group_merge_mech': {
	'ja': "メカニカルな局部は結合",
	'en': "Merge mechanical parts",
	'es': "Unir partes mecánicas",
},
'action_selection_mode_tip': {
	'en': "How actions are selected for export",
	'es': "Cómo seleccionar acciones para exportar",
},
'use_scene_export_tip': {
	'en': "Export this item with the scene",
	'es': "Exportar este elemento con la escena",
},
'curve_poly_side_back': {
	'en': "Backward (inner) side",
	'es': "Lado trasero (interior)",
},
'valvesource_vertex_blend': {
	'en': "Blend Params RGB",
	'es': "Parámetros de mezcla RGB",
},
'bone_rot_legacy_tip': {
	'en': "Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",
	'es': "Reasigna eje Y a Z para compatibilidad (sólo SMD)",
},
'controller_source': {
	'ja': "DMXフレックスのコントローラーのソースファイル ",
	'en': "DMX Flex Controller source",
	'es': "Fuente de controladores flex DMX",
},
'group_suppress_tip': {
	'en': "Export this group's objects individually",
	'es': "Exportar objetos de este grupo individualmente",
},
'action_selection_current': {
	'ja': "現在 / NLA",
	'en': "Current / NLA",
	'es': "Actual / NLA",
},
'action_slot_current': {
	'ja': "現在のアクションスロット",
	'en': "Current Action Slot",
	'es': "Ranura de acción actual",
},
'shape_stereo_sharpness': {
	'en': "DMX stereo split sharpness",
	'es': "Nitidez de división estéreo DMX",
},
'group_suppress': {
	'ja': "ミュート",
	'en': "Suppress",
	'es': "Suprimir",
},
'shape_stereo_vgroup': {
	'en': "DMX stereo split vertex group",
	'es': "Grupo de vértices para estéreo DMX",
},
'shape_stereo_vgroup_tip': {
	'en': "The vertex group that defines stereo balance (0=Left, 1=Right)",
	'es': "Grupo que define balance estéreo (0=Izq, 1=Der)",
},
'controllers_source_tip': {
	'en': "A DMX file (or Text datablock) containing flex controllers",
	'es': "Archivo DMX (o bloque de texto) con controladores flex",
},
'valvesource_vertex_blend1': {
	'en': "Blend Params Extra (?)",
	'es': "Parámetros extra de mezcla (?)",
},
'curve_poly_side_tip': {
	'en': "Determines which side(s) of this curve will generate polygons when exported",
	'es': "Qué lados de la curva generarán polígonos al exportar",
},
'triangulate': {
	'ja': "三角測量",
	'en': "Triangulate",
	'es': "Triangular",
},
'curve_poly_side_both': {
	'en': "Both sides",
	'es': "Ambos lados",
},
'group_merge_mech_tip': {
	'en': "Optimises DMX export of meshes sharing the same parent bone",
	'es': "Optimiza exportación DMX de mallas con mismo hueso padre",
},
'action_selection_mode': {
	'en': "Action Selection",
	'es': "Selección de acciones",
},
'shape_stereo_mode_vgroup': {
	'en': "Use a vertex group to define stereo balance",
	'es': "Usar grupo de vértices para balance estéreo",
},
'vca_end_tip': {
	'en': "Scene frame at which to stop recording Vertex Animation",
	'es': "Fotograma donde detener la animación de vértices",
},
'valvesource_vertex_paint': {
	'en': "Vertex Paint",
	'es': "Pintura de vértices",
},
'controllers_mode_tip': {
	'en': "How flex controllers are defined",
	'es': "Cómo se definen los controladores flex",
},
'subdir': {
	'en': "Subfolder",
	'es': "Subcarpeta",
},
'dummy_bone_tip': {
	'en': "Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)",
	'es': "Crear hueso ficticio para vértices estáticos (sólo SMD)",
},
'exportpanel_steam': {
	'ja': "Steam コミュニティ",
	'en': "Steam Community",
	'es': "Comunidad Steam",
},
'exportables_arm_filter_result': {
	'ja': "「{0}」アクション～{1}",
	'en': "\"{0}\" actions ({1})",
	'es': "Acciones \"{0}\" ({1})",
},
'exportables_arm_no_slot_filter': {
	'en': "All action slots ({0}) for \"{1}\"",
	'es': "Todas las ranuras ({0}) para \"{1}\"",
},
'exportables_flex_count_corrective': {
	'ja': "是正シェイプ：{0}",
	'en': "Corrective Shapes: {0}",
	'es': "Formas correctivas: {0}",
},
'exportables_curve_polyside': {
	'ja': "ポリゴン生成：",
	'en': "Polygon Generation:",
	'es': "Generación de polígonos:",
},
'exportmenu_title': {
	'ja': "Source Tools エクスポート",
	'en': "Source Tools Export",
	'es': "Exportar Source Tools",
},
'exportables_flex_help': {
	'ja': "フレックス・コントローラーのヘレプ",
	'en': "Flex Controller Help",
	'es': "Ayuda de controladores flex",
},
'exportpanel_title': {
	'ja': "Source Engine エクスポート",
	'en': "Source Engine Export",
	'es': "Exportar para Source Engine",
},
'exportables_flex_src': {
	'ja': "コントローラーのソースファイル ",
	'en': "Controller Source",
	'es': "Fuente de controladores",
},
'exportmenu_invalid': {
	'en': "Cannot export selection",
	'es': "No se puede exportar la selección",
},
'qc_title': {
	'ja': "Source Engine QCのコンパイル",
	'en': "Source Engine QC Compiles",
	'es': "Compilar QC para Source Engine",
},
'exportables_flex_props': {
	'ja': "フレックスのプロパティ",
	'en': "Flex Properties",
	'es': "Propiedades flex",
},
'exportables_flex_generate': {
	'ja': "コントローラーを生成します",
	'en': "Generate Controllers",
	'es': "Generar controladores",
},
'exportables_flex_split': {
	'ja': "ステレオフルックスの差額：",
	'en': "Stereo Flex Balance:",
	'es': "Balance estéreo flex:",
},
'exportables_group_mute_suffix': {
	'ja': "(ミユト)",
	'en': "(suppressed)",
	'es': "(suprimido)",
},
'exportmenu_scene': {
	'ja': "シーンをエクスポート ({0}つファイル)",
	'en': "Scene export ({0} files)",
	'es': "Exportar escena ({0} archivos)",
},
'exportpanel_dmxver': {
	'ja': "DMXのバージョン：",
	'en': "DMX Version:",
	'es': "Versión DMX:",
},
'exportpanel_update': {
	'ja': "更新アドオンの確認",
	'en': "Check for updates",
	'es': "Buscar actualizaciones",
},
'exportables_title': {
	'ja': "Source Engineのエクスポート可能",
	'en': "Source Engine Exportables",
	'es': "Elementos exportables",
},
'exportables_armature_props': {
	'ja': "アーマティアのプロパティ",
	'en': "Armature Properties ({0})",
	'es': "Propiedades de armadura ({0})",
},
'qc_bad_enginepath': {
	'ja': "エンジンのパスが無効です",
	'en': "Invalid Engine Path",
	'es': "Ruta de motor inválida",
},
'qc_invalid_source2': {
	'ja': "Source Engine 2はQCファイルが使いません",
	'en': "QC files do not exist in Source 2",
	'es': "Los archivos QC no existen en Source 2",
},
'exportmenu_selected': {
	'en': "Selected objects ({0} files)",
	'es': "Objetos seleccionados ({0} archivos)",
},
'exportables_group_props': {
	'ja': "グループのプロパティ",
	'en': "Group Properties",
	'es': "Propiedades de grupo",
},
'qc_no_enginepath': {
	'ja': "エンジンのパスはありません",
	'en': "No Engine Path provided",
	'es': "No se especificó ruta de motor",
},
'exportables_curve_props': {
	'ja': "カーブのプロパティ",
	'en': "Curve Properties",
	'es': "Propiedades de curva",
},
'exportables_flex_count': {
	'ja': "シェイプ：{0}",
	'en': "Shapes: {0}",
	'es': "Formas: {0}",
},
'activate_dependency_shapes': {
	'en': "Activate dependency shapes",
	'es': "Activar formas dependientes",
},
'settings_prop': {
	'en': "Blender Source Tools settings",
	'es': "Configuración de Blender Source Tools",
},
'bl_info_description': {
	'en': "Importer and exporter for Valve Software's Source Engine. Supports SMD\\VTA, DMX and QC.",
	'es': "Importador/exportador para Source Engine de Valve. Soporta SMD/VTA, DMX y QC.",
},
'export_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx)",
	'es': "Source Engine (.smd, .vta, .dmx)",
},
'help': {
	'ja': "ヘレプ",
	'en': "Help",
	'es': "Ayuda",
},
'bl_info_location': {
	'ja': "ファイル > インポート / エクスポート、シーンのプロパティ",
	'en': "File > Import/Export, Scene properties",
	'es': "Archivo > Importar/Exportar, Propiedades de escena",
},
'import_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx, .qc)",
	'es': "Source Engine (.smd, .vta, .dmx, .qc)",
},
'exporter_err_nogroupitems': {
	'en': "Nothing in Group \"{0}\" is enabled for export",
	'es': "Nada en el grupo \"{0}\" está habilitado para exportar",
},
'exporter_report_qc': {
	'en': "{0} files exported and {2} QCs compiled ({3}/{4}) in {1} seconds",
	'es': "{0} archivos exportados y {2} QCs compilados ({3}/{4}) en {1} segundos",
},
'exporter_err_relativeunsaved': {
	'en': "Cannot export to a relative path until the blend file has been saved.",
	'es': "No se puede exportar a ruta relativa hasta guardar el archivo .blend",
},
'exporter_err_nopolys': {
	'en': "Object {0} has no polygons, skipping",
	'es': "El objeto {0} no tiene polígonos, omitiendo",
},
'exporter_err_hidden': {
	'en': "Skipping {0}: object cannot be selected, probably due to being hidden by an animation driver.",
	'es': "Omitiendo {0}: no se puede seleccionar (probablemente oculto por controlador)",
},
'exporter_err_arm_nonuniform': {
	'en': "Armature \"{0}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.",
	'es': "La armadura \"{0}\" tiene escala no uniforme. La deformación en Source diferirá de Blender.",
},
'exporter_err_facesnotex_ormat': {
	'en': "{0} faces on {1} did not have a Material or Texture assigned",
	'es': "{0} caras en {1} no tenían material o textura asignada",
},
'exporter_err_arm_noanims': {
	'en': "Couldn't find any animation for Armature \"{0}\"",
	'es': "No se encontraron animaciones para la armadura \"{0}\"",
},
'exporter_err_dupeenv_arm': {
	'en': "Armature modifier \"{0}\" found on \"{1}\", which already has a bone parent or constraint. Ignoring.",
	'es': "El modificador de armadura \"{0}\" en \"{1}\" ya tiene un hueso padre o restricción. Ignorando.",
},
'exporter_err_bonelimit': {
	'en': "Exported {0} bones, but SMD only supports {1}!",
	'es': "Se exportaron {0} huesos, ¡pero SMD sólo soporta {1}!",
},
'exporter_err_unmergable': {
	'en': "Skipping vertex animations on Group \"{0}\", which could not be merged into a single DMX object due to its envelope. To fix this, either ensure that the entire Group has the same bone parent or remove all envelopes.",
	'es': "Omitiendo animaciones de vértices en el grupo \"{0}\" (no se pudo fusionar en un objeto DMX). Solución: asegúrese de que todo el grupo tenga el mismo hueso padre o elimine todos los envolventes.",
},
'exporter_warn_source2names': {
	'en': "Consider renaming \"{0}\": in Source 2, model names can contain only lower-case characters, digits, and/or underscores.",
	'es': "Considere renombrar \"{0}\": en Source 2, los nombres sólo pueden contener minúsculas, números y guiones bajos.",
},
'exporter_warn_unicode': {
	'ja': "{0}「{1}」の名前はUnicode文字を含みます。間違ってコンパイルすることが可能です。",
	'en': "Name of {0} \"{1}\" contains Unicode characters. This may not compile correctly!",
	'es': "El nombre de {0} \"{1}\" contiene caracteres Unicode. ¡Puede no compilarse correctamente!",
},
'exporter_err_flexctrl_loadfail': {
	'en': "Could not load flex controllers. Python reports: {0}",
	'es': "No se pudieron cargar controladores flex. Error de Python: {0}",
},
'qc_compile_err_nofiles': {
	'en': "Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.",
	'es': "No se pueden compilar QCs (no se proporcionaron). Estas herramientas no generan QCs.",
},
'exporter_err_missing_corrective_target': {
	'en': "Found corrective shape key \"{0}\", but not target shape \"{1}\"",
	'es': "Se encontró la forma correctiva \"{0}\" pero no la forma objetivo \"{1}\"",
},
'qc_compile_complete': {
	'ja': "{0}つ「{1}」QCがコンパイルしました",
	'en': "Compiled {0} {1} QCs",
	'es': "Se compilaron {0} QCs {1}",
},
'exporter_err_shapes_decimate': {
	'en': "Cannot export shape keys from \"{0}\" because it has a '{1}' Decimate modifier. Only Un-Subdivide mode is supported.",
	'es': "No se pueden exportar formas de \"{0}\" porque tiene un modificador '{1}' de reducción. Sólo se soporta el modo 'Un-Subdivide'.",
},
'exporterr_goldsrc_multiweights': {
	'en': "{0} verts on \"{1}\" have multiple weight links. GoldSrc does not support this!",
	'es': "¡{0} vértices en \"{1}\" tienen múltiples pesos (no soportado en GoldSrc)!",
},
'exporter_err_splitvgroup_undefined': {
	'en': "Object \"{0}\" uses Vertex Group stereo split, but does not define a Vertex Group to use.",
	'es': "El objeto \"{0}\" usa división estéreo por grupo de vértices, pero no define ningún grupo.",
},
'exporter_err_open': {
	'en': "Could not create {0} file. Python reports: {1}.",
	'es': "No se pudo crear el archivo {0}. Error de Python: {1}.",
},
'qc_compile_title': {
	'ja': "QCコンパイル",
	'en': "Compile QC",
	'es': "Compilar QC",
},
'exporter_err_noexportables': {
	'en': "Found no valid objects for export",
	'es': "No se encontraron objetos válidos para exportar",
},
'exporter_warn_sanitised_filename': {
	'en': "Sanitised exportable name \"{0}\" to \"{1}\"",
	'es': "Nombre exportable \"{0}\" saneado a \"{1}\"",
},
'exporter_warn_correctiveshape_duplicate': {
	'en': "Corrective shape key \"{0}\" has the same activation conditions ({1}) as \"{2}\". Skipping.",
	'es': "La forma correctiva \"{0}\" tiene las mismas condiciones ({1}) que \"{2}\". Omitiendo.",
},
'exporter_err_flexctrl_missing': {
	'en': "No flex controller defined for shape {0}.",
	'es': "No hay controlador flex definido para la forma {0}.",
},
'qc_compile_err_compiler': {
	'en': "Could not execute studiomdl from \"{0}\"",
	'es': "No se pudo ejecutar studiomdl desde \"{0}\"",
},
'exporter_err_facesnotex': {
	'en': "{0} faces on {1} did not have a Texture assigned",
	'es': "{0} caras en {1} no tenían textura asignada",
},
'exporter_err_flexctrl_undefined': {
	'en': "Could not find flex controllers for \"{0}\"",
	'es': "No se encontraron controladores flex para \"{0}\"",
},
'exporter_warn_source2smdsupport': {
	'en': "Source 2 no longer supports SMD.",
	'es': "Source 2 ya no soporta SMD.",
},
'exporter_tip': {
	'en': "Export and compile Source Engine models",
	'es': "Exportar y compilar modelos para Source Engine",
},
'exporter_warn_weightlinks_culled': {
	'en': "{0} excess weight links beneath scene threshold of {1:0.2} culled on \"{2}\".",
	'es': "Se eliminaron {0} pesos menores al umbral {1:0.2} en \"{2}\".",
},
'exporter_prop_scene_tip': {
	'en': "Export all items selected in the Source Engine Exportables panel",
	'es': "Exportar todos los elementos seleccionados en el panel",
},
'exporter_err_dmxenc': {
	'en': "DMX format \"Model {0}\" requires DMX encoding \"Binary 3\" or later",
	'es': "El formato DMX \"Model {0}\" requiere codificación \"Binary 3\" o superior",
},
'exporter_prop_group': {
	'ja': "グループの名前",
	'en': "Group Name",
	'es': "Nombre de grupo",
},
'qc_compile_tip': {
	'en': "Compile QCs with the Source SDK",
	'es': "Compilar QCs con el SDK de Source",
},
'exporter_report_suffix': {
	'en': " with {0} Errors and {1} Warnings",
	'es': " con {0} errores y {1} advertencias",
},
'exporter_err_groupempty': {
	'en': "Group {0} has no active objects",
	'es': "El grupo {0} no tiene objetos activos",
},
'exporter_err_dmxother': {
	'en': "Cannot export DMX. Resolve errors with the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
	'es': "No se puede exportar DMX. Corrija los errores en el panel de exportación.",
},
'exporter_prop_group_tip': {
	'ja': "エクスポートにグループの名前",
	'en': "Name of the Group to export",
	'es': "Nombre del grupo a exportar",
},
'exporter_warn_multiarmature': {
	'en': "Multiple armatures detected",
	'es': "Se detectaron múltiples armaduras",
},
'exporter_err_solidifyinside': {
	'en': "Curve {0} has the Solidify modifier with rim fill, but is still exporting polys on both sides.",
	'es': "La curva {0} tiene el modificador Solidify pero exporta polígonos en ambos lados.",
},
'exporter_err_dupeenv_con': {
	'en': "Bone constraint \"{0}\" found on \"{1}\", which already has a bone parent. Ignoring.",
	'es': "Restricción de hueso \"{0}\" en \"{1}\" que ya tiene un hueso padre. Ignorando.",
},
'exporter_err_unconfigured': {
	'en': "Scene unconfigured. See the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
	'es': "Escena no configurada. Ver panel de exportación en propiedades de escena.",
},
'exporter_err_makedirs': {
	'en': "Could not create export folder. Python reports: {0}",
	'es': "No se pudo crear carpeta de exportación. Error de Python: {0}",
},
'exporter_warn_weightlinks_excess': {
	'en': "{0} verts on \"{1}\" have over {2} weight links. Source does not support this!",
	'es': "¡{0} vértices en \"{1}\" tienen más de {2} pesos (no soportado en Source)!",
},
'exporter_err_noframes': {
	'en': "Armature {0} has no animation frames to export",
	'es': "La armadura {0} no tiene fotogramas de animación para exportar",
},
'exporter_report_menu': {
	'ja': "レポート：Source Tools エラー",
	'en': "Source Tools Error Report",
	'es': "Reporte de errores de Source Tools",
},
'exporter_report': {
	'ja': "{0}つファイルは{1}秒エクスポート",
	'en': "{0} files exported in {1} seconds",
	'es': "{0} archivos exportados en {1} segundos",
},
'exporter_err_groupmuted': {
	'ja': "ゲルーポ「{0}」はミュートです",
	'en': "Group {0} is suppressed",
	'es': "El grupo {0} está suprimido",
},
'exporter_title': {
	'ja': "SMD/VTA/DMXをエクスポート",
	'en': "Export SMD/VTA/DMX",
	'es': "Exportar SMD/VTA/DMX",
},
'qc_compile_err_unknown': {
	'en': "Compile of {0} failed. Check the console for details",
	'es': "Falló la compilación de {0}. Ver consola para detalles.",
},
'exporter_err_splitvgroup_missing': {
	'en': "Could not find stereo split Vertex Group \"{0}\" on object \"{1}\"",
	'es': "No se encontró el grupo de vértices \"{0}\" en el objeto \"{1}\"",
},
'importer_complete': {
	'en': "Imported {0} files in {1} seconds",
	'es': "Se importaron {0} archivos en {1} segundos",
},
'importer_bonemode': {
	'ja': "ボーンカスタムシェイプ",
	'en': "Bone shapes",
	'es': "Formas de huesos",
},
'importer_err_nofile': {
	'ja': "選択ファイルはありません",
	'en': "No file selected",
	'es': "No se seleccionó archivo",
},
'importer_err_smd': {
	'en': "Could not open SMD file \"{0}\": {1}",
	'es': "No se pudo abrir el archivo SMD \"{0}\": {1}",
},
'importer_qc_macroskip': {
	'en': "Skipping macro in QC {0}",
	'es': "Omitiendo macro en QC {0}",
},
'importer_bones_validate_desc': {
	'en': "Report new bones as missing without making any changes to the target Armature",
	'es': "Reportar huesos nuevos como faltantes sin modificar la armadura",
},
'importer_tip': {
	'en': "Imports uncompiled Source Engine model data",
	'es': "Importa datos de modelos sin compilar",
},
'importer_title': {
	'ja': "インポート SMD/VTA, DMX, QC",
	'en': "Import SMD/VTA, DMX, QC",
	'es': "Importar SMD/VTA, DMX, QC",
},
'importer_makecamera': {
	'ja': "$originにカメラを生成",
	'en': "Make Camera At $origin",
	'es': "Crear cámara en $origin",
},
'importer_bone_parent_miss': {
	'en': "Parent mismatch for bone \"{0}\": \"{1}\" in Blender, \"{2}\" in {3}.",
	'es': "Discrepancia en padre del hueso \"{0}\": \"{1}\" en Blender, \"{2}\" en {3}.",
},
'importer_makecamera_tip': {
	'en': "For use in viewmodel editing; if not set, an Empty will be created instead",
	'es': "Para edición de viewmodels. Si no está activo, se creará un Empty",
},
'importer_err_shapetarget': {
	'en': "Could not import shape keys: no valid target object found",
	'es': "No se pudieron importar formas: no se encontró objeto objetivo",
},
'importer_rotmode_tip': {
	'en': "Determines the type of rotation Keyframes created when importing bones or animation",
	'es': "Determina el tipo de fotogramas clave de rotación al importar",
},
'importer_skipremdoubles_tip': {
	'en': "Import raw, disconnected polygons from SMD files; these are harder to edit but a closer match to the original mesh",
	'es': "Importar polígonos desconectados de archivos SMD (más difíciles de editar pero más fieles al original)",
},
'importer_balance_group': {
	'en': "DMX Stereo Balance",
	'es': "Balance estéreo DMX",
},
'importer_bones_mode_desc': {
	'en': "How to behave when a reference mesh import introduces new bones to the target Armature (ignored for QCs)",
	'es': "Comportamiento cuando una malla introduce huesos nuevos (ignorado para QCs)",
},
'importer_rotmode': {
	'ja': "回転モード",
	'en': "Rotation mode",
	'es': "Modo de rotación",
},
'importer_skipremdoubles': {
	'ja': "SMDのポリゴンと法線を保持",
	'en': "Preserve SMD Polygons & Normals",
	'es': "Preservar polígonos y normales SMD",
},
'importer_bonemode_tip': {
	'en': "How bones in new Armatures should be displayed",
	'es': "Cómo mostrar huesos en nuevas armaduras",
},
'importer_bones_append': {
	'ja': "対象で追加",
	'en': "Append to Target",
	'es': "Anexar al objetivo",
},
'importer_err_qci': {
	'en': "Could not open QC $include file \"{0}\" - skipping!",
	'es': "No se pudo abrir archivo $include \"{0}\" - ¡omitido!",
},
'importer_up_tip': {
	'en': "Which axis represents 'up' (ignored for QCs)",
	'es': "Qué eje representa 'arriba' (ignorado para QCs)",
},
'importer_err_namelength': {
	'en': "{0} name \"{1}\" is too long to import. Truncating to \"{2}\"",
	'es': "El nombre de {0} \"{1}\" es demasiado largo. Truncando a \"{2}\"",
},
'importer_bones_append_desc': {
	'en': "Add new bones to the target Armature",
	'es': "Añadir huesos nuevos a la armadura objetivo",
},
'importer_err_unmatched_mesh': {
	'en': "{0} VTA vertices ({1}%) were not matched to a mesh vertex! An object with a vertex group has been created to show where the VTA file's vertices are.",
	'es': "¡{0} vértices VTA ({1}%) no coincidieron con la malla! Se creó un objeto con grupo de vértices para mostrar su ubicación.",
},
'importer_bones_validate': {
	'ja': "対象で確認",
	'en': "Validate Against Target",
	'es': "Validar con objetivo",
},
'importer_name_nomat': {
	'ja': "UndefinedMaterial",
	'en': "UndefinedMaterial",
	'es': "MaterialIndefinido",
},
'importer_bones_newarm_desc': {
	'en': "Make a new Armature for this import",
	'es': "Crear nueva armadura para esta importación",
},
'importer_err_refanim': {
	'en': "Found animation in reference mesh \"{0}\", ignoring!",
	'es': "¡Se encontró animación en malla de referencia \"{0}\" (ignorada)!",
},
'importer_bones_mode': {
	'ja': "ボーンの追加がモード",
	'en': "Bone Append Mode",
	'es': "Modo de anexión de huesos",
},
'importer_err_badweights': {
	'en': "{0} vertices weighted to invalid bones on {1}",
	'es': "{0} vértices con pesos en huesos inválidos en {1}",
},
'importer_err_bonelimit_smd': {
	'en': "SMD only supports 128 bones!",
	'es': "¡SMD sólo soporta 128 huesos!",
},
'importer_err_badfile': {
	'en': "Format of {0} not recognised",
	'es': "Formato de {0} no reconocido",
},
'importer_err_smd_ver': {
	'en': "Unrecognised/invalid SMD file. Import will proceed, but may fail!",
	'es': "Archivo SMD no reconocido/inválido. Se intentará importar pero puede fallar.",
},
'importer_doanims': {
	'ja': "アニメーションをインポート",
	'en': "Import Animations",
	'es': "Importar animaciones",
},
'importer_use_collections':{
	'en': "Create Collections",	
	'es': "Crear colecciones",
},
'importer_use_collections_tip':{
	'en': "Create a Blender collection for each imported mesh file. This retains the original file structure (important for DMX) and makes it easy to switch between LODs etc. with the number keys",
	'es': "Crear una colección por archivo importado. Conserva la estructura original (importante para DMX) y facilita cambiar entre LODs con teclas numéricas",
},
'importer_err_missingbones': {
	'en': "{0} contains {1} bones not present in {2}. Check the console for a list.",
	'es': "{0} contiene {1} huesos no presentes en {2}. Ver consola para lista.",
},
'importer_err_noanimationbones': {
	'en': "No bones imported for animation {0}",
	'es': "No se importaron huesos para la animación {0}",
},
'importer_name_unmatchedvta': {
	'en': "Unmatched VTA",
	'es': "VTA no coincidente",
},
'importer_bones_newarm': {
	'ja': "アーマティアを生成",
	'en': "Make New Armature",
	'es': "Crear nueva armadura",
},
'qc_warn_noarmature': {
	'en': "Skipping {0}; no armature found.",
	'es': "Omitiendo {0}; no se encontró armadura.",
},
'exportstate_pattern_tip': {
	'en': "Visible objects with this string in their name will be affected",
	'es': "Afecta objetos visibles con este texto en su nombre",
},
'exportstate': {
	'en': "Set Source Tools export state",
	'es': "Establecer estado de exportación",
},
'activate_dep_shapes': {
	'en': "Activate Dependency Shapes",
	'es': "Activar formas dependientes",
},
'gen_block_success': {
	'en': "DMX written to text block \"{0}\"",
	'es': "DMX escrito en bloque de texto \"{0}\"",
},
'gen_block': {
	'ja': "DMXフレックスのコントローラーの抜粋を生成します",
	'en': "Generate DMX Flex Controller block",
	'es': "Generar bloque de controladores flex DMX",
},
'vca_add_tip': {
	'en': "Add a Vertex Animation to the active Source Tools exportable",
	'es': "Añadir animación de vértices al exportable activo",
},
'insert_uuid': {
	'en': "Insert UUID",
	'es': "Insertar UUID",
},
'launch_hlmv_tip': {
	'en': "Launches Half-Life Model Viewer",
	'es': "Abre el visor de modelos de Half-Life",
},
'vertmap_remove': {
	'en': "Remove Source 2 Vertex Map",
	'es': "Eliminar mapa de vértices de Source 2",
},
'activate_dep_shapes_tip': {
	'en': "Activates shapes found in the name of the current shape (underscore delimited)",
	'es': "Activa formas encontradas en el nombre de la forma actual (separadas por guión bajo)",
},
'vca_qcgen_tip': {
	'en': "Copies a QC segment for this object's Vertex Animations to the clipboard",
	'es': "Copia un segmento QC para las animaciones de vértices al portapapeles",
},
'vca_remove_tip': {
	'en': "Remove the active Vertex Animation from the active Source Tools exportable",
	'es': "Eliminar animación de vértices activa del exportable",
},
'vca_add': {
	'en': "Add Vertex Animation",
	'es': "Añadir animación de vértices",
},
'vertmap_select': {
	'en': "Select Source 2 Vertex Map",
	'es': "Seleccionar mapa de vértices de Source 2",
},
'vca_preview': {
	'ja': "頂点アニメーションを再生します",
	'en': "Preview Vertex Animation",
	'es': "Previsualizar animación de vértices",
},
'activate_dep_shapes_success': {
	'en': "Activated {0} dependency shapes",
	'es': "Se activaron {0} formas dependientes",
},
'launch_hlmv': {
	'ja': "HLMVを開始",
	'en': "Launch HLMV",
	'es': "Abrir HLMV",
},
'exportstate_pattern': {
	'en': "Search pattern",
	'es': "Patrón de búsqueda",
},
'insert_uuid_tip': {
	'en': "Inserts a random UUID at the current location",
	'es': "Inserta un UUID aleatorio en la ubicación actual",
},
'gen_block_tip': {
	'en': "Generate a simple Flex Controller DMX block",
	'es': "Generar bloque DMX simple de controladores flex",
},
'gen_drivers': {
	'ja': "是正シェイプキーのドライバーを生成します",
	'en': "Generate Corrective Shape Key Drivers",
	'es': "Generar controladores para formas correctivas",
},
'apply_drivers':{
	'en': "Regenerate Shape Key Names From Drivers",
	'es': "Renombrar formas según controladores",
},
'apply_drivers_tip':{
	'en': "Renames corrective shape keys so that each their names are a combination of the shape keys that control them (via Blender animation drivers)",
	'es': "Renombra formas correctivas según los controladores que las activan",
},
'apply_drivers_success':{
	'en': "{0} shapes renamed.",
	'es': "{0} formas renombradas.",
},
'vca_qcgen': {
	'ja': "QCの抜粋を生成します",
	'en': "Generate QC Segment",
	'es': "Generar segmento QC",
},
'vertmap_create': {
	'en': "Create Source 2 Vertex Map",
	'es': "Crear mapa de vértices de Source 2",
},
'vca_preview_tip': {
	'en': "Plays the active Source Tools Vertex Animation using scene preview settings",
	'es': "Reproduce la animación de vértices con la configuración actual",
},
'vca_remove': {
	'en': "Remove Vertex Animation",
	'es': "Eliminar animación de vértices",
},
'gen_drivers_tip': {
	'en': "Adds Blender animation drivers to corrective Source engine shapes",
	'es': "Añade controladores de Blender a formas correctivas",
},
'qc_path': {
	'ja': "QCのパス",
	'en': "QC Path",
	'es': "Ruta de QCs",
},
'engine_path': {
	'ja': "エンジンのパス",
	'en': "Engine Path",
	'es': "Ruta del motor",
},
'game_path_tip': {
	'en': "Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",
	'es': "Directorio con gameinfo.txt (si no se especifica, se usará VPROJECT)",
},
'visible_only': {
	'ja': "たった可視のレイヤー",
	'en': "Visible layers only",
	'es': "Sólo capas visibles",
},
'dmx_encoding': {
	'ja': "DMXの符号化",
	'en': "DMX encoding",
	'es': "Codificación DMX",
},
'game_path': {
	'ja': "ゲームのパス",
	'en': "Game Path",
	'es': "Ruta del juego",
},
'up_axis': {
	'ja': "対象の上昇軸",
	'en': "Target Up Axis",
	'es': "Eje superior objetivo",
},
'dmx_format': {
	'ja': "DMXのフォーマット",
	'en': "DMX format",
	'es': "Formato DMX",
},
'ignore_materials': {
	'ja': "Blenderのマテリアルを軽視",
	'en': "Ignore Blender Materials",
	'es': "Ignorar materiales de Blender",
},
'visible_only_tip': {
	'en': "Ignore objects in hidden layers",
	'es': "Ignorar objetos en capas ocultas",
},
'active_exportable': {
	'ja': "アクティブ・エクスポート可能",
	'en': "Active exportable",
	'es': "Exportable activo",
},
'exportroot_tip': {
	'en': "The root folder into which SMD and DMX exports from this scene are written",
	'es': "Carpeta raíz para exportaciones SMD/DMX de esta escena",
},
'qc_compilenow': {
	'ja': "今全てはコンパイル",
	'en': "Compile All Now",
	'es': "Compilar todo ahora",
},
'up_axis_tip': {
	'en': "Use for compatibility with data from other 3D tools",
	'es': "Para compatibilidad con datos de otras herramientas 3D",
},
'smd_format': {
	'ja': "対象のエンジン",
	'en': "Target Engine",
	'es': "Motor objetivo",
},
'dmx_mat_path_tip': {
	'en': "Folder relative to game root containing VMTs referenced in this scene (DMX only)",
	'es': "Carpeta relativa a la raíz con VMTs referenciados (sólo DMX)",
},
'qc_compileall_tip': {
	'en': "Compile all QC files whenever anything is exported",
	'es': "Compilar todos los QCs al exportar",
},
'qc_path_tip': {
	'en': "This scene's QC file(s); Unix wildcards supported",
	'es': "Archivo(s) QC de esta escena (admite comodines Unix)",
},
'qc_nogamepath': {
	'en': "No Game Path and invalid VPROJECT",
	'es': "Sin ruta de juego y VPROJECT inválido",
},
'dmx_mat_path': {
	'ja': "マテリアルのパス",
	'en': "Material Path",
	'es': "Ruta de materiales",
},
'exportroot': {
	'ja': "エクスポートのパス",
	'en': "Export Path",
	'es': "Ruta de exportación",
},
'export_format': {
	'ja': "エクスポートのフォーマット",
	'en': "Export Format",
	'es': "Formato de exportación",
},
'qc_compileall': {
	'ja': "エクスポートから、みんあがコンパイル",
	'en': "Compile all on export",
	'es': "Compilar todo al exportar",
},
'dmx_weightlinkcull': {
	'ja': "ウェイト・リンクの間引きのしきい値",
	'en': "Weight Link Cull Threshold",
	'es': "Umbral de pesos",
},
'dmx_weightlinkcull_tip': {
	'en': "The maximum strength at which a weight link can be removed to comply with Source's per-vertex link limit",
	'es': "Fuerza máxima a la que se puede eliminar un peso para cumplir el límite de Source",
},
'dmx_encoding_tip': {
	'en': "Manual override for binary DMX encoding version",
	'es': "Anular versión de codificación DMX binaria",
},
'dmx_format_tip': {
	'en': "Manual override for DMX model format version",
	'es': "Anular versión de formato DMX",
},
'engine_path_tip': {
	'en': "Directory containing studiomdl (Source 1) or resourcecompiler (Source 2)",
	'es': "Directorio con studiomdl (Source 1) o resourcecompiler (Source 2)",
},
'ignore_materials_tip': {
	'en': "Only export face-assigned image filenames",
	'es': "Sólo exportar nombres de imágenes asignadas a caras",
},
'updater_title': {
	'ja': "更新Source Toolsの確認",
	'en': "Check for Source Tools updates",
	'es': "Buscar actualizaciones de Source Tools",
},
'update_err_downloadfailed': {
	'en': "Could not complete download:",
	'es': "No se pudo completar la descarga:",
},
'offerchangelog_offer': {
	'en': "Restart Blender to complete the update. Click to view the changelog.",
	'es': "Reinicia Blender para completar la actualización. Haz clic para ver los cambios.",
},
'update_err_outdated': {
	'en': "The latest Source Tools require Blender {0}. Please upgrade.",
	'es': "Las últimas Source Tools requieren Blender {0}. Por favor actualiza.",
},
'update_err_unknown': {
	'en': "Could not install update:",
	'es': "No se pudo instalar la actualización:",
},
'offerchangelog_title': {
	'en': "Source Tools Update",
	'es': "Actualización de Source Tools",
},
'update_err_corruption': {
	'en': "Update was downloaded, but file was not valid",
	'es': "Se descargó la actualización pero el archivo no era válido",
},
'update_done': {
	'en': "Installed Source Tools {0}!",
	'es': "¡Se instalaron Source Tools {0}!",
},
'updater_title_tip': {
	'en': "Connects to http://steamreview.org/BlenderSourceTools/latest.php",
	'es': "Se conecta a http://steamreview.org/BlenderSourceTools/latest.php",
},
'update_alreadylatest': {
	'en': "The latest Source Tools ({0}) are already installed.",
	'es': "Ya están instaladas las últimas Source Tools ({0}).",
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
