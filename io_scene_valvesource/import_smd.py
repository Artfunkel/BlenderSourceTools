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

import bpy
import bmesh
import random
import collections
from bpy import ops
from bpy.app.translations import pgettext
from bpy.props import *
from .utils import *
from .smd_reader import SMDReader
from .qc_reader import QCReader


class SmdImporter(bpy.types.Operator, QCReader, SMDReader, Logger):
    bl_idname = "import_scene.smd"
    bl_label = get_id("importer_title")
    bl_description = get_id("importer_tip")
    bl_options = {'UNDO'}

    qc = None
    smd = None

    # Properties used by the file browser
    filepath: StringProperty(
        name="File Path",
        description="File filepath used for importing the SMD/VTA/DMX/QC file",
        maxlen=1024,
        default="",
        options={'HIDDEN'})
    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN'})
    directory: StringProperty(
        maxlen=1024, default="",
        subtype='FILE_PATH',
        options={'HIDDEN'})
    filter_folder: BoolProperty(
        name="Filter Folders",
        description="",
        default=True,
        options={'HIDDEN'})
    filter_glob: StringProperty(
        default="*.smd;*.vta;*.dmx;*.qc;*.qci",
        options={'HIDDEN'})

    # Custom properties
    doAnim: BoolProperty(
        name=get_id("importer_doanims"),
        default=True)
    makeCamera: BoolProperty(
        name=get_id("importer_makecamera"),
        description=get_id("importer_makecamera_tip"),
        default=False)
    append: EnumProperty(
        name=get_id("importer_bones_mode"),
        description=get_id("importer_bones_mode_desc"),
        items=(
            (
                'VALIDATE',
                get_id("importer_bones_validate"),
                get_id("importer_bones_validate_desc")),
            (
                'APPEND',
                get_id("importer_bones_append"),
                get_id("importer_bones_append_desc")),
            (
                'NEW_ARMATURE',
                get_id("importer_bones_newarm"),
                get_id("importer_bones_newarm_desc"))),
        default='APPEND')
    upAxis: EnumProperty(
        name="Up Axis",
        items=axes,
        default='Z',
        description=get_id("importer_up_tip"))
    rotMode: EnumProperty(
        name=get_id("importer_rotmode"),
        items=(
            ('XYZ', "Euler", ''),
            ('QUATERNION', "Quaternion", "")),
        default='XYZ',
        description=get_id("importer_rotmode_tip"))
    boneMode: EnumProperty(
        name=get_id("importer_bonemode"),
        items=(
            ('NONE', 'Default', ''),
            ('ARROWS', 'Arrows', ''),
            ('SPHERE', 'Sphere', '')),
        default='SPHERE',
        description=get_id("importer_bonemode_tip"))

    def executeQC_QCI(self, filepath):
        return self.readQC(
            filepath,
            False,
            self.properties.doAnim,
            self.properties.makeCamera,
            self.properties.rotMode,
            outer_qc=True)
        bpy.context.view_layer.objects.active = self.qc.a

    def executeSMD(self, filepath):
        return self.readSMD(
            filepath,
            self.properties.upAxis,
            self.properties.rotMode)

    def executeVTA(self, filepath):
        return self.readSMD(
            filepath,
            self.properties.upAxis,
            self.properties.rotMode,
            smd_type=FLEX)

    def executeDMX(self, filepath):
        return self.readDMX(
            filepath,
            self.properties.upAxis,
            self.properties.rotMode)

    def execute(self, context):
        bpyctx = bpy.context
        bpyctx_scene = bpyctx.scene
        bpyctx_area = bpyctx.area

        pre_obs = set(bpyctx_scene.objects)
        pre_eem = context.preferences.edit.use_enter_edit_mode
        pre_append = self.append
        context.preferences.edit.use_enter_edit_mode = False

        self.existingBones = []  # bones which existed before importing began
        self.num_files_imported = 0

        for filepath in [
                os.path.join(self.directory, file.name) for file in self.files
        ] if self.files else [self.filepath]:
            filepath_lc = filepath.lower()
            file_ext = filepath_lc.split(".")[-1]
            funcSwitch = {
                'qc': self.executeQC_QCI,
                'qci': self.executeQC_QCI,
                'smd': self.executeSMD,
                'vta': self.executeVTA,
                'dmx': self.executeDMX,
            }
            if file_ext in funcSwitch.keys():
                self.num_files_imported = funcSwitch[file_ext](filepath)
            else:
                if len(filepath_lc) == 0:
                    self.report(
                        {'ERROR'}, get_id(
                            "importer_err_nofile"))
                else:
                    self.report(
                        {'ERROR'}, get_id(
                            "importer_err_badfile", True).format(
                                os.path.basename(filepath)))

            self.append = pre_append

        self.errorReport(
            get_id("importer_complete", True).format(
                self.num_files_imported,
                self.elapsed_time()))
        if self.num_files_imported:
            ops.object.select_all(action='DESELECT')
            new_obs = set(bpyctx_scene.objects).difference(pre_obs)
            xy = xyz = 0
            for ob in new_obs:
                ob.select_set(True)
                # FIXME: assumes meshes are centered around their origins
                xy = max(xy, int(max(ob.dimensions[0], ob.dimensions[1])))
                xyz = max(xyz, max(xy, int(ob.dimensions[2])))

            bpyctx.view_layer.objects.active = (
                self.qc.a
                if self.qc else self.smd.a
            )
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.spaces.active.clip_end = max(
                        area.spaces.active.clip_end,
                        xyz * 2)
        if (bpyctx_area and
            bpyctx_area.type == 'VIEW_3D' and
                bpyctx.region):
            ops.view3d.view_selected()

        context.preferences.edit.use_enter_edit_mode = pre_eem
        self.append = pre_append

        return {'FINISHED'}

    def invoke(self, context, event):
        self.properties.upAxis = context.scene.vs.up_axis
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def ensureAnimationBonesValidated(self):
        if (self.smd.jobType == ANIM and
            self.append == 'APPEND' and
            (
                hasattr(self.smd, "a") or
                self.findArmature())):
            print(
                "- Appending bones from animations is destructive; "
                "switching Bone Append Mode to \"Validate\""
            )
            self.append = 'VALIDATE'

    # Datablock names are limited to 63 bytes of UTF-8
    def truncate_id_name(self, name, id_type):
        truncated = bytes(name, 'utf8')
        if len(truncated) < 64:
            return name

        truncated = truncated[:63]
        while truncated:
            try:
                truncated = truncated.decode('utf8')
                break
            except UnicodeDecodeError:
                truncated = truncated[:-1]
        self.error(
            get_id(
                "importer_err_namelength",
                True
            ).format(
                pgettext(
                    id_type
                    if isinstance(id_type, str)
                    else id_type.__name__),
                name,
                truncated))
        return truncated

    # Identifies what type of SMD this is.
    #  Cannot tell between reference/lod/collision meshes!
    def scanSMD(self):
        smd = self.smd
        for line in smd.file:
            if line == "triangles\n":
                smd.jobType = REF
                print("- This is a mesh")
                break
            if line == "vertexanimation\n":
                print("- This is a flex animation library")
                smd.jobType = FLEX
                break

        # Finished the file

        if smd.jobType is None:
            #  No triangles, no flex - must be animation
            print("- This is a skeltal animation or pose")
            smd.jobType = ANIM
            self.ensureAnimationBonesValidated()

        smd.file.seek(0, 0)  # rewind to start of file

    # joins up "quoted values" that would otherwise
    #  be delimited, removes comments
    def parseQuoteBlockedLine(self, line, lower=True):
        if len(line) == 0:
            return ["\n"]

        qc = self.qc
        words = []
        last_word_start = 0

        # in_whitespace ? unused var
        in_quote = in_whitespace = False

        # The last char of the last line in the file was missed
        if line[-1] != "\n":
            line += "\n"

        for i in range(len(line)):
            char = line[i]
            nchar = pchar = None
            if i < len(line) - 1:
                nchar = line[i + 1]
            if i > 0:
                pchar = line[i - 1]

            # line comment - precedence over block comment
            if (char == "/" and nchar == "/") or char in ['#', ';']:
                if i > 0:
                    i = i - 1  # last word will be caught after the loop
                break  # nothing more this line

            if qc:
                # block comment
                if qc.in_block_comment:
                    # done backwards so we don't have to skip two chars
                    if char == "/" and pchar == "*":
                        qc.in_block_comment = False
                    continue
                elif char == "/" and nchar == "*":  # note: nchar, not pchar
                    qc.in_block_comment = True
                    continue

            # quote block
            if char == "\"" and not pchar == "\\":  # quotes can be escaped
                in_quote = (in_quote is False)
            if not in_quote:
                if char in [" ", "\t"]:

                    # characters between last whitespace and here
                    cur_word = line[last_word_start:i].strip("\"")
                    if len(cur_word) > 0:
                        if (lower and os.name == 'nt') or cur_word[0] == "$":
                            cur_word = cur_word.lower()
                        words.append(cur_word)

                    # we are in whitespace, first new char is the next one
                    last_word_start = i + 1

        # catch last word and any '{'s crashing into it
        needBracket = False
        cur_word = line[last_word_start:i]
        if cur_word.endswith("{"):
            needBracket = True

        cur_word = cur_word.strip("\"{")
        if len(cur_word) > 0:
            words.append(cur_word)

        if needBracket:
            words.append("{")

        if (line.endswith("\\\\\n") and
            (len(words) == 0 or
                words[-1] != "\\\\")):
            words.append("\\\\")  # macro continuation beats everything

        return words

    # Bones
    def readNodes(self):
        smd = self.smd
        boneParents = {}

        def addBone(id, name, parent):
            bone = smd.a.data.edit_bones.new(
                self.truncate_id_name(name, bpy.types.Bone))
            bone.tail = 0, 5, 0  # Blender removes zero-length bones

            smd.boneIDs[int(id)] = bone.name
            boneParents[bone.name] = int(parent)

            return bone

        if self.append != 'NEW_ARMATURE':
            smd.a = smd.a or self.findArmature()
            if smd.a:

                append = self.append == 'APPEND' and smd.jobType in [REF, ANIM]

                if append:
                    bpy.context.view_layer.objects.active = smd.a
                    smd.a.hide_viewport = False
                    ops.object.mode_set(mode='EDIT', toggle=False)
                    self.existingBones.extend(
                        [b.name for b in smd.a.data.bones])

                missing = validated = 0
                for line in smd.file:
                    if smdBreak(line):
                        break
                    if smdContinue(line):
                        continue

                    id, name, parent = self.parseQuoteBlockedLine(
                        line, lower=False)[:3]
                    id = int(id)
                    parent = int(parent)

                    # names, not IDs, are the key
                    targetBone = smd.a.data.bones.get(name)

                    if targetBone:
                        validated += 1
                    elif append:
                        targetBone = addBone(id, name, parent)
                    else:
                        missing += 1

                    if not smd.boneIDs.get(parent):
                        smd.phantomParentIDs[id] = parent

                    smd.boneIDs[id] = targetBone.name if targetBone else name

                if smd.a != smd.a:
                    removeObject(smd.a)
                    smd.a = smd.a

                print(
                    "- Validated {} bones against armature \"{}\"{}".format(
                        validated,
                        smd.a.name,
                        " (could not find {})".format(
                            missing
                        ) if missing > 0 else ""))

        if not smd.a:
            smd.a = self.createArmature(
                self.truncate_id_name(
                    (self.qc.jobName
                        if self.qc else smd.jobName) +
                    "_skeleton", bpy.types.Armature))
            if self.qc:
                self.qc.a = smd.a

            # Too easy to break compatibility,
            #  plus the skeleton is probably set up already
            smd.a.data.vs.implicit_zero_bone = False

            ops.object.mode_set(mode='EDIT', toggle=False)

            # Read bone definitions from disc
            for line in smd.file:
                if smdBreak(line):
                    break
                if smdContinue(line):
                    continue

                id, name, parent = self.parseQuoteBlockedLine(
                    line, lower=False)[:3]
                addBone(id, name, parent)

        # Apply parents now that all bones exist
        for bone_name, parent_id in boneParents.items():
            if parent_id != -1:
                smd.a.data.edit_bones[bone_name].parent = (
                    smd.a.data.edit_bones[smd.boneIDs[parent_id]])

        ops.object.mode_set(mode='OBJECT')
        if boneParents:
            print("- Imported {} new bones".format(len(boneParents)))
        if len(smd.a.data.bones) > 128:
            self.warning(get_id("importer_err_bonelimit_smd"))

    @classmethod
    def findArmature(self):
        # Search the current scene for an existing armature
        # - there can only be one skeleton in a Source model
        if (bpy.context.active_object and
                bpy.context.active_object.type == 'ARMATURE'):
            return bpy.context.active_object

        def isArmIn(list):
            for ob in list:
                if ob.type == 'ARMATURE':
                    return ob

        a = isArmIn(bpy.context.selected_objects)  # armature in the selection?
        if a:
            return a

        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                a = ob.find_armature()  # armature modifying a selected object?
                if a:
                    return a
        # armature in the scene at all?
        return isArmIn(bpy.context.scene.objects)

    def createArmature(self, armature_name):
        smd = self.smd
        if bpy.context.active_object:
            ops.object.mode_set(mode='OBJECT', toggle=False)
        a = bpy.data.objects.new(
            armature_name, bpy.data.armatures.new(armature_name))
        a.show_in_front = True
        a.data.display_type = 'STICK'
        bpy.context.scene.collection.objects.link(a)

        for i in bpy.context.selected_objects:
            i.select_set(False)  # deselect all objects
        a.select_set(True)
        bpy.context.view_layer.objects.active = a

        if not smd.isDMX:
            ops.object.mode_set(mode='OBJECT')

        return a

    def applyPhantomBoneParent(
        self,
        keyframes,
        phantom_keyframes,
        phantom_parent
    ):
        phantom_source_frame = phantom_keyframe.frame
        # rewind to the last value
        while not (
            phantom_keyframes[phantom_parent].get(
                phantom_keyframe.frame)):
            if phantom_source_frame == 0:
                # should never happen
                continue
            phantom_source_frame -= 1
        # Apply the phantom bone, then recurse

        keyframes[bone][phantom_keyframe.frame].matrix = (
            phantom_keyframes[phantom_parent][phantom_source_frame] @
            keyframes[bone][phantom_keyframe.frame].matrix)
        phantom_parent = smd.phantomParentIDs.get(phantom_parent)

    def applyPhantomBone(self, bone, keyframes, phantom_keyframes):
        for phantom_keyframe in phantom_keyframes[bone]:
                phantom_parent = parentID

                # is there a keyframe to modify?
                if len(keyframes[bone]) >= phantom_keyframe.frame:
                    # parents are recursive
                    while phantom_keyframes.get(phantom_parent):
                        self.applyPhantomBoneParent(
                            keyframes,
                            phantom_keyframes,
                            phantom_parent
                        )

    def readFrames(self):
        smd = self.smd
        # We only care about pose data in some SMD types
        if smd.jobType not in [REF, ANIM]:
            if smd.jobType == FLEX:
                smd.shapeNames = {}
            for line in smd.file:
                line = line.strip()
                if smdBreak(line):
                    return
                if smd.jobType == FLEX and line.startswith("time"):
                    for c in line:
                        if c in ['#', ';', '/']:
                            pos = line.index(c)
                            frame = line[:pos].split()[1]
                            if c == '/':
                                pos += 1
                            smd.shapeNames[frame] = line[pos + 1:].strip()

        a = smd.a

        # bones unused var?
        bones = a.data.bones

        bpy.context.view_layer.objects.active = smd.a
        ops.object.mode_set(mode='POSE')

        num_frames = 0
        keyframes = collections.defaultdict(list)
        # bones that aren't in the reference skeleton
        phantom_keyframes = collections.defaultdict(list)

        for line in smd.file:
            if smdBreak(line):
                break
            if smdContinue(line):
                continue

            values = line.split()

            # frame number is a dummy value, all frames are equally spaced
            if values[0] == "time":
                if num_frames > 0:
                    if smd.jobType == REF:
                        self.warning(
                            get_id(
                                "importer_err_refanim", True).format(
                                    smd.jobName))
                        for line in smd.file:  # skip to end of block
                            if smdBreak(line):
                                break
                            if smdContinue(line):
                                continue
                num_frames += 1
                continue

            # Read SMD data
            pos = Vector([
                float(values[1]),
                float(values[2]),
                float(values[3])])
            rot = Euler([float(values[4]), float(values[5]), float(values[6])])

            keyframe = KeyFrame()
            keyframe.frame = num_frames - 1
            keyframe.matrix = (
                Matrix.Translation(pos) @ rot.to_matrix().to_4x4())
            keyframe.pos = keyframe.rot = True

            # store the keyframe
            values[0] = int(values[0])
            try:
                bone = smd.a.pose.bones[smd.boneIDs[values[0]]]
                if not bone.parent:
                    keyframe.matrix = (
                        getUpAxisMat(smd.upAxis) @ keyframe.matrix)
                keyframes[bone].append(keyframe)
            except KeyError:
                if not smd.phantomParentIDs.get(values[0]):
                    keyframe.matrix = (
                        getUpAxisMat(smd.upAxis) @ keyframe.matrix)
                phantom_keyframes[values[0]].append(keyframe)

        # All frames read, apply phantom bones
        for ID, parentID in smd.phantomParentIDs.items():
            bone = smd.a.pose.bones.get(smd.boneIDs.get(ID))
            if not bone:
                continue
            self.applyPhantomBone(bone, keyframes, phantom_keyframes)

        self.applyFrames(keyframes, num_frames)

    def applyFrames(self, keyframes, num_frames, fps=None):
        smd = self.smd
        ops.object.mode_set(mode='POSE')

        if (self.append != 'VALIDATE' and
            smd.jobType in [REF, ANIM] and not
                self.appliedReferencePose):
            self.appliedReferencePose = True

            for bone in smd.a.pose.bones:
                bone.matrix_basis.identity()
            for bone, kf in keyframes.items():
                if bone.name in self.existingBones:
                    continue
                elif bone.parent and not keyframes.get(bone.parent):
                    bone.matrix = bone.parent.matrix @ kf[0].matrix
                else:
                    bone.matrix = kf[0].matrix
            ops.pose.armature_apply()

            bone_vis = (
                None if self.properties.boneMode == 'NONE'
                else bpy.data.objects.get("smd_bone_vis"))

            if (self.properties.boneMode == 'SPHERE' and
                    (not bone_vis or bone_vis.type != 'MESH')):

                    ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2)
                    bone_vis = bpy.context.active_object
                    bone_vis.data.name = bone_vis.name = "smd_bone_vis"
                    bone_vis.use_fake_user = True
                    for collection in bone_vis.users_collection:
                        # don't want the user deleting this
                        collection.objects.unlink(bone_vis)
                    bpy.context.view_layer.objects.active = smd.a
            elif (self.properties.boneMode == 'ARROWS' and
                    (not bone_vis or bone_vis.type != 'EMPTY')):
                    bone_vis = bpy.data.objects.new("smd_bone_vis", None)
                    bone_vis.use_fake_user = True
                    bone_vis.empty_display_type = 'ARROWS'
                    bone_vis.empty_draw_size = 5

            # Calculate armature dimensions...Blender should be doing this!
            maxs = [0, 0, 0]
            mins = [0, 0, 0]
            for bone in smd.a.data.bones:
                for i in range(3):
                    maxs[i] = max(maxs[i], bone.head_local[i])
                    mins[i] = min(mins[i], bone.head_local[i])

            dimensions = []
            if self.qc:
                self.qc.dimensions = dimensions
            for i in range(3):
                dimensions.append(maxs[i] - mins[i])

            length = max(
                #  very small indeed, but a custom bone is used for display
                0.001,
                (dimensions[0] + dimensions[1] + dimensions[2]) / 600)

            # Apply spheres
            ops.object.mode_set(mode='EDIT')
            for bone in [
                smd.a.data.edit_bones[b.name] for b in keyframes.keys()
            ]:
                # Resize loose bone tails based on armature size
                bone.tail = (
                    bone.head +
                    (bone.tail - bone.head).normalized() * length)
                # apply bone shape
                smd.a.pose.bones[bone.name].custom_shape = bone_vis

        if smd.jobType == ANIM:
            if not smd.a.animation_data:
                smd.a.animation_data_create()

            action = bpy.data.actions.new(smd.jobName)

            if 'ActLib' in dir(bpy.types):
                smd.a.animation_data.action_library.add()
            else:
                action.use_fake_user = True

            smd.a.animation_data.action = action

            if 'fps' in dir(action):
                action.fps = fps if fps else 30
                bpy.context.scene.render.fps = 60
                bpy.context.scene.render.fps_base = 1

            ops.object.mode_set(mode='POSE')

            # Create an animation
            if 'ActLib' in dir(bpy.types):
                bpy.context.scene.use_preview_range = bpy.context.scene.use_preview_range_action_lock = True
            else:
                bpy.context.scene.frame_start = 0
                bpy.context.scene.frame_end = num_frames - 1

            for bone in smd.a.pose.bones:
                bone.rotation_mode = smd.rotMode

            for bone, frames in list(keyframes.items()):
                if not frames:
                    del keyframes[bone]

            if smd.isDMX is False:
                # Remove every point but the first unless there is motion
                still_bones = list(keyframes.keys())
                for bone in keyframes.keys():
                    bone_keyframes = keyframes[bone]
                    for keyframe in bone_keyframes[1:]:
                        diff = (
                            keyframe.matrix.inverted() @
                            bone_keyframes[0].matrix)
                        if (diff.to_translation().length > 0.00001 or
                                abs(diff.to_quaternion().w) > 0.0001):
                            still_bones.remove(bone)
                            break
                for bone in still_bones:
                    keyframes[bone] = [keyframes[bone][0]]

            def applyRecursiveCore(
                keys,
                bone,
                bone_string,
                group,
                curvesLoc,
                curvesRot,
            ):
                for keyframe in keys:
                        if curvesLoc and curvesRot:
                            break
                        if keyframe.pos and not curvesLoc:
                            curvesLoc = []
                            for i in range(3):
                                curve = action.fcurves.new(
                                    data_path=(
                                        bone_string +
                                        "location"),
                                    index=i)
                                curve.group = group
                                curvesLoc.append(curve)
                        if keyframe.rot and not curvesRot:
                            curvesRot = []
                            for i in range(3 if smd.rotMode == 'XYZ' else 4):
                                curve = action.fcurves.new(
                                    data_path=(
                                        bone_string +
                                        "rotation_" +
                                        (
                                            "euler" if smd.rotMode == 'XYZ'
                                            else "quaternion")),
                                    index=i)
                                curve.group = group
                                curvesRot.append(curve)
                # Apply each imported keyframe
                for keyframe in keys:
                    # Transform
                    if smd.a.data.vs.legacy_rotation:
                        keyframe.matrix @= mat_BlenderToSMD.inverted()

                    if bone.parent:
                        if smd.a.data.vs.legacy_rotation:
                            parentMat = (
                                bone.parent.matrix @ mat_BlenderToSMD)
                        else:
                            parentMat = bone.parent.matrix
                        bone.matrix = parentMat @ keyframe.matrix
                    else:
                        bone.matrix = (
                            getUpAxisMat(smd.upAxis) @
                            keyframe.matrix)

                    # Key location
                    if keyframe.pos:
                        for i in range(3):
                            curvesLoc[i].keyframe_points.add(1)
                            curvesLoc[i].keyframe_points[-1].co = [
                                keyframe.frame, bone.location[i]
                            ]

                    # Key rotation
                    if keyframe.rot:
                        if smd.rotMode == 'XYZ':
                            for i in range(3):
                                curvesRot[i].keyframe_points.add(1)
                                curvesRot[i].keyframe_points[-1].co = [
                                    keyframe.frame, bone.rotation_euler[i]
                                ]
                        else:
                            for i in range(4):
                                curvesRot[i].keyframe_points.add(1)
                                curvesRot[i].keyframe_points[-1].co = [
                                    keyframe.frame, bone.rotation_quaternion[i]
                                ]

            # Create Blender keyframes
            def ApplyRecursive(bone):
                keys = keyframes.get(bone)
                if keys:
                    # Generate curves
                    curvesLoc = None
                    curvesRot = None
                    bone_string = "pose.bones[\"{}\"].".format(bone.name)
                    applyRecursiveCore(
                        keys,
                        bone,
                        bone_string,
                        action.groups.new(name=bone.name),
                        curvesLoc,
                        curvesRot)
                # Recurse
                for child in bone.children:
                    ApplyRecursive(child)

            # Start keying
            for bone in smd.a.pose.bones:
                if not bone.parent:
                    ApplyRecursive(bone)

            for fc in action.fcurves:
                fc.update()

        # clear any unkeyed poses
        for bone in smd.a.pose.bones:
            bone.location.zero()
            if smd.rotMode == 'XYZ':
                bone.rotation_euler.zero()
            else:
                bone.rotation_quaternion.identity()
        scn = bpy.context.scene

        # Blender starts on 1, Source starts on 0
        if scn.frame_current == 1:
            scn.frame_set(0)
        else:
            scn.frame_set(scn.frame_current)
        ops.object.mode_set(mode='OBJECT')

        print("- Imported {} frames of animation".format(num_frames))

    def getMeshMaterial(self, mat_name):
        smd = self.smd
        if mat_name:
            mat_name = self.truncate_id_name(mat_name, bpy.types.Material)
        else:
            mat_name = "Material"

        md = smd.m.data
        mat = None
        # Do we have this material already?
        for candidate in bpy.data.materials:
            if candidate.name == mat_name:
                mat = candidate
        if mat:
            # Look for it on this mesh
            if md.materials.get(mat.name):
                for i in range(len(md.materials)):
                    if md.materials[i].name == mat.name:
                        mat_ind = i
                        break
            else:
                # material exists, but not on this mesh
                md.materials.append(mat)
                mat_ind = len(md.materials) - 1
        else:
            # material does not exist
            print("- New material: {}".format(mat_name))
            mat = bpy.data.materials.new(mat_name)
            md.materials.append(mat)
            # Give it a random colour
            randCol = []
            for i in range(3):
                randCol.append(random.uniform(.4, 1))
            randCol.append(1)
            mat.diffuse_color = randCol
            if smd.jobType == PHYS:
                smd.m.display_type = 'SOLID'
            mat_ind = len(md.materials) - 1

        return mat, mat_ind

    # triangles block
    def readPolys(self):
        smd = self.smd
        if smd.jobType not in [REF, PHYS]:
            return

        mesh_name = smd.jobName
        if (smd.jobType == REF and not
            smd.jobName.lower().find("reference") and not
                smd.jobName.lower().endswith("ref")):
            mesh_name += " ref"
        mesh_name = self.truncate_id_name(mesh_name, bpy.types.Mesh)

        # Create a new mesh object,
        #  disable double-sided rendering,
        #  link it to the current scene
        smd.m = bpy.data.objects.new(mesh_name, bpy.data.meshes.new(mesh_name))
        smd.m.parent = smd.a
        smd.g.objects.link(smd.m)
        if smd.jobType == REF:
            # can only have flex on a ref mesh
            if self.qc:
                # for VTA import
                self.qc.ref_mesh = smd.m

        # Create weightmap groups
        for bone in smd.a.data.bones.values():
            smd.m.vertex_groups.new(name=bone.name)

        # Apply armature modifier
        modifier = smd.m.modifiers.new(
            type="ARMATURE",
            name=pgettext("Armature"))
        modifier.object = smd.a

        # Initialisation
        md = smd.m.data

        # unused
        lastWindowUpdate = time.time()

        # Vertex values
        norms = []

        bm = bmesh.new()
        bm.from_mesh(md)
        weightLayer = bm.verts.layers.deform.new()
        uvLayer = bm.loops.layers.uv.new()

        # *************************************************************************************************
        # There are two loops in this function:
        #    one for polygons which continues until the "end" keyword
        #    and one for the vertices on each polygon that loops three times.
        #    We're entering the poly one now.
        countPolys = 0
        badWeights = 0
        vertMap = {}
        allVertexWeights = set()

        # unused
        WeightLink = collections.namedtuple("WeightLink", ["group", "weight"])

        for line in smd.file:
            line = line.rstrip("\n")

            if line and smdBreak(line):
                # normally a blank line means a break,
                #  but Milkshape can export SMDs with
                #  zero-length material names...
                break
            if smdContinue(line):
                continue

            mat, mat_ind = self.getMeshMaterial(
                line if line
                else pgettext(get_id("importer_name_nomat", data=True)))

            # ***************************************************************
            # Enter the vertex loop. This will run three times for each poly.
            vertexCount = 0
            faceVerts = []
            faceWeights = []
            faceUVs = []

            # which of these vertices are weighted uniquely
            #  and should thus be imported without merging?
            splitVerts = []

            for line in smd.file:
                if smdBreak(line):
                    break
                if smdContinue(line):
                    continue
                values = line.split()

                vertexCount += 1
                co = [0, 0, 0]
                norm = [0, 0, 0]

                # Read co-ordinates and normals
                for i in range(1, 4):
                    # 0 is the deprecated bone weight value
                    co[i - 1] = float(values[i])
                    norm[i - 1] = float(values[i + 3])

                co = tuple(co)
                faceVerts.append(co)
                norms.append(norm)

                # Can't do these in the above for loop since there's only two
                faceUVs.append((float(values[7]), float(values[8])))

                # Read weightmap data
                vertWeights = []
                if len(values) > 10 and values[9] != "0":
                    # got weight links?
                    for i in range(10, 10 + (int(values[9]) * 2), 2):
                        # The range between the first and last weightlinks
                        #  (each of which is *two* values)
                        try:
                            bone = smd.a.data.bones[
                                smd.boneIDs[int(values[i])]]
                            vertWeights.append((
                                smd.m.vertex_groups.find(bone.name),
                                float(values[i + 1])))
                        except KeyError:
                            badWeights += 1
                else:
                    # Fall back on the deprecated value
                    #  at the start of the line
                    try:
                        bone = smd.a.data.bones[smd.boneIDs[int(values[0])]]
                        vertWeights.append((
                            smd.m.vertex_groups.find(bone.name),
                            1.0))
                    except KeyError:
                        badWeights += 1

                faceWeights.append(vertWeights)

                coWeight = tuple([co] + vertWeights)
                splitVerts.append(coWeight not in allVertexWeights)
                allVertexWeights.add(coWeight)

                # Three verts? It's time for a new poly
                if vertexCount == 3:
                    for _ in range(2):
                        bmVerts = []

                        # unused
                        newWeights = collections.defaultdict(list)

                        for i in range(3):
                            # if a vertex in this position with
                            #  these bone weights exists, re-use it.
                            bmv = (
                                None if splitVerts[i]
                                else vertMap.get(faceVerts[i]))
                            if bmv is None:
                                bmv = bm.verts.new(faceVerts[i])
                                for link in faceWeights[i]:
                                    bmv[weightLayer][link[0]] = link[1]
                                vertMap[faceVerts[i]] = bmv
                            bmVerts.append(bmv)
                        try:
                            face = bm.faces.new(bmVerts)
                        except ValueError:
                            # face overlaps another,
                            #  try again with all-new vertices
                            splitVerts = [True] * 3
                            continue

                        face.material_index = mat_ind
                        for i in range(3):
                            face.loops[i][uvLayer].uv = faceUVs[i]

                        break
                    break

            # Back in polyland now, with three verts processed.
            countPolys += 1

        bm.to_mesh(md)
        vertMap = None
        bm.free()
        md.update()

        if countPolys:
            ops.object.select_all(action="DESELECT")
            smd.m.select_set(True)
            bpy.context.view_layer.objects.active = smd.m

            ops.object.shade_smooth()

            for poly in smd.m.data.polygons:
                poly.select = True

            smd.m.show_wire = smd.jobType == PHYS

            md.use_auto_smooth = True
            md.normals_split_custom_set(norms)

            if smd.upAxis == 'Y':
                md.transform(rx90)
                md.update()

            if badWeights:
                self.warning(
                    get_id("importer_err_badweights", True).format(
                        badWeights, smd.jobName))
            print("- Imported {} polys".format(countPolys))

    # vertexanimation block
    def readShapes(self):
        smd = self.smd
        if smd.jobType is not FLEX:
            return

        if not smd.m:
            if self.qc:
                smd.m = self.qc.ref_mesh
            else:
                # user selection
                if bpy.context.active_object.type in shape_types:
                    smd.m = bpy.context.active_object
                else:
                    for obj in bpy.context.selected_objects:
                        if obj.type in shape_types:
                            smd.m = obj

        if not smd.m:
            # FIXME: this could actually be supported
            self.error(get_id("importer_err_shapetarget"))
            return

        if hasShapes(smd.m):
            smd.m.active_shape_key_index = 0

        # easier to view each shape,
        #  less confusion when several are active at once
        smd.m.show_only_shape_key = True

        def vec_round(v):
            return Vector([round(co, 3) for co in v])
        co_map = {}
        mesh_cos = [vert.co for vert in smd.m.data.vertices]
        mesh_cos_rnd = None

        smd.vta_ref = None
        vta_cos = []
        vta_ids = []

        making_base_shape = True
        bad_vta_verts = []
        num_shapes = 0
        md = smd.m.data

        for line in smd.file:
            line = line.rstrip("\n")

            if smdBreak(line):
                break
            if smdContinue(line):
                continue

            values = line.split()

            if values[0] == "time":
                shape_name = smd.shapeNames.get(values[1])
                if smd.vta_ref is None:
                    if not hasShapes(smd.m, False):
                        smd.m.shape_key_add(
                            name=shape_name if shape_name
                            else "Basis")
                    vd = bpy.data.meshes.new(name="VTA vertices")
                    vta_ref = smd.vta_ref = bpy.data.objects.new(
                        name=vd.name,
                        object_data=vd)
                    vta_ref.matrix_world = smd.m.matrix_world
                    smd.g.objects.link(vta_ref)

                    vta_err_vg = vta_ref.vertex_groups.new(
                        name=get_id("importer_name_unmatchedvta"))
                elif making_base_shape:
                    vd.vertices.add(len(vta_cos) / 3)
                    vd.vertices.foreach_set("co", vta_cos)
                    num_vta_verts = len(vd.vertices)
                    del vta_cos

                    mod = vta_ref.modifiers.new(
                        name="VTA Shrinkwrap",
                        type='SHRINKWRAP')
                    mod.target = smd.m
                    mod.wrap_method = 'NEAREST_VERTEX'

                    vd = bpy.data.meshes.new_from_object(
                        vta_ref.evaluated_get(
                            bpy.context.evaluated_depsgraph_get()))

                    vta_ref.modifiers.remove(mod)
                    del mod

                    for i in range(len(vd.vertices)):
                        id = vta_ids[i]
                        co = vd.vertices[i].co
                        map_id = None
                        try:
                            map_id = mesh_cos.index(co)
                        except ValueError:
                            if not mesh_cos_rnd:
                                mesh_cos_rnd = [
                                    vec_round(co) for co in mesh_cos]
                            try:
                                map_id = mesh_cos_rnd.index(vec_round(co))
                            except ValueError:
                                bad_vta_verts.append(i)
                                continue
                        co_map[id] = map_id

                    bpy.data.meshes.remove(vd)
                    del vd

                    if bad_vta_verts:
                        err_ratio = len(bad_vta_verts) / num_vta_verts
                        vta_err_vg.add(bad_vta_verts, 1.0, 'REPLACE')
                        message = get_id(
                            "importer_err_unmatched_mesh", True).format(
                                len(bad_vta_verts),
                                int(err_ratio * 100))
                        if err_ratio == 1:
                            self.error(message)
                            return
                        else:
                            self.warning(message)
                    else:
                        removeObject(vta_ref)
                    making_base_shape = False

                if not making_base_shape:
                    smd.m.shape_key_add(
                        name=shape_name if shape_name else values[1])
                    num_shapes += 1

                continue  # to the first vertex of the new shape

            cur_id = int(values[0])
            vta_co = (
                getUpAxisMat(smd.upAxis) @
                Vector([float(values[1]), float(values[2]), float(values[3])]))

            if making_base_shape:
                vta_ids.append(cur_id)
                vta_cos.extend(vta_co)
            else:  # write to the shapekey
                try:
                    md.shape_keys.key_blocks[-1].data[
                        co_map[cur_id]
                    ].co = vta_co
                except KeyError:
                    pass

        print("- Imported", num_shapes, "flex shapes")
