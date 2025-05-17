#coding=utf-8
_languages = ['ja']

_data = {
'vca_sequence': {
	'ja': "シクウェンスを生成します",
	'en': "Generate Sequence",
},
'controllers_simple_tip': {
	'en': "Generate one flex controller per shape key",
},
'vertmap_group_props': {
	'en': "Vertex Maps",
},
'action_selection_filter_tip': {
	'en': "All actions that match the armature's filter term and have users",
},
'curve_poly_side_fwd': {
	'en': "Forward (outer) side",
},
'action_selection_current_tip': {
	'en': "The armature's currently assigned action or NLA tracks",
},
'action_slot_selection_current_tip': {
	'en': "The armature's active action slot",
},
'valvesource_cloth_enable': {
	'en': "Cloth Physics Enable",
},
'subdir_tip': {
	'en': "Optional path relative to scene output folder",
},
'controllers_mode': {
	'ja': "DMXフレックスのコントローラー生成",
	'en': "DMX Flex Controller generation",
},
'scene_export': {
	'ja': "シーンをエクスポート",
	'en': "Scene Export",
},
'shape_stereo_mode_tip': {
	'en': "How stereo split balance should be defined",
},
'bone_rot_legacy': {
	'en': "Legacy rotation",
},
'controllers_advanced_tip': {
	'en': "Insert the flex controllers of an existing DMX file",
},
'triangulate_tip': {
	'en': "Avoids concave DMX faces, which are not supported by Source",
},
'action_filter': {
	'ja': "アクションフィルター",
	'en': "Action Filter",
},
'slot_filter': {
	'en': "Slot Filter",
},
'vca_start_tip': {
	'en': "Scene frame at which to start recording Vertex Animation",
},
'action_filter_tip': {
	'en': "Actions with names matching this filter pattern and which have users will be exported",
},
'slot_filter_tip': {
	'en': "Slots of the assigned Action with names matching this wildcard filter pattern will be exported (blank to export everything)",
},
'shape_stereo_sharpness_tip': {
	'en': "How sharply stereo flex shapes should transition from left to right",
},
'vca_sequence_tip': {
	'en': "On export, generate an animation sequence that drives this Vertex Animation",
},
'shape_stereo_mode': {
	'en': "DMX stereo split mode",
},
'dummy_bone': {
	'en': "Implicit motionless bone",
},
'vca_group_props': {
	'ja': "頂点アニメーション",
	'en': "Vertex Animation",
},
'curve_poly_side': {
	'ja': "ポリゴン生成",
	'en': "Polygon Generation",
},
'group_merge_mech': {
	'ja': "メカニカルな局部は結合",
	'en': "Merge mechanical parts",
},
'action_selection_mode_tip': {
	'en': "How actions are selected for export",
},
'use_scene_export_tip': {
	'en': "Export this item with the scene",
},
'curve_poly_side_back': {
	'en': "Backward (inner) side",
},
'valvesource_vertex_blend': {
	'en': "Blend Params RGB",
},
'bone_rot_legacy_tip': {
	'en': "Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",
},
'controller_source': {
	'ja': "DMXフレックスのコントローラーのソースファイル ",
	'en': "DMX Flex Controller source",
},
'group_suppress_tip': {
	'en': "Export this group's objects individually",
},
'action_selection_current': {
	'ja': "現在 / NLA",
	'en': "Current / NLA",
},
'action_slot_current': {
	'ja': "現在のアクションスロット",
	'en': "Current Action Slot",
},
'shape_stereo_sharpness': {
	'en': "DMX stereo split sharpness",
},
'group_suppress': {
	'ja': "ミュート",
	'en': "Suppress",
},
'shape_stereo_vgroup': {
	'en': "DMX stereo split vertex group",
},
'shape_stereo_vgroup_tip': {
	'en': "The vertex group that defines stereo balance (0=Left, 1=Right)",
},
'controllers_source_tip': {
	'en': "A DMX file (or Text datablock) containing flex controllers",
},
'valvesource_vertex_blend1': {
	'en': "Blend Params Extra (?)",
},
'curve_poly_side_tip': {
	'en': "Determines which side(s) of this curve will generate polygons when exported",
},
'triangulate': {
	'ja': "三角測量",
	'en': "Triangulate",
},
'curve_poly_side_both': {
	'en': "Both sides",
},
'group_merge_mech_tip': {
	'en': "Optimises DMX export of meshes sharing the same parent bone",
},
'action_selection_mode': {
	'en': "Action Selection",
},
'shape_stereo_mode_vgroup': {
	'en': "Use a vertex group to define stereo balance",
},
'vca_end_tip': {
	'en': "Scene frame at which to stop recording Vertex Animation",
},
'valvesource_vertex_paint': {
	'en': "Vertex Paint",
},
'controllers_mode_tip': {
	'en': "How flex controllers are defined",
},
'subdir': {
	'en': "Subfolder",
},
'dummy_bone_tip': {
	'en': "Create a dummy bone for vertices which don't move. Emulates Blender's behaviour in Source, but may break compatibility with existing files (SMD only)",
},
'exportpanel_steam': {
	'ja': "Steam コミュニティ",
	'en': "Steam Community",
},
'exportables_arm_filter_result': {
	'ja': "「{0}」アクション～{1}",
	'en': "\"{0}\" actions ({1})",
},
'exportables_arm_no_slot_filter': {
	'en': "All action slots ({0}) for \"{1}\"",
},
'exportables_flex_count_corrective': {
	'ja': "是正シェイプ：{0}",
	'en': "Corrective Shapes: {0}",
},
'exportables_curve_polyside': {
	'ja': "ポリゴン生成：",
	'en': "Polygon Generation:",
},
'exportmenu_title': {
	'ja': "Source Tools エクスポート",
	'en': "Source Tools Export",
},
'exportables_flex_help': {
	'ja': "フレックス・コントローラーのヘレプ",
	'en': "Flex Controller Help",
},
'exportpanel_title': {
	'ja': "Source Engine エクスポート",
	'en': "Source Engine Export",
},
'exportables_flex_src': {
	'ja': "コントローラーのソースファイル ",
	'en': "Controller Source",
},
'exportmenu_invalid': {
	'en': "Cannot export selection",
},
'qc_title': {
	'ja': "Source Engine QCのコンパイル",
	'en': "Source Engine QC Compiles",
},
'exportables_flex_props': {
	'ja': "フレックスのプロパティ",
	'en': "Flex Properties",
},
'exportables_flex_generate': {
	'ja': "コントローラーを生成します",
	'en': "Generate Controllers",
},
'exportables_flex_split': {
	'ja': "ステレオフルックスの差額：",
	'en': "Stereo Flex Balance:",
},
'exportables_group_mute_suffix': {
	'ja': "(ミユト)",
	'en': "(suppressed)",
},
'exportmenu_scene': {
	'ja': "シーンをエクスポート ({0}つファイル)",
	'en': "Scene export ({0} files)",
},
'exportpanel_dmxver': {
	'ja': "DMXのバージョン：",
	'en': "DMX Version:",
},
'exportpanel_update': {
	'ja': "更新アドオンの確認",
	'en': "Check for updates",
},
'exportables_title': {
	'ja': "Source Engineのエクスポート可能",
	'en': "Source Engine Exportables",
},
'exportables_armature_props': {
	'ja': "アーマティアのプロパティ",
	'en': "Armature Properties ({0})",
},
'qc_bad_enginepath': {
	'ja': "エンジンのパスが無効です",
	'en': "Invalid Engine Path",
},
'qc_invalid_source2': {
	'ja': "Source Engine 2はQCファイルが使いません",
	'en': "QC files do not exist in Source 2",
},
'exportmenu_selected': {
	'en': "Selected objects ({0} files)",
},
'exportables_group_props': {
	'ja': "グループのプロパティ",
	'en': "Group Properties",
},
'qc_no_enginepath': {
	'ja': "エンジンのパスはありません",
	'en': "No Engine Path provided",
},
'exportables_curve_props': {
	'ja': "カーブのプロパティ",
	'en': "Curve Properties",
},
'exportables_flex_count': {
	'ja': "シェイプ：{0}",
	'en': "Shapes: {0}",
},
'activate_dependency_shapes': {
	'en': "Activate dependency shapes",
},
'settings_prop': {
	'en': "Blender Source Tools settings",
},
'bl_info_description': {
	'en': "Importer and exporter for Valve Software's Source Engine. Supports SMD\\VTA, DMX and QC.",
},
'export_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx)",
},
'help': {
	'ja': "ヘレプ",
	'en': "Help",
},
'bl_info_location': {
	'ja': "ファイル > インポート / エクスポート、シーンのプロパティ",
	'en': "File > Import/Export, Scene properties",
},
'import_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx, .qc)",
},
'exporter_err_nogroupitems': {
	'en': "Nothing in Group \"{0}\" is enabled for export",
},
'exporter_report_qc': {
	'en': "{0} files exported and {2} QCs compiled ({3}/{4}) in {1} seconds",
},
'exporter_err_relativeunsaved': {
	'en': "Cannot export to a relative path until the blend file has been saved.",
},
'exporter_err_nopolys': {
	'en': "Object {0} has no polygons, skipping",
},
'exporter_err_hidden': {
	'en': "Skipping {0}: object cannot be selected, probably due to being hidden by an animation driver.",
},
'exporter_err_arm_nonuniform': {
	'en': "Armature \"{0}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.",
},
'exporter_err_facesnotex_ormat': {
	'en': "{0} faces on {1} did not have a Material or Texture assigned",
},
'exporter_err_arm_noanims': {
	'en': "Couldn't find any animation for Armature \"{0}\"",
},
'exporter_err_dupeenv_arm': {
	'en': "Armature modifier \"{0}\" found on \"{1}\", which already has a bone parent or constraint. Ignoring.",
},
'exporter_err_bonelimit': {
	'en': "Exported {0} bones, but SMD only supports {1}!",
},
'exporter_err_unmergable': {
	'en': "Skipping vertex animations on Group \"{0}\", which could not be merged into a single DMX object due to its envelope. To fix this, either ensure that the entire Group has the same bone parent or remove all envelopes.",
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
},
'qc_compile_err_nofiles': {
	'en': "Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.",
},
'exporter_err_missing_corrective_target': {
	'en': "Found corrective shape key \"{0}\", but not target shape \"{1}\"",
},
'qc_compile_complete': {
	'ja': "{0}つ「{1}」QCがコンパイルしました",
	'en': "Compiled {0} {1} QCs",
},
'exporter_err_shapes_decimate': {
	'en': "Cannot export shape keys from \"{0}\" because it has a '{1}' Decimate modifier. Only Un-Subdivide mode is supported.",
},
'exporterr_goldsrc_multiweights': {
	'en': "{0} verts on \"{1}\" have multiple weight links. GoldSrc does not support this!",
},
'exporter_err_splitvgroup_undefined': {
	'en': "Object \"{0}\" uses Vertex Group stereo split, but does not define a Vertex Group to use.",
},
'exporter_err_open': {
	'en': "Could not create {0} file. Python reports: {1}.",
},
'qc_compile_title': {
	'ja': "QCコンパイル",
	'en': "Compile QC",
},
'exporter_err_noexportables': {
	'en': "Found no valid objects for export",
},
'exporter_warn_sanitised_filename': {
	'en': "Sanitised exportable name \"{0}\" to \"{1}\"",
},
'exporter_warn_correctiveshape_duplicate': {
	'en': "Corrective shape key \"{0}\" has the same activation conditions ({1}) as \"{2}\". Skipping.",
},
'exporter_err_flexctrl_missing': {
	'en': "No flex controller defined for shape {0}.",
},
'qc_compile_err_compiler': {
	'en': "Could not execute studiomdl from \"{0}\"",
},
'exporter_err_facesnotex': {
	'en': "{0} faces on {1} did not have a Texture assigned",
},
'exporter_err_flexctrl_undefined': {
	'en': "Could not find flex controllers for \"{0}\"",
},
'exporter_warn_source2smdsupport': {
	'en': "Source 2 no longer supports SMD.",
},
'exporter_tip': {
	'en': "Export and compile Source Engine models",
},
'exporter_warn_weightlinks_culled': {
	'en': "{0} excess weight links beneath scene threshold of {1:0.2} culled on \"{2}\".",
},
'exporter_prop_scene_tip': {
	'en': "Export all items selected in the Source Engine Exportables panel",
},
'exporter_err_dmxenc': {
	'en': "DMX format \"Model {0}\" requires DMX encoding \"Binary 3\" or later",
},
'exporter_prop_group': {
	'ja': "グループの名前",
	'en': "Group Name",
},
'qc_compile_tip': {
	'en': "Compile QCs with the Source SDK",
},
'exporter_report_suffix': {
	'en': " with {0} Errors and {1} Warnings",
},
'exporter_err_groupempty': {
	'en': "Group {0} has no active objects",
},
'exporter_err_dmxother': {
	'en': "Cannot export DMX. Resolve errors with the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
},
'exporter_prop_group_tip': {
	'ja': "エクスポートにグループの名前",
	'en': "Name of the Group to export",
},
'exporter_warn_multiarmature': {
	'en': "Multiple armatures detected",
},
'exporter_err_solidifyinside': {
	'en': "Curve {0} has the Solidify modifier with rim fill, but is still exporting polys on both sides.",
},
'exporter_err_dupeenv_con': {
	'en': "Bone constraint \"{0}\" found on \"{1}\", which already has a bone parent. Ignoring.",
},
'exporter_err_unconfigured': {
	'en': "Scene unconfigured. See the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
},
'exporter_err_makedirs': {
	'en': "Could not create export folder. Python reports: {0}",
},
'exporter_warn_weightlinks_excess': {
	'en': "{0} verts on \"{1}\" have over {2} weight links. Source does not support this!",
},
'exporter_report_menu': {
	'ja': "レポート：Source Tools エラー",
	'en': "Source Tools Error Report",
},
'exporter_report': {
	'ja': "{0}つファイルは{1}秒エクスポート",
	'en': "{0} files exported in {1} seconds",
},
'exporter_err_groupmuted': {
	'ja': "ゲルーポ「{0}」はミュートです",
	'en': "Group {0} is suppressed",
},
'exporter_title': {
	'ja': "SMD/VTA/DMXをエクスポート",
	'en': "Export SMD/VTA/DMX",
},
'qc_compile_err_unknown': {
	'en': "Compile of {0} failed. Check the console for details",
},
'exporter_err_splitvgroup_missing': {
	'en': "Could not find stereo split Vertex Group \"{0}\" on object \"{1}\"",
},
'importer_complete': {
	'en': "Imported {0} files in {1} seconds",
},
'importer_bonemode': {
	'ja': "ボーンカスタムシェイプ",
	'en': "Bone shapes",
},
'importer_err_nofile': {
	'ja': "選択ファイルはありません",
	'en': "No file selected",
},
'importer_err_smd': {
	'en': "Could not open SMD file \"{0}\": {1}",
},
'importer_qc_macroskip': {
	'en': "Skipping macro in QC {0}",
},
'importer_bones_validate_desc': {
	'en': "Report new bones as missing without making any changes to the target Armature",
},
'importer_tip': {
	'en': "Imports uncompiled Source Engine model data",
},
'importer_title': {
	'ja': "インポート SMD/VTA, DMX, QC",
	'en': "Import SMD/VTA, DMX, QC",
},
'importer_makecamera': {
	'ja': "$originにカメラを生成",
	'en': "Make Camera At $origin",
},
'importer_bone_parent_miss': {
	'en': "Parent mismatch for bone \"{0}\": \"{1}\" in Blender, \"{2}\" in {3}.",
},
'importer_makecamera_tip': {
	'en': "For use in viewmodel editing; if not set, an Empty will be created instead",
},
'importer_err_shapetarget': {
	'en': "Could not import shape keys: no valid target object found",
},
'importer_rotmode_tip': {
	'en': "Determines the type of rotation Keyframes created when importing bones or animation",
},
'importer_skipremdoubles_tip': {
	'en': "Import raw, disconnected polygons from SMD files; these are harder to edit but a closer match to the original mesh",
},
'importer_balance_group': {
	'en': "DMX Stereo Balance",
},
'importer_bones_mode_desc': {
	'en': "How to behave when a reference mesh import introduces new bones to the target Armature (ignored for QCs)",
},
'importer_rotmode': {
	'ja': "回転モード",
	'en': "Rotation mode",
},
'importer_skipremdoubles': {
	'ja': "SMDのポリゴンと法線を保持",
	'en': "Preserve SMD Polygons & Normals",
},
'importer_bonemode_tip': {
	'en': "How bones in new Armatures should be displayed",
},
'importer_bones_append': {
	'ja': "対象で追加",
	'en': "Append to Target",
},
'importer_err_qci': {
	'en': "Could not open QC $include file \"{0}\" - skipping!",
},
'importer_up_tip': {
	'en': "Which axis represents 'up' (ignored for QCs)",
},
'importer_err_namelength': {
	'en': "{0} name \"{1}\" is too long to import. Truncating to \"{2}\"",
},
'importer_bones_append_desc': {
	'en': "Add new bones to the target Armature",
},
'importer_err_unmatched_mesh': {
	'en': "{0} VTA vertices ({1}%) were not matched to a mesh vertex! An object with a vertex group has been created to show where the VTA file's vertices are.",
},
'importer_bones_validate': {
	'ja': "対象で確認",
	'en': "Validate Against Target",
},
'importer_name_nomat': {
	'ja': "UndefinedMaterial",
	'en': "UndefinedMaterial",
},
'importer_bones_newarm_desc': {
	'en': "Make a new Armature for this import",
},
'importer_err_refanim': {
	'en': "Found animation in reference mesh \"{0}\", ignoring!",
},
'importer_bones_mode': {
	'ja': "ボーンの追加がモード",
	'en': "Bone Append Mode",
},
'importer_err_badweights': {
	'en': "{0} vertices weighted to invalid bones on {1}",
},
'importer_err_bonelimit_smd': {
	'en': "SMD only supports 128 bones!",
},
'importer_err_badfile': {
	'en': "Format of {0} not recognised",
},
'importer_err_smd_ver': {
	'en': "Unrecognised/invalid SMD file. Import will proceed, but may fail!",
},
'importer_doanims': {
	'ja': "アニメーションをインポート",
	'en': "Import Animations",
},
'importer_use_collections':{
	'en': "Create Collections",	
},
'importer_use_collections_tip':{
	'en': "Create a Blender collection for each imported mesh file. This retains the original file structure (important for DMX) and makes it easy to switch between LODs etc. with the number keys",
},
'importer_err_missingbones': {
	'en': "{0} contains {1} bones not present in {2}. Check the console for a list.",
},
'importer_err_noanimationbones': {
	'en': "No bones imported for animation {0}",
},
'importer_name_unmatchedvta': {
	'en': "Unmatched VTA",
},
'importer_bones_newarm': {
	'ja': "アーマティアを生成",
	'en': "Make New Armature",
},
'qc_warn_noarmature': {
	'en': "Skipping {0}; no armature found.",
},
'exportstate_pattern_tip': {
	'en': "Visible objects with this string in their name will be affected",
},
'exportstate': {
	'en': "Set Source Tools export state",
},
'activate_dep_shapes': {
	'en': "Activate Dependency Shapes",
},
'gen_block_success': {
	'en': "DMX written to text block \"{0}\"",
},
'gen_block': {
	'ja': "DMXフレックスのコントローラーの抜粋を生成します",
	'en': "Generate DMX Flex Controller block",
},
'vca_add_tip': {
	'en': "Add a Vertex Animation to the active Source Tools exportable",
},
'insert_uuid': {
	'en': "Insert UUID",
},
'launch_hlmv_tip': {
	'en': "Launches Half-Life Model Viewer",
},
'vertmap_remove': {
	'en': "Remove Source 2 Vertex Map",
},
'activate_dep_shapes_tip': {
	'en': "Activates shapes found in the name of the current shape (underscore delimited)",
},
'vca_qcgen_tip': {
	'en': "Copies a QC segment for this object's Vertex Animations to the clipboard",
},
'vca_remove_tip': {
	'en': "Remove the active Vertex Animation from the active Source Tools exportable",
},
'vca_add': {
	'en': "Add Vertex Animation",
},
'vertmap_select': {
	'en': "Select Source 2 Vertex Map",
},
'vca_preview': {
	'ja': "頂点アニメーションを再生します",
	'en': "Preview Vertex Animation",
},
'activate_dep_shapes_success': {
	'en': "Activated {0} dependency shapes",
},
'launch_hlmv': {
	'ja': "HLMVを開始",
	'en': "Launch HLMV",
},
'exportstate_pattern': {
	'en': "Search pattern",
},
'insert_uuid_tip': {
	'en': "Inserts a random UUID at the current location",
},
'gen_block_tip': {
	'en': "Generate a simple Flex Controller DMX block",
},
'gen_drivers': {
	'ja': "是正シェイプキーのドライバーを生成します",
	'en': "Generate Corrective Shape Key Drivers",
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
},
'vertmap_create': {
	'en': "Create Source 2 Vertex Map",
},
'vca_preview_tip': {
	'en': "Plays the active Source Tools Vertex Animation using scene preview settings",
},
'vca_remove': {
	'en': "Remove Vertex Animation",
},
'gen_drivers_tip': {
	'en': "Adds Blender animation drivers to corrective Source engine shapes",
},
'qc_path': {
	'ja': "QCのパス",
	'en': "QC Path",
},
'engine_path': {
	'ja': "エンジンのパス",
	'en': "Engine Path",
},
'game_path_tip': {
	'en': "Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",
},
'visible_only': {
	'ja': "たった可視のレイヤー",
	'en': "Visible layers only",
},
'dmx_encoding': {
	'ja': "DMXの符号化",
	'en': "DMX encoding",
},
'game_path': {
	'ja': "ゲームのパス",
	'en': "Game Path",
},
'up_axis': {
	'ja': "対象の上昇軸",
	'en': "Target Up Axis",
},
'dmx_format': {
	'ja': "DMXのフォーマット",
	'en': "DMX format",
},
'ignore_materials': {
	'ja': "Blenderのマテリアルを軽視",
	'en': "Ignore Blender Materials",
},
'visible_only_tip': {
	'en': "Ignore objects in hidden layers",
},
'active_exportable': {
	'ja': "アクティブ・エクスポート可能",
	'en': "Active exportable",
},
'exportroot_tip': {
	'en': "The root folder into which SMD and DMX exports from this scene are written",
},
'qc_compilenow': {
	'ja': "今全てはコンパイル",
	'en': "Compile All Now",
},
'up_axis_tip': {
	'en': "Use for compatibility with data from other 3D tools",
},
'smd_format': {
	'ja': "対象のエンジン",
	'en': "Target Engine",
},
'dmx_mat_path_tip': {
	'en': "Folder relative to game root containing VMTs referenced in this scene (DMX only)",
},
'qc_compileall_tip': {
	'en': "Compile all QC files whenever anything is exported",
},
'qc_path_tip': {
	'en': "This scene's QC file(s); Unix wildcards supported",
},
'qc_nogamepath': {
	'en': "No Game Path and invalid VPROJECT",
},
'dmx_mat_path': {
	'ja': "マテリアルのパス",
	'en': "Material Path",
},
'exportroot': {
	'ja': "エクスポートのパス",
	'en': "Export Path",
},
'export_format': {
	'ja': "エクスポートのフォーマット",
	'en': "Export Format",
},
'qc_compileall': {
	'ja': "エクスポートから、みんあがコンパイル",
	'en': "Compile all on export",
},
'dmx_weightlinkcull': {
	'ja': "ウェイト・リンクの間引きのしきい値",
	'en': "Weight Link Cull Threshold",
},
'dmx_weightlinkcull_tip': {
	'en': "The maximum strength at which a weight link can be removed to comply with Source's per-vertex link limit",
},
'dmx_encoding_tip': {
	'en': "Manual override for binary DMX encoding version",
},
'dmx_format_tip': {
	'en': "Manual override for DMX model format version",
},
'engine_path_tip': {
	'en': "Directory containing studiomdl (Source 1) or resourcecompiler (Source 2)",
},
'ignore_materials_tip': {
	'en': "Only export face-assigned image filenames",
},
'updater_title': {
	'ja': "更新Source Toolsの確認",
	'en': "Check for Source Tools updates",
},
'update_err_downloadfailed': {
	'en': "Could not complete download:",
},
'offerchangelog_offer': {
	'en': "Restart Blender to complete the update. Click to view the changelog.",
},
'update_err_outdated': {
	'en': "The latest Source Tools require Blender {0}. Please upgrade.",
},
'update_err_unknown': {
	'en': "Could not install update:",
},
'offerchangelog_title': {
	'en': "Source Tools Update",
},
'update_err_corruption': {
	'en': "Update was downloaded, but file was not valid",
},
'update_done': {
	'en': "Installed Source Tools {0}!",
},
'updater_title_tip': {
	'en': "Connects to http://steamreview.org/BlenderSourceTools/latest.php",
},
'update_alreadylatest': {
	'en': "The latest Source Tools ({0}) are already installed.",
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
