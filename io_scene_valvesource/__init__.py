#  Copyright (c) 2014 Tom Edwards contact@steamreview.org
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "(fixed) Blender Source Tools SMD",
	"author": "Tom Edwards (translators: Grigory Revzin)",
	"version": (3, 3, 1),
	"blender": (4, 1, 0),
	"category": "Import-Export",
	"location": "File > Import/Export, Scene properties",
	"wiki_url": "http://steamcommunity.com/groups/BlenderSourceTools",
	"tracker_url": "http://steamcommunity.com/groups/BlenderSourceTools/discussions/0/",
	"description": "Importer and exporter for Valve Software's Source Engine. Supports SMD\VTA, DMX and QC. New Fixes BLENDER 4.2. + BST 3 3 1 (w_model)"
}

import bpy, os, re
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty, PointerProperty

# Python doesn't reload package sub-modules at the same time as __init__.py!
import importlib, sys
for filename in [ f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
	if filename == os.path.basename(__file__): continue
	module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
	if module: importlib.reload(module)

# clear out any scene update funcs hanging around, e.g. after a script reload
for collection in [bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.load_post]:
	for func in collection:
		if func.__module__.startswith(__name__):
			collection.remove(func)



from . import datamodel, import_smd, export_smd, flex, GUI, update
from .utils import *

class ValveSource_Exportable(bpy.types.PropertyGroup):
	ob_type : StringProperty()
	icon : StringProperty()
	obj : PointerProperty(type=bpy.types.Object)
	collection : PointerProperty(type=bpy.types.Collection)

	@property
	def item(self): return self.obj or self.collection

	@property
	def session_uid(self): return self.item.session_uid

def menu_func_import(self, context):
	self.layout.operator(import_smd.SmdImporter.bl_idname, text=get_id("import_menuitem", True))

def menu_func_export(self, context):
	self.layout.menu("SMD_MT_ExportChoice", text=get_id("export_menuitem"))

def menu_func_shapekeys(self,context):
	self.layout.operator(flex.ActiveDependencyShapes.bl_idname, text=get_id("activate_dependency_shapes",True), icon='SHAPEKEY_DATA')

def menu_func_textedit(self,context):
	self.layout.operator(flex.InsertUUID.bl_idname)

def export_active_changed(self, context):
	if not context.scene.vs.export_list_active < len(context.scene.vs.export_list):
		context.scene.vs.export_list_active = len(context.scene.vs.export_list) - 1
		return

	item = get_active_exportable(context).item
	
	if type(item) == bpy.types.Collection and item.vs.mute: return
	for ob in context.scene.objects: ob.select_set(False)
	
	if type(item) == bpy.types.Collection:
		context.view_layer.objects.active = item.objects[0]
		for ob in item.objects: ob.select_set(True)
	else:
		item.select_set(True)
		context.view_layer.objects.active = item
#
# Property Groups
#
from bpy.types import PropertyGroup

encodings = []
for enc in datamodel.list_support()['binary']: encodings.append( (str(enc), f"Binary {enc}", '' ) )
formats = []
for version in set(x for x in [*dmx_versions_source1.values(), *dmx_versions_source2.values()] if x.format != 0):
	formats.append((version.format_enum, version.format_title, ''))
formats.sort(key = lambda f: f[0])

class ValveSource_SceneProps(PropertyGroup):
	export_path : StringProperty(name=get_id("exportroot"),description=get_id("exportroot_tip"), subtype='DIR_PATH')
	qc_compile : BoolProperty(name=get_id("qc_compileall"),description=get_id("qc_compileall_tip"),default=False)
	qc_path : StringProperty(name=get_id("qc_path"),description=get_id("qc_path_tip"),default="//*.qc",subtype="FILE_PATH")
	engine_path : StringProperty(name=get_id("engine_path"),description=get_id("engine_path_tip"), subtype='DIR_PATH',update=State.onEnginePathChanged)
	
	dmx_encoding : EnumProperty(name=get_id("dmx_encoding"),description=get_id("dmx_encoding_tip"),items=tuple(encodings),default='2')
	dmx_format : EnumProperty(name=get_id("dmx_format"),description=get_id("dmx_format_tip"),items=tuple(formats),default='1')
	
	export_format : EnumProperty(name=get_id("export_format"),items=( ('SMD', "SMD", "Studiomdl Data" ), ('DMX', "DMX", "Datamodel Exchange" ) ),default='SMD')
	up_axis : EnumProperty(name=get_id("up_axis"),items=axes,default='Z',description=get_id("up_axis_tip"))
	material_path : StringProperty(name=get_id("dmx_mat_path"),description=get_id("dmx_mat_path_tip"))
	export_list_active : IntProperty(name=get_id("active_exportable"),default=0,min=0,update=export_active_changed)
	export_list : CollectionProperty(type=ValveSource_Exportable,options={'SKIP_SAVE','HIDDEN'})
	use_kv2 : BoolProperty(name="Write KeyValues2",description="Write ASCII DMX files",default=False)
	game_path : StringProperty(name=get_id("game_path"),description=get_id("game_path_tip"),subtype='DIR_PATH',update=State.onGamePathChanged)
	dmx_weightlink_threshold : FloatProperty(name=get_id("dmx_weightlinkcull"),description=get_id("dmx_weightlinkcull_tip"),max=1,min=0)
	smd_format : EnumProperty(name=get_id("smd_format"), items=(('SOURCE', "Source", "Source Engine (Half-Life 2)") , ("GOLDSOURCE", "GoldSrc", "GoldSrc engine (Half-Life 1)")), default="GOLDSOURCE")

class ValveSource_VertexAnimation(PropertyGroup):
	name : StringProperty(name="Name",default="VertexAnim")
	start : IntProperty(name="Start",description=get_id("vca_start_tip"),default=0)
	end : IntProperty(name="End",description=get_id("vca_end_tip"),default=250)
	export_sequence : BoolProperty(name=get_id("vca_sequence"),description=get_id("vca_sequence_tip"),default=True)

class ExportableProps():
	flex_controller_modes = (
		('SIMPLE',"Simple",get_id("controllers_simple_tip")),
		('ADVANCED',"Advanced",get_id("controllers_advanced_tip"))
	)

	export : BoolProperty(name=get_id("scene_export"),description=get_id("use_scene_export_tip"),default=True)
	subdir : StringProperty(name=get_id("subdir"),description=get_id("subdir_tip"))
	flex_controller_mode : EnumProperty(name=get_id("controllers_mode"),description=get_id("controllers_mode_tip"),items=flex_controller_modes,default='SIMPLE')
	flex_controller_source : StringProperty(name=get_id("controller_source"),description=get_id("controllers_source_tip"),subtype='FILE_PATH')

	vertex_animations : CollectionProperty(name=get_id("vca_group_props"),type=ValveSource_VertexAnimation)
	active_vertex_animation : IntProperty(default=-1)

class ValveSource_ObjectProps(ExportableProps,PropertyGroup):
	action_filter : StringProperty(name=get_id("action_filter"),description=get_id("action_filter_tip"))
	triangulate : BoolProperty(name=get_id("triangulate"),description=get_id("triangulate_tip"),default=False)

class ValveSource_ArmatureProps(PropertyGroup):
	implicit_zero_bone : BoolProperty(name=get_id("dummy_bone"),default=True,description=get_id("dummy_bone_tip"))
	arm_modes = (
		('CURRENT',get_id("action_selection_current"),get_id("action_selection_current_tip")),
		('FILTERED',get_id("action_filter"),get_id("action_selection_filter_tip"))
	)
	action_selection : EnumProperty(name=get_id("action_selection_mode"), items=arm_modes,description=get_id("action_selection_mode_tip"),default='CURRENT')
	legacy_rotation : BoolProperty(name=get_id("bone_rot_legacy"),description=get_id("bone_rot_legacy_tip"),default=False)

class ValveSource_CollectionProps(ExportableProps,PropertyGroup):
	mute : BoolProperty(name=get_id("group_suppress"),description=get_id("group_suppress_tip"),default=False)
	selected_item : IntProperty(default=-1, max=-1, min=-1)
	automerge : BoolProperty(name=get_id("group_merge_mech"),description=get_id("group_merge_mech_tip"),default=False)

class ShapeTypeProps():
	flex_stereo_sharpness : FloatProperty(name=get_id("shape_stereo_sharpness"),description=get_id("shape_stereo_sharpness_tip"),default=90,min=0,max=100,subtype='PERCENTAGE')
	flex_stereo_mode : EnumProperty(name=get_id("shape_stereo_mode"),description=get_id("shape_stereo_mode_tip"),
								 items=tuple(list(axes) + [('VGROUP','Vertex Group',get_id("shape_stereo_mode_vgroup"))]), default='X')
	flex_stereo_vg : StringProperty(name=get_id("shape_stereo_vgroup"),description=get_id("shape_stereo_vgroup_tip"))

class CurveTypeProps():
	faces : EnumProperty(name=get_id("curve_poly_side"),description=get_id("curve_poly_side_tip"),default='FORWARD',items=(
	('FORWARD', get_id("curve_poly_side_fwd"), ''),
	('BACKWARD', get_id("curve_poly_side_back"), ''),
	('BOTH', get_id("curve_poly_side_both"), '')) )

class ValveSource_MeshProps(ShapeTypeProps,PropertyGroup):
	pass
class ValveSource_SurfaceProps(ShapeTypeProps,CurveTypeProps,PropertyGroup):
	pass
class ValveSource_CurveProps(ShapeTypeProps,CurveTypeProps,PropertyGroup):
	pass
class ValveSource_TextProps(CurveTypeProps,PropertyGroup):
	pass


import os
import subprocess
import re
import shutil
import bpy
import sys

#################################### BUTTONS 
class Create_SMD_Utils_Panel(bpy.types.Panel):
    bl_label = "SMD Import/Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SMD"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # layout.separator()
        # layout.label(text="SUB_Model Setup:")
        layout.operator("import_scene.smd", text="Import SMD")
        layout.operator("export_scene.smd", text="Export SMD")
        layout.operator("open.qc_file_with_studiomodel", text="Compile")
        layout.operator("smd.open_model", text="Open Model")
  
        layout.label(text="Tools:")
        layout.operator("open.smd_file_with_splitter", text="Split SMD")
        layout.operator("rename.mesh_based_on_smd", text="Rename mesh to unic")
        layout.operator("object.create_one_bone_and_assign_obj", text="new Skeleton")
        layout.operator("export.create_idle_smd", text="sequence_idle.smd")
        layout.operator("export.create_qc_file", text="new_w_model.qc")
        layout.separator()
        layout.operator("export.submodels_qc", text="new_w_models.qc")
        layout.operator("mdl.process_files", text="Pack all models to one")
        # layout.operator("texture.create_256_color_texture", text="Save 256 Pallete")

    
        # Проверяем, задана ли рабочая папка
        export_path = scene.vs.export_path
        is_export_path_set = export_path and os.path.isdir(export_path)

        # Если рабочая папка не задана, показываем поле для её указания
        if not is_export_path_set:
            layout.prop(scene.vs, "export_path", text="")


        # Счётчик полигонов
        active_obj = context.active_object
        if active_obj and active_obj.type == 'MESH':
            mesh = active_obj.data
            num_triangles = sum(len(polygon.vertices) - 2 for polygon in mesh.polygons)
            layout.label(text=f"Triangles: {num_triangles}")
        else:
            layout.label(text="Select a mesh to see triangle count")

        # Группа "Main" шпаргалка для боксов HUD
        #box = layout.box()
        #box.label(text="Main:")
        #col = box.column()
        #col.operator("import_scene.smd", text="Import SMD")



# Глобальный массив для хранения имен моделей
g_model_references = []

class MDL_PROCESSOR_OT_Process(bpy.types.Operator):
    bl_idname = "mdl.process_files"
    bl_label = "Pack all models to one"
    bl_description = "Process all .mdl files in the working directory and combine them into a single model"

    @classmethod
    def poll(cls, context):
        # Кнопка активна только если указан рабочий каталог
        return context.scene.vs.export_path and os.path.isdir(context.scene.vs.export_path)

    def execute(self, context):
        # Получаем рабочую папку из настроек сцены
        directory = bpy.path.abspath(context.scene.vs.export_path)
        if not os.path.isdir(directory):
            self.report({'ERROR'}, "Directory does not exist!")
            return {'CANCELLED'}

        try:
            # Получаем список всех .mdl файлов
            mdl_files = [f for f in os.listdir(directory) if f.endswith('.mdl')]
            if not mdl_files:
                self.report({'ERROR'}, "No .mdl files found in the directory!")
                return {'CANCELLED'}

            # Обрабатываем каждый файл по очереди
            for mdl_file in mdl_files:
                self.report({'INFO'}, f"Processing file: {mdl_file}")
                success = self.process_single_mdl(directory, mdl_file)
                if not success:
                    self.report({'ERROR'}, f"Failed to process {mdl_file}")
                    return {'CANCELLED'}

            # Выводим количество обработанных моделей в консоль
            self.report({'INFO'}, f"Total models processed: {len(g_model_references)}")
            print(f"Total models processed: {len(g_model_references)}")

            # Создаем текстовый файл с именами моделей
            self.create_model_list_file(directory)

            # Создаем QC файл
            self.create_qc_file(directory)

            # Создаем файл sequence_idle.smd
            self.create_sequence_idle_smd(directory)

            # Открываем QC файл с помощью !studiomdl.exe
            self.compile_qc_file(directory)

            self.report({'INFO'}, "All files processed and compilation started successfully!")
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def process_single_mdl(self, directory, mdl_file):
        """Обрабатывает один .mdl файл: декомпиляция, сортировка, подготовка."""
        mdl_path = os.path.join(directory, mdl_file)

        # Проверка наличия декомпилятора
        mdldec_exe = os.path.join(directory, "!mdldec.exe")
        if not os.path.exists(mdldec_exe):
            self.report({'ERROR'}, f"File {mdldec_exe} not found!")
            return False

        # Декомпиляция
        try:
            result = subprocess.run(
                [mdldec_exe, mdl_path],
                check=True,
                capture_output=True,
                text=True
            )
            if "ERROR" in result.stdout:
                self.report({'ERROR'}, f"Decompilation failed: {result.stdout}")
                return False
            self.report({'INFO'}, f"Successfully decompiled: {mdl_file}")
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Error during decompilation: {e}")
            return False

        # Обработка декомпилированных файлов
        qc_file = mdl_file.replace('.mdl', '.qc')
        qc_path = os.path.join(directory, qc_file)

        if os.path.exists(qc_path):
            # Чтение QC файла для поиска референса
            reference = self.find_reference_in_qc(qc_path)
            if reference:
                ref_smd = f"{reference}.smd"
                new_smd = f"{mdl_file.replace('.mdl', '')}.smd"
                if os.path.exists(os.path.join(directory, ref_smd)):
                    os.rename(os.path.join(directory, ref_smd), os.path.join(directory, new_smd))
                    self.report({'INFO'}, f"Renamed {ref_smd} to {new_smd}")

                    # Добавляем имя модели в массив БЕЗ расширения .smd
                    model_name_without_extension = os.path.splitext(new_smd)[0]
                    g_model_references.append(model_name_without_extension)

                # Удаление анимаций
                with open(qc_path, 'r') as file:
                    content = file.read()
                    animations = re.findall(r'\$sequence\s+"[^"]+"\s+"([^"]+)"', content)
                    for anim in animations:
                        anim_file = f"{anim}.smd"
                        if os.path.exists(os.path.join(directory, anim_file)):
                            os.remove(os.path.join(directory, anim_file))
                            self.report({'INFO'}, f"Deleted animation file: {anim_file}")

                # Удаление QC файла
                os.remove(qc_path)
                self.report({'INFO'}, f"Deleted QC file: {qc_file}")

        # Перемещение обработанного .mdl файла
        processed_dir = os.path.join(directory, "Obrabotano")
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
        shutil.move(mdl_path, os.path.join(processed_dir, mdl_file))
        self.report({'INFO'}, f"Moved {mdl_file} to {processed_dir}")

        return True

    def find_reference_in_qc(self, qc_file):
        """Ищет референс в QC файле."""
        with open(qc_file, 'r') as file:
            content = file.read()
            match = re.search(r'\$body\s+"studio"\s+"([^"]+)"', content)
            if match:
                return match.group(1)
        return None

    def create_model_list_file(self, directory):
        """Создает текстовый файл с именами моделей."""
        model_list_path = os.path.join(directory, "model_list.txt")
        with open(model_list_path, 'w') as file:
            for model_name in g_model_references:
                file.write(f"{model_name}\n")
        self.report({'INFO'}, f"Model list created at {model_list_path}")

    def create_qc_file(self, directory):
        """Создает QC файл с именами моделей в блоке $bodygroup."""
        qc_file_path = os.path.join(directory, "!w_new_models.qc")
        with open(qc_file_path, 'w') as file:
            file.write("/*\n")
            file.write("this QC generated by DeathDemonSaxofonovich\n")
            file.write("*/\n\n")
            file.write('$modelname "new_w_models.mdl"\n')
            file.write('$cd ".\\"\n')
            file.write('$cdtexture ".\\"\n')
            file.write('$scale 1.0\n')
            file.write('$cliptotextures\n\n')
            file.write('$bbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000\n')
            file.write('$cbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000\n\n')
            file.write('$eyeposition 0.000000 0.000000 0.000000\n\n')
            file.write('$bodygroup body\n')
            file.write('{\n')
            file.write('    blank\n')
            for model_name in g_model_references:
                # Имена моделей уже без расширения .smd
                file.write(f'    studio "{model_name}"\n')
            file.write('}\n\n')
            file.write('$sequence "idle" "sequence_idle" loop fps 0 ACT_IDLE 1\n')
            file.write('/// КОНЕЦ QC файла\n')
        self.report({'INFO'}, f"QC file created at {qc_file_path}")

    def create_sequence_idle_smd(self, directory):
        """Создает файл sequence_idle.smd с указанным содержимым."""
        smd_file_path = os.path.join(directory, "sequence_idle.smd")
        smd_content = '''version 1
nodes
0 "blender_implicit" -1
end
skeleton
time 0
0 0.000000 0.000000 0.000000 0.000000 -0.000000 0.000000
end
'''
        with open(smd_file_path, 'w') as file:
            file.write(smd_content)
        self.report({'INFO'}, f"Created sequence_idle.smd at {smd_file_path}")

    def compile_qc_file(self, directory):
        """Открывает QC файл с помощью !studiomdl.exe для компиляции."""
        qc_file_path = os.path.join(directory, "!w_new_models.qc")
        studiomodel_exe = os.path.join(directory, "!studiomdl.exe")

        if not os.path.exists(studiomodel_exe):
            self.report({'ERROR'}, f"File {studiomodel_exe} not found!")
            return False

        if not os.path.exists(qc_file_path):
            self.report({'ERROR'}, f"QC file {qc_file_path} not found!")
            return False

        try:
            # Кодируем путь к исполняемому файлу
            edir = studiomodel_exe.encode(sys.getfilesystemencoding())

            # Функция для получения директории файла
            def filedir(some_array):
                return os.path.dirname(some_array)

            # Запуск процесса
            cmd_process = subprocess.Popen(
                [edir, qc_file_path],
                cwd=filedir(qc_file_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # Чтение вывода процесса
            while True:
                output = cmd_process.stdout.readline()
                if output == b'' and cmd_process.poll() is not None:
                    break
                if output:
                    print(output.strip().decode())  # Вывод в консоль Blender
                    self.report({'INFO'}, output.strip().decode())  # Вывод в UI Blender

            # Проверка завершения процесса
            if cmd_process.returncode != 0:
                self.report({'ERROR'}, f"Compilation failed with return code {cmd_process.returncode}")
                return {'CANCELLED'}

            self.report({'INFO'}, f"Successfully compiled {qc_file_path} with {os.path.basename(studiomodel_exe)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to compile QC file: {str(e)}")
            return {'CANCELLED'}

        return True

# Добавляем кнопку в панель Blender Source Tools



class SMD_OT_SetExportPath(bpy.types.Operator):
    bl_idname = "smd.set_export_path"
    bl_label = "Set Export Path"
    bl_description = "Set the current export path as the working directory"

    def execute(self, context):
        export_path = context.scene.vs.export_path

        # Проверяем, что путь существует
        if not export_path or not os.path.isdir(export_path):
            self.report({'ERROR'}, "Invalid directory path!")
            return {'CANCELLED'}

        # Сохраняем путь в настройках сцены
        context.scene.vs.export_path = export_path
        self.report({'INFO'}, f"Work directory set to: {export_path}")
        return {'FINISHED'}



#### Iсоздаём кнопку:: Finish


import bpy
import os
import subprocess
import sys

class OpenSMDFileWithSplitter(bpy.types.Operator):
    bl_idname = "open.smd_file_with_splitter"
    bl_label = "Open SMD File with Splitter"
    bl_description = "Open the SMD file corresponding to the selected mesh using smd_splitter.exe"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        # Получаем активный объект
        active_obj = context.active_object

        # Проверяем, что активный объект — это меш
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Получаем имя активного меша
        mesh_name = active_obj.name
        print(f"Active mesh name: {mesh_name}")

        # Получаем путь к рабочей папке
        working_directory = bpy.context.scene.vs.export_path
        if not working_directory or not os.path.isdir(working_directory):
            working_directory = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
        print(f"Working directory: {working_directory}")

        # Ищем SMD файл с именем, соответствующим имени меша
        SMD_file = f"{mesh_name}.smd"
        SMD_file_path = os.path.join(working_directory, SMD_file)

        if not os.path.exists(SMD_file_path):
            self.report({'ERROR'}, f"No SMD file found for mesh '{mesh_name}'")
            return {'CANCELLED'}

        print(f"Found SMD file: {SMD_file_path}")

        # Ищем программу smd_splitter.exe в рабочей папке
        splitter_files = [f for f in os.listdir(working_directory) if f.lower() == "!smd-splitter.exe"]
        if not splitter_files:
            self.report({'ERROR'}, "No smd_splitter.exe found in the working directory")
            return {'CANCELLED'}

        splitter_file = splitter_files[0]
        splitter_file_path = os.path.join(working_directory, splitter_file)
        print(f"Found smd_splitter.exe: {splitter_file_path}")

        # Запуск smd_splitter.exe для обработки SMD файла без ожидания завершения
        try:
            subprocess.Popen(
                [splitter_file_path, SMD_file_path],
                cwd=working_directory,
                shell=True,
                stdout=subprocess.DEVNULL,  # Игнорируем вывод
                stderr=subprocess.DEVNULL   # Игнорируем ошибки
            )
            self.report({'INFO'}, f"Started processing {SMD_file} with {os.path.basename(splitter_file_path)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start smd_splitter.exe: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

#import bpy
#import os
#import numpy as np  # Добавьте эту строку
#from PIL import Image  # Библиотека Pillow для работы с изображениями


class Create256ColorTextureAndMaterial(bpy.types.Operator):
    bl_idname = "texture.create_256_color_texture"
    bl_label = "Create 256 Color Texture"
    bl_description = "Create a 16x16 texture with 256 colors, save it, and assign it to the selected mesh"

    # Добавляем свойство для хранения пути
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Получаем активный объект
        active_obj = context.active_object

        # Проверяем, что активный объект — это меш
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Создаём изображение 16x16
        image_name = "palette_256_colors"
        image = bpy.data.images.new(image_name, width=16, height=16)

        # Заполняем изображение 256 цветами (градиент)
        pixels = np.zeros((16, 16, 4), dtype=np.float32)  # RGBA
        for i in range(256):
            x = i % 16
            y = i // 16
            r = (i & 0xE0) / 255.0  # Красный канал
            g = ((i & 0x1C) << 3) / 255.0  # Зелёный канал
            b = ((i & 0x03) << 6) / 255.0  # Синий канал
            pixels[y, x] = (r, g, b, 1.0)  # Альфа = 1.0

        # Записываем пиксели в изображение
        image.pixels = pixels.flatten()

        # Сохраняем изображение в формате BMP с использованием Pillow
        export_path = os.path.dirname(self.filepath)  # Получаем путь из свойства filepath
        if not export_path:
            self.report({'ERROR'}, "Export path is not set")
            return {'CANCELLED'}

        # Преобразуем изображение в 8-bit с использованием Pillow
        pil_image = Image.new("P", (16, 16))  # Создаём 8-bit изображение

        # Создаём палитру из 256 цветов
        palette = []
        for i in range(256):
            r, g, b, _ = pixels[i // 16, i % 16]
            palette.extend([int(r * 255), int(g * 255), int(b * 255)])
        pil_image.putpalette(palette)

        # Заполняем изображение индексами палитры
        pil_image.putdata([i for i in range(256)])

        # Сохраняем изображение в формате BMP
        texture_path = os.path.join(export_path, f"{image_name}.bmp")
        pil_image.save(texture_path, format="BMP")

        # Создаём материал
        material_name = f"{image_name}.bmp"
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True

        # Очищаем ноды материала
        nodes = material.node_tree.nodes
        nodes.clear()

        # Добавляем ноду для текстуры
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = image
        texture_node.location = (0, 0)

        # Добавляем ноду для вывода
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)

        # Соединяем ноды
        links = material.node_tree.links
        links.new(texture_node.outputs['Color'], output_node.inputs['Surface'])

        # Назначаем материал активному объекту
        if active_obj.data.materials:
            active_obj.data.materials[0] = material
        else:
            active_obj.data.materials.append(material)

        self.report({'INFO'}, f"Created texture and material '{material_name}' and assigned to the mesh")
        return {'FINISHED'}

    # Добавляем метод invoke для выбора пути
    def invoke(self, context, event):
        # Устанавливаем путь по умолчанию
        self.filepath = os.path.join(bpy.path.abspath("//"), "palette_256_colors.bmp")
        # Открываем окно выбора файла
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#### Создаём кастомный экспорт OBJ:: Finish
class EXPORT_OT_ObjCustom(bpy.types.Operator):
    bl_idname = "export_scene.obj_custom"
    bl_label = "Export OBJ (Custom)"
    bl_description = "Export the scene to OBJ with custom settings"

    # Добавляем свойство для хранения пути экспорта
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Устанавливаем параметры экспорта
        bpy.ops.export_scene.obj(
            filepath=self.filepath,  # Используем путь, выбранный пользователем
            use_selection=True,      # Экспортировать только выбранные объекты
            global_scale=1.0,        # Масштаб
            axis_forward='-Z',       # Ось вперед
            axis_up='Y'             # Ось вверх
        )
        return {'FINISHED'}

    def invoke(self, context, event):
        # Открываем окно файлового браузера для выбора пути экспорта
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
#### Создаём кастомный экспорт OBJ:: Finish
		
#### W_model 

class Create_w_model_Bone_1(bpy.types.Operator):
    bl_idname = "object.create_one_bone_and_assign_obj"
    bl_label = "Create W_model"
    bl_description = "Create a single-bone armature and assign the active mesh to it"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        # Получаем активный объект
        active_obj = context.active_object

        # Проверяем, что активный объект — это меш
        if not active_obj or active_obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Создаем новую арматуру
        bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=active_obj.location)
        armature_obj = context.active_object
        armature_obj.name = "Armature_W_model"

        # Переходим в режим редактирования арматуры
        bpy.ops.object.mode_set(mode='EDIT')

        # Удаляем все кости, кроме одной оставляем 2 кости blender_implict и Bone_W_model
        #bones = armature_obj.data.edit_bones
        #for bone in bones:
        #    if bone.name != "Bone":
        #        bones.remove(bone)
		# Удаляем все кости, кроме одной blender_implict
        bones = armature_obj.data.edit_bones
        for bone in bones:
            if bone.name == "Bone":
            	bones.remove(bone)

        # Переименовываем оставшуюся кость
        #bone = bones[0]
        #bone.name = "Bone_W_model"

        # Выходим из режима редактирования
        bpy.ops.object.mode_set(mode='OBJECT')

        # Привязываем меш к арматуре
        modifier = active_obj.modifiers.new(name="Armature", type='ARMATURE')
        modifier.object = armature_obj

        # Устанавливаем арматуру как родителя меша
        bpy.ops.object.select_all(action='DESELECT')
        active_obj.select_set(True)
        armature_obj.select_set(True)
        context.view_layer.objects.active = armature_obj
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        self.report({'INFO'}, "Armature created and mesh assigned successfully")
        return {'FINISHED'}

class Create_w_model_Sequence_Idle_1(bpy.types.Operator):
    bl_idname = "export.create_idle_smd"
    bl_label = "Write Collection Idle SMD"
    bl_description = "Create a collection_idle.smd file with the specified content"

    # Свойство для хранения пути сохранения
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        # Кнопка активна только если указан рабочий каталог
        return context.scene.vs.export_path and os.path.isdir(context.scene.vs.export_path)

    def execute(self, context):
        # Содержимое файла collection_idle.smd
        content = """version 1
nodes
0 "blender_implicit" -1
end
skeleton
time 0
0 0.000000 0.000000 0.000000 0.000000 -0.000000 0.000000
end
"""

        # Записываем содержимое в файл
        try:
            with open(self.filepath, 'w') as file:
                file.write(content)
            self.report({'INFO'}, f"File saved: {self.filepath}")

            # Обновляем путь экспорта в настройках сцены
            export_dir = os.path.dirname(self.filepath)
            bpy.context.scene.vs.export_path = export_dir
            self.report({'INFO'}, f"Export path updated to: {export_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save file: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        # Получаем путь экспорта из настроек сцены
        export_path = bpy.context.scene.vs.export_path

        # Если путь экспорта указан, используем его
        if export_path and os.path.isdir(export_path):
            self.filepath = os.path.join(export_path, "sequence_idle.smd")
            return self.execute(context)
        else:
            # Если путь не указан, открываем окно файлового браузера
            self.filepath = "sequence_idle.smd"  # Имя файла по умолчанию
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}



### Имя файла mdl по имени reference
### Имя файла QC по имени reference 
class Create_w_model_QC(bpy.types.Operator):
    bl_idname = "export.create_qc_file"
    bl_label = "Create and Write QC file"
    bl_description = "Create a QC file with the name of the active object or collection"

    # Свойство для хранения пути сохранения
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        # Получаем активный объект или коллекцию
        active_object = context.view_layer.objects.active
        active_collection = context.view_layer.active_layer_collection.collection

        # Определяем имя референса
        if active_object:
            reference_name = active_object.name
        elif active_collection:
            reference_name = active_collection.name
        else:
            self.report({'ERROR'}, "No active object or collection found!")
            return {'CANCELLED'}

        # Содержимое файла QC
        content = f"""/*
this QC generated by DeathDemonSaxofonovich in Blender
*/

$modelname "new_w_model.mdl"
$cd ".\\"
$cdtexture ".\\"
$scale 1.0
$cliptotextures

$bbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000
$cbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000

$eyeposition 0.000000 0.000000 0.000000

$bodygroup body
{{
studio "{reference_name}"
}}

$sequence "idle" "sequence_idle" loop fps 0 ACT_IDLE 1
"""

        # Записываем содержимое в файл
        try:
            with open(self.filepath, 'w') as file:
                file.write(content)
            self.report({'INFO'}, f"File saved: {self.filepath}")

            # Обновляем путь экспорта в настройках сцены
            export_dir = os.path.dirname(self.filepath)
            bpy.context.scene.vs.export_path = export_dir
            self.report({'INFO'}, f"Export path updated to: {export_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save file: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        # Получаем путь экспорта из настроек сцены
        export_path = bpy.context.scene.vs.export_path

        # Определяем имя файла на основе активного объекта или коллекции
        active_object = context.view_layer.objects.active
        active_collection = context.view_layer.active_layer_collection.collection

        if active_object:
            file_name = "new_w_model.qc" ## f"{active_object.name}.qc"
        elif active_collection:
            file_name = "new_w_model.qc" ## f"{active_collection.name}.qc"
        else:
            self.report({'ERROR'}, "No active object or collection found!")
            return {'CANCELLED'}

        # Если путь экспорта указан, используем его
        if export_path and os.path.isdir(export_path):
            self.filepath = os.path.join(export_path, file_name)
            return self.execute(context)
        else:
            # Если путь не указан, открываем окно файлового браузера
            self.filepath = file_name  # Имя файла по умолчанию
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}


bpy.types.Scene.checkbox_typemode = BoolProperty(
    name="Use Automatic",
    description="Enable automatic processing",
    default=False
)


### выбрать режим экспорта. 
class Checkbox_Type(bpy.types.Operator):
    bl_idname = "checkbox.method"
    bl_label = "Choose export type"

    # Свойство для хранения пути сохранения
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if context.scene.checkbox_typemode:
            self.report({'INFO'}, "use_automatic_submodel mode enabled")
            # Ваш код для автоматической обработки
        else:
            self.report({'INFO'}, "use_automatic_submodel mode disabled")
            # Вызвать "export_scene.smd" с параметрами
        return {'FINISHED'}

    def invoke(self, context, event):
        # Открываем окно файлового браузера для выбора пути
        # context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



################### Создать QC файл для контейнера субмоделей

class Create_w_model_sub_QC(bpy.types.Operator):
    bl_idname = "export.submodels_qc"
    bl_label = "Pack submodelslist into QC"
    bl_description = "Pack submodelslist into QC"

    # Свойство для хранения пути сохранения
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        # Кнопка активна только если указан рабочий каталог
        return context.scene.vs.export_path and os.path.isdir(context.scene.vs.export_path)

    def execute(self, context):
        # Получаем путь экспорта из настроек сцены
        export_path = bpy.context.scene.vs.export_path

        # Если путь экспорта не указан, используем текущую директорию
        if not export_path or not os.path.isdir(export_path):
            export_path = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()

        # Получаем список всех файлов .smd
        smd_files = [f for f in os.listdir(export_path) if f.endswith(".smd")]

        # Разделяем файлы на две группы:
        # 1. Файлы для $bodygroup (без "idle" и "seq" в имени)
        bodygroup_files = [
            f for f in smd_files
            if "idle" not in f.lower() and "seq" not in f.lower()
        ]

        # 2. Файлы для $sequence (с "idle" или "seq" в имени)
        sequence_files = [
            f for f in smd_files
            if "idle" in f.lower() or "seq" in f.lower()
        ]

        # Если файлов не найдено, выводим сообщение об ошибке
        if not smd_files:
            self.report({'ERROR'}, "No .smd files found")
            return {'CANCELLED'}

        # Генерируем содержимое QC-файла
        qc_content = '/*\n'
        qc_content += 'this QC generated by DeathDemonSaxofonovich in Blender\n'
        qc_content += '*/\n\n'
        qc_content += '$modelname "new_w_models.mdl"\n'
        qc_content += '$cd "."\n'
        qc_content += '$cdtexture "."\n'
        qc_content += '$scale 1.0\n'
        qc_content += '$cliptotextures\n\n'
        qc_content += '$bbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000\n'
        qc_content += '$cbox 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000\n\n'
        qc_content += '$eyeposition 0.000000 0.000000 0.000000\n\n'

        # Добавляем блок $bodygroup
        qc_content += '$bodygroup "w_models"\n{\n'
        qc_content += '    blank\n'
        for smd_file in bodygroup_files:
            file_name = os.path.splitext(smd_file)[0]  # Убираем расширение .smd
            qc_content += f'    studio "{file_name}"\n'
        qc_content += '}\n\n'

        # Добавляем блок $sequence для файлов с "idle" или "seq"
        for smd_file in sequence_files:
            file_name = os.path.splitext(smd_file)[0]  # Убираем расширение .smd
            qc_content += f'$sequence Idle "{file_name}" loop fps 0 ACT_IDLE 1\n'

        # Записываем содержимое в файл
        try:
            with open(self.filepath, 'w') as file:
                file.write(qc_content)
            self.report({'INFO'}, f"QC file saved: {self.filepath}")

            # Обновляем путь экспорта в настройках сцены
            bpy.context.scene.vs.export_path = os.path.dirname(self.filepath)
            self.report({'INFO'}, f"Export path updated to: {bpy.context.scene.vs.export_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save QC file: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        # Получаем путь экспорта из настроек сцены
        export_path = bpy.context.scene.vs.export_path

        # Если путь экспорта указан, используем его
        if export_path and os.path.isdir(export_path):
            self.filepath = os.path.join(export_path, "new_w_models.qc")
            return self.execute(context)
        else:
            # Если путь не указан, открываем окно файлового браузера
            self.filepath = "new_w_models.qc"  # Имя файла по умолчанию
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

import os
import re
import bpy


class RenameMeshBasedOnSMDFiles(bpy.types.Operator):
    bl_idname = "rename.mesh_based_on_smd"
    bl_label = "Rename Mesh Based on SMD Files"
    bl_description = "Rename active mesh if an SMD file with the same name exists"

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        # Получаем путь экспорта из настроек сцены
        export_path = bpy.context.scene.vs.export_path

        # Если путь экспорта не указан, используем текущую директорию
        if not export_path or not os.path.isdir(export_path):
            export_path = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()

        print(f"Export path: {export_path}")
        
        # Получаем список всех файлов .smd
        smd_files = [f for f in os.listdir(export_path) if f.endswith(".smd")]
        print(f"All SMD files: {smd_files}")

        # Фильтруем файлы, исключая те, которые содержат "idle" или "seq"
        filtered_files = [
            f for f in smd_files
            if "idle" not in f.lower() and "seq" not in f.lower()
        ]
        print(f"Filtered SMD files: {filtered_files}")

        # Получаем активный объект (меш)
        active_object = context.view_layer.objects.active

        if not active_object or active_object.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object found")
            return {'CANCELLED'}

        # Имя активного меша
        mesh_name = active_object.name
        print(f"Active mesh name: {mesh_name}")

        # Убираем числовой суффикс из имени меша (например, "Cube.001" -> "Cube")
        base_name = re.sub(r"\.\d+$", "", mesh_name)
        print(f"Base name extracted: {base_name}")

        # Функция для проверки существования файла с указанным именем
        def is_file_exists(name):
            # Проверяем, есть ли файл с таким именем (без учёта регистра)
            exists = any(f.lower().startswith(f"{name.lower()}.") and f.lower().endswith(".smd") for f in filtered_files)
            print(f"Checking if file '{name}.smd' exists: {exists}")
            return exists

        # Если имя меша (без числового суффикса) еще не занято, оставляем его
        if not is_file_exists(base_name):
            print("Current mesh name is unique, no renaming needed.")
            self.report({'INFO'}, "Mesh name is already unique")
            return {'FINISHED'}

        # Находим следующий доступный индекс
        new_meshnum = 1
        print(f"Starting search for available suffix, starting with: {new_meshnum}")
        
        while is_file_exists(f"{base_name}.{new_meshnum:03}"):  # Пока файл с таким именем уже существует
            print(f"Name '{base_name}.{new_meshnum:03}' is taken, trying next index...")
            new_meshnum += 1  # Увеличиваем индекс

        # Формируем новое имя меша
        new_mesh_name = f"{base_name}.{new_meshnum:03}"
        print(f"New mesh name found: {new_mesh_name}")

        # Переименовываем меш, если новое имя отличается от текущего
        if new_mesh_name != mesh_name:
            active_object.name = new_mesh_name
            self.report({'INFO'}, f"Renamed mesh to: {new_mesh_name}")
        else:
            self.report({'INFO'}, "Mesh name is already unique")

        return {'FINISHED'}


        
import os
import subprocess
import bpy
import sys

class OpenQCFileWithStudioModel(bpy.types.Operator):
    bl_idname = "open.qc_file_with_studiomodel"
    bl_label = "Open QC File with StudioModel"
    bl_description = "Find a QC file in the working directory and open it with a program containing 'studiomdl' in its name"

    @classmethod
    def poll(cls, context):
        # Кнопка активна только если указан рабочий каталог
        return context.scene.vs.export_path and os.path.isdir(context.scene.vs.export_path)

    def execute(self, context):
        # Получаем путь к рабочей папке
        working_directory = bpy.context.scene.vs.export_path
        if not working_directory or not os.path.isdir(working_directory):
            working_directory = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
        print(f"Working directory: {working_directory}")

        # Ищем QC файл в рабочей папке
        qc_files = [f for f in os.listdir(working_directory) if f.endswith(".qc")]
        if not qc_files:
            self.report({'ERROR'}, "No QC files found in the working directory")
            return {'CANCELLED'}

        # Берем первый найденный QC файл (можно доработать для выбора, если их несколько)
        qc_file = qc_files[0]
        qc_file_path = os.path.join(working_directory, qc_file)
        print(f"Found QC file: {qc_file_path}")

        # Ищем программу с "studiomdl" в названии
        the_compiler_files = [f for f in os.listdir(working_directory) if f.endswith(".exe") and "studiomdl" in f.lower()]
        if not the_compiler_files:
            self.report({'ERROR'}, "No studiomdl executable found in the working directory")
            return {'CANCELLED'}

        the_compiler_file = the_compiler_files[0]
        the_compiler_file_path = os.path.join(working_directory, the_compiler_file)
        print(f"Found STUDIOMODEL Custom file: {the_compiler_file_path}")

        # Запуск компиляции с использованием вашего кода
        try:
            # Кодируем путь к исполняемому файлу
            edir = the_compiler_file_path.encode(sys.getfilesystemencoding())

            # Функция для получения директории файла
            def filedir(some_array):
                return os.path.dirname(some_array)

            # Запуск процесса
            cmd_process = subprocess.Popen(
                [edir, qc_file_path],
                cwd=filedir(qc_file_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # Чтение вывода процесса
            while True:
                output = cmd_process.stdout.readline()
                if output == b'' and cmd_process.poll() is not None:
                    break
                if output:
                    print(output.strip().decode())  # Вывод в консоль Blender
                    self.report({'INFO'}, output.strip().decode())  # Вывод в UI Blender

            # Проверка завершения процесса
            if cmd_process.returncode != 0:
                self.report({'ERROR'}, f"Compilation failed with return code {cmd_process.returncode}")
                return {'CANCELLED'}

            self.report({'INFO'}, f"Successfully compiled {qc_file} with {os.path.basename(the_compiler_file_path)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to compile QC file: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


# Добавляем новый оператор для открытия модели
class SMD_OT_OpenModel(bpy.types.Operator):
    bl_idname = "smd.open_model"
    bl_label = "Open Model"
    bl_description = "Open the compiled .mdl file in the default viewer"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        # Проверяем, что путь экспорта указан и существует
        return context.scene.vs.export_path and os.path.isdir(context.scene.vs.export_path)

    def execute(self, context):
        # Получаем путь к папке экспорта
        export_path = context.scene.vs.export_path

        # Ищем файл .mdl в папке экспорта
        mdl_files = [f for f in os.listdir(export_path) if f.endswith('.mdl')]
        if not mdl_files:
            self.report({'ERROR'}, "No .mdl files found in the export directory!")
            return {'CANCELLED'}

        # Берём первый найденный файл .mdl
        mdl_file = os.path.join(export_path, mdl_files[0])

        # Открываем файл в программе по умолчанию
        try:
            if os.name == 'nt':  # Windows
                os.startfile(mdl_file)
            elif os.name == 'posix':  # macOS или Linux
                subprocess.run(['open', mdl_file] if sys.platform == 'darwin' else ['xdg-open', mdl_file])
            self.report({'INFO'}, f"Opened {mdl_file}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open model: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

########################
_classes = (
	ValveSource_Exportable,
	ValveSource_SceneProps,
	ValveSource_VertexAnimation,
	ValveSource_ObjectProps,
	ValveSource_ArmatureProps,
	ValveSource_CollectionProps,
	ValveSource_MeshProps,
	ValveSource_SurfaceProps,
	ValveSource_CurveProps,
	ValveSource_TextProps,
	GUI.SMD_MT_ExportChoice,
	GUI.SMD_PT_Scene,
	GUI.SMD_MT_ConfigureScene,
	GUI.SMD_UL_ExportItems,
	GUI.SMD_UL_GroupItems,
	GUI.SMD_UL_VertexAnimationItem,
	GUI.SMD_OT_AddVertexAnimation,
	GUI.SMD_OT_RemoveVertexAnimation,
	GUI.SMD_OT_PreviewVertexAnimation,
	GUI.SMD_OT_GenerateVertexAnimationQCSnippet,
	GUI.SMD_OT_LaunchHLMV,
	GUI.SMD_PT_Object_Config,
	GUI.SMD_PT_Group,
	GUI.SMD_PT_VertexAnimation,
	GUI.SMD_PT_Armature,
	GUI.SMD_PT_ShapeKeys,
	GUI.SMD_PT_VertexMaps,
	GUI.SMD_PT_Curves,
	GUI.SMD_PT_Scene_QC_Complie,
	flex.DmxWriteFlexControllers,
	flex.AddCorrectiveShapeDrivers,
	flex.RenameShapesToMatchCorrectiveDrivers,
	flex.ActiveDependencyShapes,
	flex.InsertUUID,
	update.SmdToolsUpdate,
	update.SMD_MT_Updated,
	export_smd.SMD_OT_Compile, 
	export_smd.SmdExporter, 
	import_smd.SmdImporter,
    Create_SMD_Utils_Panel,
    Create_w_model_Bone_1,
    Create_w_model_Sequence_Idle_1,
    Create_w_model_QC,
    Create_w_model_sub_QC,
    Checkbox_Type,
    RenameMeshBasedOnSMDFiles,
    OpenQCFileWithStudioModel,
    SMD_OT_OpenModel,
    Create256ColorTextureAndMaterial,
    OpenSMDFileWithSplitter,
    SMD_OT_SetExportPath,
    MDL_PROCESSOR_OT_Process)

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

    from . import translations
    bpy.app.translations.register(__name__,translations.translations)
    
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.MESH_MT_shape_key_context_menu.append(menu_func_shapekeys)
    bpy.types.TEXT_MT_edit.append(menu_func_textedit)
        
    try: bpy.ops.wm.addon_disable('EXEC_SCREEN',module="io_smd_tools")
    except: pass

    def make_pointer(prop_type):
        return PointerProperty(name=get_id("settings_prop"),type=prop_type)
        
    bpy.types.Scene.vs = make_pointer(ValveSource_SceneProps)
    bpy.types.Object.vs = make_pointer(ValveSource_ObjectProps)
    bpy.types.Armature.vs = make_pointer(ValveSource_ArmatureProps)
    bpy.types.Collection.vs = make_pointer(ValveSource_CollectionProps)
    bpy.types.Mesh.vs = make_pointer(ValveSource_MeshProps)
    bpy.types.SurfaceCurve.vs = make_pointer(ValveSource_SurfaceProps)
    bpy.types.Curve.vs = make_pointer(ValveSource_CurveProps)
    bpy.types.Text.vs = make_pointer(ValveSource_TextProps)

    State.hook_events()

def unregister():
    State.unhook_events()

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.MESH_MT_shape_key_context_menu.remove(menu_func_shapekeys)
    bpy.types.TEXT_MT_edit.remove(menu_func_textedit)

    bpy.app.translations.unregister(__name__)

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vs
    del bpy.types.Object.vs
    del bpy.types.Armature.vs
    del bpy.types.Collection.vs
    del bpy.types.Mesh.vs
    del bpy.types.SurfaceCurve.vs
    del bpy.types.Curve.vs
    del bpy.types.Text.vs

if __name__ == "__main__":
    register()
