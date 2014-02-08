_languages = ['ru']

_data = {
'controllers_simple_tip': {
	'en': "Generate one flex controller per shape key",
},
'action_selection_filter_tip': {
	'en': "All actions that match the armature's filter term and have users",
},
'action_selection_current_tip': {
	'en': "The armature's currently assigned action or NLA tracks",
},
'subdir_tip': {
	'en': "Optional path relative to scene output folder",
},
'controllers_mode': {
	'en': "DMX Flex Controller generation",
},
'scene_export': {
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
	'en': "Avoids concave DMX faces, which are not supported by studiomdl",
},
'action_filter': {
	'en': "Action Filter",
},
'action_filter_tip': {
	'en': "Actions with names matching this filter pattern and have users will be exported",
},
'shape_stereo_sharpness_tip': {
	'en': "How sharply stereo flex shapes should transition from left to right",
},
'shape_stereo_mode': {
	'en': "DMX stereo split mode",
},
'dummy_bone': {
	'en': "Implicit motionless bone",
},
'curve_poly_side': {
	'en': "Polygon Generation",
},
'group_merge_mech': {
	'en': "Merge mechanical parts",
},
'action_selection_mode_tip': {
	'en': "How actions are selected for export",
},
'use_scene_export_tip': {
	'en': "Export this item with the scene",
},
'bone_rot_legacy_tip': {
	'en': "Remaps the Y axis of bones in this armature to Z, for backwards compatibility with old imports (SMD only)",
},
'controller_source': {
	'en': "DMX Flex Controller source",
},
'group_suppress_tip': {
	'en': "Export this group's objects individually",
},
'action_selection_current': {
	'en': "Current / NLA",
},
'shape_stereo_sharpness': {
	'en': "DMX stereo split sharpness",
},
'group_suppress': {
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
'curve_poly_side_tip': {
	'en': "Determines which side(s) of this curve will generate polygons when exported",
},
'triangulate': {
	'en': "Triangulate",
},
'group_merge_mech_tip': {
	'en': "Optimises DMX export of meshes sharing the same parent bone",
},
'action_selection_mode': {
	'en': "Action Selection",
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
	'en': "Steam Community",
},
'exportables_arm_filter_result': {
	'en': "\"{}\" actions ({})",
},
'exportables_flex_count_corrective': {
	'en': "Corrective Shapes: {}",
},
'exportables_curve_polyside': {
	'en': "Polygon Generation:",
},
'exportmenu_title': {
	'en': "Source Tools Export",
},
'exportables_flex_help': {
	'en': "Flex Controller Help",
},
'exportpanel_title': {
	'en': "Source Engine Export",
},
'exportables_flex_src': {
	'en': "Controller Source",
},
'exportmenu_invalid': {
	'en': "Cannot export selection",
},
'qc_title': {
	'en': "Source Engine QC Complies",
},
'exportables_flex_props': {
	'en': "Flex Properties",
},
'exportables_flex_generate': {
	'en': "Generate Controllers",
},
'exportables_flex_split': {
	'en': "Stereo Flex Balance:",
},
'exportables_group_mute_suffix': {
	'en': "(suppressed)",
},
'exportmenu_scene': {
	'en': "Scene export ({} files)",
},
'exportpanel_dmxver': {
	'en': "DMX Version:",
},
'exportpanel_update': {
	'en': "Check for updates",
},
'exportables_title': {
	'en': "Source Engine Exportables",
	'ru': "TEST",
},
'exportables_armature_props': {
	'en': "Armature Properties ({})",
},
'qc_bad_enginepath': {
	'en': "Invalid Engine Path",
},
'exportmenu_selected': {
	'en': "Selected objects ({} files)",
},
'exportables_group_props': {
	'en': "Group Properties",
},
'qc_no_enginepath': {
	'en': "No Engine Path provided",
},
'exportables_curve_props': {
	'en': "Curve Properties",
},
'exportables_flex_count': {
	'en': "Shapes: {}",
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
	'en': "Help",
},
'bl_info_location': {
	'en': "File > Import/Export, Scene properties",
},
'import_menuitem': {
	'en': "Source Engine (.smd, .vta, .dmx, .qc)",
},
'exporter_report_qc': {
	'en': "{0} files exported and {2} QCs compiled ({3}/{4}) in {1} seconds",
},
'exporter_err_relativeunsaved': {
	'en': "Cannot export to a relative path until the blend file has been saved.",
},
'exporter_err_nopolys': {
	'en': "Object {} has no polygons, skipping",
},
'exporter_err_arm_nonuniform': {
	'en': "Armature \"{}\" has non-uniform scale. Mesh deformation in Source will differ from Blender.",
},
'exporter_err_vtadist': {
	'en': "Shape \"{}\" has {} vertex movements that exceed eight units. Source does not support this!",
},
'exporter_err_facesnotex_ormat': {
	'en': "{} faces on {} did not have a Material or Texture assigned",
},
'exporter_err_arm_noanims': {
	'en': "Couldn't find any animation for Armature \"{}\"",
},
'exporter_err_dupeenv_arm': {
	'en': "Armature modifier \"{}\" found on \"{}\", which already has a bone parent or constraint. Ignoring.",
},
'exporter_err_bonelimit': {
	'en': "Exported {} bones, but SMD only supports {}!",
},
'exporter_err_flexctrl_loadfail': {
	'en': "Could not load flex controllers. Python reports: {}",
},
'qc_compile_err_nofiles': {
	'en': "Cannot compile, no QCs provided. The Blender Source Tools do not generate QCs.",
},
'qc_compile_complete': {
	'en': "\"Compiled {} {} QCs\"",
},
'exporter_err_shapes_decimate': {
	'en': "Cannot export shape keys from \"{}\" because it has a '{}' Decimate modifier. Only Un-Subdivide mode is supported.",
},
'exporter_err_splitvgroup_undefined': {
	'en': "Object \"{}\" uses Vertex Group stereo split, but does not define a Vertex Group to use.",
},
'exporter_err_open': {
	'en': "Could not create {} file. Python reports: {}.",
},
'qc_compile_title': {
	'en': "Compile QC",
},
'exporter_err_noexportables': {
	'en': "Found no valid objects for export",
},
'exporter_err_flexctrl_missing': {
	'en': "No flex controller defined for shape {}.",
},
'qc_compile_err_compiler': {
	'en': "Could not execute studiomdl from \"{}\"",
},
'exporter_err_facesnotex': {
	'en': "{} faces on {} did not have a Texture assigned",
},
'exporter_err_flexctrl_undefined': {
	'en': "Could not find flex controllers for \"{}\"",
},
'exporter_tip': {
	'en': "Export and compile Source Engine models",
},
'exporter_prop_scene_tip': {
	'en': "Export all items selected in the Source Engine Exportables panel",
},
'exporter_err_dmxenc': {
	'en': "DMX format \"Model {}\" requires DMX encoding \"Binary 3\" or later",
},
'exporter_prop_group': {
	'en': "Group Name",
},
'qc_compile_tip': {
	'en': "Compile QCs with the Source SDK",
},
'exporter_report_suffix': {
	'en': " with {0} Errors and {1} Warnings",
},
'exporter_err_groupempty': {
	'en': "Group {} has no active objects",
},
'exporter_err_dmxother': {
	'en': "Cannot export DMX. Resolve errors with the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
},
'exporter_prop_group_tip': {
	'en': "Name of the Group to export",
},
'exporter_err_solidifyinside': {
	'en': "Curve {} has the Solidify modifier with rim fill, but is still exporting polys on both sides.",
},
'exporter_err_dupeenv_con': {
	'en': "Bone constraint \"{}\" found on \"{}\", which already has a bone parent. Ignoring.",
},
'exporter_err_unconfigured': {
	'en': "Scene unconfigured. See the SOURCE ENGINE EXPORT panel in SCENE PROPERTIES.",
},
'exporter_err_makedirs': {
	'en': "Could not create export folder. Python reports: {}",
},
'exporter_err_weightlinks': {
	'en': "{} verts on \"{}\" have over 3 weight links. Studiomdl does not support this!",
},
'exporter_report_menu': {
	'en': "Source Tools Error Report",
},
'exporter_report': {
	'en': "{0} files exported in {1} seconds",
},
'exporter_err_groupmuted': {
	'en': "Group {} is suppressed",
},
'exporter_title': {
	'en': "Export SMD/VTA/DMX",
},
'qc_compile_err_unknown': {
	'en': "Compile of {} failed. Check the console for details",
},
'exporter_err_splitvgroup_missing': {
	'en': "Could not find stereo split Vertex Group \"{}\" on object \"{}\"",
},
'importer_complete': {
	'en': "Imported {} files in {} seconds",
},
'importer_err_nofile': {
	'en': "No file selected",
},
'importer_err_smd': {
	'en': "Could not open SMD file \"{}\": {}",
},
'importer_qc_macroskip': {
	'en': "Skipping macro in QC {}",
},
'importer_tip': {
	'en': "Imports uncompiled Source Engine model data",
},
'importer_title': {
	'en': "Import SMD/VTA, DMX, QC",
},
'importer_makecamera': {
	'en': "Make Camera At $origin",
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
'importer_rotmode': {
	'en': "Rotation mode",
},
'importer_err_qci': {
	'en': "Could not open QC $include file \"{}\" - skipping!",
},
'importer_up_tip': {
	'en': "Which axis represents 'up' (ignored for QCs)",
},
'importer_err_unmatched_mesh': {
	'en': "{} VTA vertices ({}%) were not matched to a mesh vertex! An object with a vertex group has been created to show where the VTA file's vertices are.",
},
'importer_name_nomat': {
	'en': "UndefinedMaterial",
},
'importer_append_tip': {
	'en': "Whether imports will latch onto an existing armature or create their own",
},
'importer_err_refanim': {
	'en': "Found animation in reference mesh \"{}\", ignoring!",
},
'importer_err_badweights': {
	'en': "{} vertices weighted to invalid bones on {}",
},
'importer_err_bonelimit_smd': {
	'en': "Source only supports 128 bones!",
},
'importer_err_badfile': {
	'en': "Format of {} not recognised",
},
'importer_err_smd_ver': {
	'en': "Unrecognised/invalid SMD file. Import will proceed, but may fail!",
},
'importer_err_cleancurves': {
	'en': "Unable to clean keyframe handles, animations might be jittery.",
},
'importer_append': {
	'en': "Append To Existing Model",
},
'importer_doanims': {
	'en': "Import Animations",
},
'importer_err_missingbones': {
	'en': "{} contains {} bones not present in {}: {}",
},
'importer_name_unmatchedvta': {
	'en': "Unmatched VTA",
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
	'en': "DMX written to text block \"{}\"",
},
'gen_block': {
	'en': "Generate DMX Flex Controller block",
},
'insert_uuid': {
	'en': "Insert UUID",
},
'launch_hlmv_tip': {
	'en': "Launches Half-Life Model Viewer",
},
'activate_dep_shapes_tip': {
	'en': "Activates shapes found in the name of the current shape (underscore delimited)",
},
'activate_dep_shapes_success': {
	'en': "Activated {} dependency shapes",
},
'launch_hlmv': {
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
	'en': "Generate Corrective Shape Key Drivers",
},
'gen_drivers_tip': {
	'en': "Adds Blender animation drivers to corrective Source engine shapes",
},
'engine_path': {
	'en': "Engine Path",
},
'game_path_tip': {
	'en': "Directory containing gameinfo.txt (if unset, the system VPROJECT will be used)",
},
'visible_only': {
	'en': "Visible layers only",
},
'dmx_encoding': {
	'en': "DMX encoding",
},
'game_path': {
	'en': "Game Path",
},
'up_axis': {
	'en': "Target Up Axis",
},
'dmx_format': {
	'en': "DMX format",
},
'ignore_materials': {
	'en': "Ignore Blender Materials",
},
'visible_only_tip': {
	'en': "Ignore objects in hidden layers",
},
'active_exportable': {
	'en': "Active exportable",
},
'exportroot_tip': {
	'en': "The root folder into which SMD and DMX exports from this scene are written",
},
'qc_compilenow': {
	'en': "Compile All Now",
},
'up_axis_tip': {
	'en': "Use for compatibility with data from other 3D tools",
},
'dmx_mat_path_tip': {
	'en': "Folder relative to game root containing VMTs referenced in this scene (DMX only)",
},
'qc_compileall_tip': {
	'en': "Compile all QC files whenever anything is exported",
},
'qc_nogamepath': {
	'en': "No Game Path and invalid VPROJECT",
},
'dmx_mat_path': {
	'en': "Material Path",
},
'exportroot': {
	'en': "Export Path",
},
'export_format': {
	'en': "Export Format",
},
'qc_compileall': {
	'en': "Compile all on export",
},
'dmx_encoding_tip': {
	'en': "Manual override for binary DMX encoding version",
},
'dmx_format_tip': {
	'en': "Manual override for DMX model format version",
},
'engine_path_tip': {
	'en': "Directory containing studiomdl",
},
'ignore_materials_tip': {
	'en': "Only export face-assigned image filenames",
},
'updater_title': {
	'en': "Check for Source Tools updates",
},
'update_err_downloadfailed': {
	'en': "Could not complete download:",
},
'offerchangelog_offer': {
	'en': "View changelog?",
},
'update_err_outdated': {
	'en': "The latest Source Tools require Blender {}. Please upgrade.",
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
	'en': "Upgraded to Source Tools {}!",
},
'updater_title_tip': {
	'en': "Connects to http://steamreview.org/BlenderSourceTools/latest.php",
},
'update_alreadylatest': {
	'en': "The latest Source Tools ({}) are already installed.",
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
