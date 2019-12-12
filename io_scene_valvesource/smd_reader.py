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
import collections
from bpy import ops
from bpy.app.translations import pgettext
from bpy.props import *

from . import datamodel
from .utils import *


class SMDReader():
    def initSMD(self, filepath, smd_type, upAxis, rotMode, target_layer):
        smd = self.smd = SmdInfo()
        smd.jobName = os.path.splitext(os.path.basename(filepath))[0]
        smd.jobType = smd_type
        smd.startTime = time.time()
        smd.layer = target_layer
        smd.rotMode = rotMode
        smd.g = bpy.data.collections.new(smd.jobName)
        bpy.context.scene.collection.children.link(smd.g)
        if self.qc:
            smd.upAxis = self.qc.upAxis
            smd.a = self.qc.a
        if upAxis:
            smd.upAxis = upAxis

        return smd

    # Parses an SMD file
    def readSMD(
        self,
        filepath,
        upAxis,
        rotMode,
        newscene=False,
        smd_type=None,
        target_layer=0
    ):
        if filepath.endswith("dmx"):
            return self.readDMX(
                filepath,
                upAxis,
                newscene,
                smd_type)

        smd = self.initSMD(filepath, smd_type, upAxis, rotMode, target_layer)
        self.appliedReferencePose = False

        try:
            smd.file = file = open(filepath, 'r')
        except IOError as err:
            # TODO: work out why errors are swallowed if I don't do this!
            self.error(
                get_id("importer_err_smd", True).format(
                    smd.jobName, err))
            return 0

        if newscene:
            # BLENDER BUG: this currently doesn't update bpy.context.scene
            bpy.context.screen.scene = bpy.data.scenes.new(smd.jobName)
        elif bpy.context.scene.name == pgettext("Scene"):
            bpy.context.scene.name = smd.jobName

        print("\nSMD IMPORTER: now working on", smd.jobName)

        while True:
            header = self.parseQuoteBlockedLine(file.readline())
            if header:
                break

        if header != ["version", "1"]:
            self.warning(get_id("importer_err_smd_ver"))

        if smd.jobType is None:
            # What are we dealing with?
            self.scanSMD()

        for line in file:
            if line == "nodes\n":
                self.readNodes()
            if line == "skeleton\n":
                self.readFrames()
            if line == "triangles\n":
                self.readPolys()
            if line == "vertexanimation\n":
                self.readShapes()

        file.close()
        printTimeMessage(smd.startTime, smd.jobName, "import")
        return 1

    def readDMX(
        self,
        filepath,
        upAxis,
        rotMode,
        newscene=False,
        smd_type=None,
        target_layer=0
    ):
        smd = self.initSMD(filepath, smd_type, upAxis, rotMode, target_layer)
        smd.isDMX = 1

        bench = BenchMarker(1, "DMX")

        target_arm = (
            self.findArmature() if self.append != 'NEW_ARMATURE'
            else None)
        if target_arm:
            smd.a = target_arm

        ob = bone = restData = smd.atch = None
        smd.layer = target_layer
        if bpy.context.active_object:
            ops.object.mode_set(mode='OBJECT')
        self.appliedReferencePose = False

        print("\nDMX IMPORTER: now working on", os.path.basename(filepath))

        # unused
        error = None

        try:
            print("- Loading DMX...")
            try:
                dm = datamodel.load(filepath)
            except IOError as e:
                self.error(e)
                return 0
            bench.report("Load DMX")

            if bpy.context.scene.name.startswith("Scene"):
                bpy.context.scene.name = smd.jobName

            keywords = getDmxKeywords(dm.format_ver)

            if not smd_type:
                smd.jobType = REF if dm.root.get("model") else ANIM
            self.ensureAnimationBonesValidated()

            DmeModel = dm.root["skeleton"]

            # unused
            FlexControllers = dm.root.get("combinationOperator")

            transforms = (
                DmeModel["baseStates"][0]["transforms"] if (
                    DmeModel.get("baseStates") and
                    len(DmeModel["baseStates"]) > 0)
                else None)

            DmeAxisSystem = DmeModel.get("axisSystem")
            if DmeAxisSystem:
                for axis in axes_lookup.items():
                    if axis[1] == DmeAxisSystem["upAxis"] - 1:
                        upAxis = smd.upAxis = axis[0]
                        break

            def getBlenderQuat(datamodel_quat):
                return Quaternion([
                    datamodel_quat[3],
                    datamodel_quat[0],
                    datamodel_quat[1],
                    datamodel_quat[2]])

            def get_transform_matrix(elem):
                out = Matrix()
                if not elem:
                    return out
                trfm = elem.get("transform")
                if transforms:
                    for e in transforms:
                        if e.name == elem.name:
                            trfm = e
                if not trfm:
                    return out
                out @= Matrix.Translation(Vector(trfm["position"]))
                out @= getBlenderQuat(trfm["orientation"]).to_matrix().to_4x4()
                return out

            def isBone(elem):
                return elem.type in ["DmeDag", "DmeJoint"]

            # Skeleton
            bone_matrices = {}
            restData = {}
            if target_arm:
                missing_bones = []

                def validateSkeleton(elem_array, parent_elem):
                    for elem in [
                        item for item in elem_array if (
                            item.type == "DmeJoint" and
                            item.name != "blender_implicit") or (
                                item.type == "DmeDag" and
                                item.get("shape") is None)
                    ]:
                        bone = smd.a.data.edit_bones.get(elem.name)
                        if not bone:
                            if (self.append == 'APPEND' and
                                    smd.jobType in [REF, ANIM]):
                                bone = smd.a.data.edit_bones.new(
                                    self.truncate_id_name(
                                        elem.name, bpy.types.Bone))
                                if parent_elem:
                                    bone.parent = smd.a.data.edit_bones[
                                        parent_elem.name]
                                bone.tail = (0, 5, 0)
                                bone_matrices[
                                    bone.name] = get_transform_matrix(elem)
                                smd.boneIDs[elem.id] = bone.name
                                smd.boneTransformIDs[
                                    elem["transform"].id] = bone.name
                                if elem.get("children"):
                                    validateSkeleton(elem["children"], elem)
                            else:
                                missing_bones.append(elem.name)
                        else:
                            scene_parent = (
                                bone.parent.name if bone.parent
                                else "<None>")
                            dmx_parent = (
                                parent_elem.name if parent_elem
                                else "<None>")
                            if scene_parent != dmx_parent:
                                self.warning(
                                    get_id(
                                        'importer_bone_parent_miss',
                                        True).format(
                                            elem.name,
                                            scene_parent,
                                            dmx_parent,
                                            smd.jobName))

                            smd.boneIDs[elem.id] = bone.name
                            smd.boneTransformIDs[
                                elem["transform"].id] = bone.name

                        if elem.get("children"):
                            validateSkeleton(elem["children"], elem)

                bpy.context.view_layer.objects.active = smd.a
                smd.a.hide_viewport = False
                ops.object.mode_set(mode='EDIT')
                validateSkeleton(DmeModel["children"], None)

                if missing_bones and smd.jobType != ANIM:
                    # animations report missing bones seperately
                    self.warning(
                        get_id("importer_err_missingbones", True).format(
                            smd.jobName,
                            len(missing_bones),
                            smd.a.name))
                    print("\n".join(missing_bones))
            elif any(
                child for child in DmeModel["children"]
                    if child and isBone(child)):
                self.append = 'NEW_ARMATURE'
                ob = smd.a = self.createArmature(
                    self.truncate_id_name(DmeModel.name, bpy.types.Armature))
                if self.qc:
                    self.qc.a = ob
                bpy.context.view_layer.objects.active = smd.a
                ops.object.mode_set(mode='EDIT')

                smd.a.matrix_world = getUpAxisMat(smd.upAxis)

                def parseSkeleton(elem_array, parent_bone):
                    for elem in elem_array:
                        if (elem.type == "DmeDag" and
                            elem.get("shape") and
                                elem["shape"].type == "DmeAttachment"):
                            atch = smd.atch = bpy.data.objects.new(
                                name=self.truncate_id_name(
                                    elem["shape"].name,
                                    "Attachment"),
                                object_data=None)
                            smd.g.objects.link(atch)
                            atch.show_in_front = True
                            atch.empty_display_type = 'ARROWS'

                            atch.parent = smd.a
                            if parent_bone:
                                atch.parent_type = 'BONE'
                                atch.parent_bone = parent_bone.name

                            atch.matrix_local = get_transform_matrix(elem)
                        elif ((
                                isBone(elem) and
                                elem.name != "blender_implicit") and not
                              elem.get("shape")):
                                # don't import Dags which simply wrap meshes
                            bone = smd.a.data.edit_bones.new(
                                self.truncate_id_name(
                                    elem.name,
                                    bpy.types.Bone)
                            )
                            bone.parent = parent_bone
                            bone.tail = (0, 5, 0)
                            bone_matrices[bone.name] = get_transform_matrix(
                                elem)
                            smd.boneIDs[elem.id] = bone.name
                            smd.boneTransformIDs[
                                elem["transform"].id] = bone.name
                            if elem.get("children"):
                                parseSkeleton(elem["children"], bone)

                parseSkeleton(DmeModel["children"], None)

            if smd.a:
                ops.object.mode_set(mode='POSE')
                for bone in smd.a.pose.bones:
                    mat = bone_matrices.get(bone.name)
                    if mat:
                        keyframe = KeyFrame()
                        keyframe.matrix = mat
                        restData[bone] = [keyframe]
                if restData:
                    self.applyFrames(restData, 1, None)

            def parseModel(elem, matrix=Matrix(), last_bone=None):
                if elem.type in ["DmeModel", "DmeDag", "DmeJoint"]:
                    if elem.type == "DmeDag":
                        matrix = matrix @ get_transform_matrix(elem)
                    if elem.get("children") and elem["children"]:
                        if elem.type == "DmeJoint":
                            last_bone = elem
                        subelems = elem["children"]
                    elif elem.get("shape"):
                        subelems = [elem["shape"]]
                    else:
                        return
                    for subelem in subelems:
                        parseModel(subelem, matrix, last_bone)
                elif elem.type == "DmeMesh":
                    DmeMesh = elem
                    if bpy.context.active_object:
                        ops.object.mode_set(mode='OBJECT')
                    mesh_name = self.truncate_id_name(
                        DmeMesh.name,
                        bpy.types.Mesh)
                    ob = smd.m = bpy.data.objects.new(
                        name=mesh_name,
                        object_data=bpy.data.meshes.new(name=mesh_name))
                    smd.g.objects.link(ob)
                    ob.show_wire = smd.jobType == PHYS

                    DmeVertexData = DmeMesh["currentState"]
                    have_weightmap = (
                        keywords["weight"] in DmeVertexData["vertexFormat"])

                    if smd.a:
                        ob.parent = smd.a
                        if have_weightmap:
                            amod = ob.modifiers.new(
                                name="Armature",
                                type='ARMATURE')
                            amod.object = smd.a
                            amod.use_bone_envelopes = False
                    else:
                        ob.matrix_local = getUpAxisMat(smd.upAxis)

                    print("Importing DMX mesh \"{}\"".format(DmeMesh.name))

                    bm = bmesh.new()
                    bm.from_mesh(ob.data)

                    positions = DmeVertexData[keywords['pos']]
                    positionsIndices = (
                        DmeVertexData[keywords['pos'] + "Indices"])

                    # Vertices
                    for pos in positions:
                        bm.verts.new(Vector(pos))

                    if hasattr(bm.verts, 'ensure_lookup_table'):
                        bm.verts.ensure_lookup_table()

                    # Faces, Materials, Colours
                    skipfaces = set()
                    vertex_colour_layers = []

                    class VertexColourInfo():
                        def __init__(self, layer, indices, colours):
                            self.layer = layer
                            self.indices = indices
                            self.colours = colours

                        def get_loop_color(self, loop_index):
                            return self.colours[self.indices[loop_index]]

                    for map_name in vertex_maps:
                        attribute_name = keywords.get(map_name)
                        if (attribute_name and
                            attribute_name in
                                DmeVertexData["vertexFormat"]):
                            vertex_colour_layers.append(VertexColourInfo(
                                bm.loops.layers.color.new(map_name),
                                DmeVertexData[attribute_name + "Indices"],
                                DmeVertexData[attribute_name]
                            ))
                        if DatamodelFormatVersion() < 22:
                            bpy.context.scene.vs.dmx_format = '22'

                    for face_set in DmeMesh["faceSets"]:
                        mat_path = face_set["material"]["mtlName"]
                        bpy.context.scene.vs.material_path = os.path.dirname(
                            mat_path).replace("\\", "/")
                        mat, mat_ind = self.getMeshMaterial(
                            os.path.basename(mat_path))
                        face_loops = []
                        dmx_face = 0
                        for vert in face_set["faces"]:
                            if vert != -1:
                                face_loops.append(vert)
                                continue

                            # -1 marks the end of a face
                            #  definition, time to create it!
                            try:
                                face = bm.faces.new([
                                    bm.verts[positionsIndices[loop]]
                                    for loop in face_loops
                                ])
                                face.smooth = True
                                face.material_index = mat_ind

                                # Apply Source 2 vertex colours
                                for colour_layer in vertex_colour_layers:
                                    for i, loop in enumerate(face.loops):
                                        loop[colour_layer.layer] = colour_layer.get_loop_color(face_loops[i])

                            except ValueError: # Can't have an overlapping face...this will be painful later
                                skipfaces.add(dmx_face)
                            dmx_face += 1
                            face_loops.clear()

                    # Move from BMesh to Blender
                    bm.to_mesh(ob.data)
                    ob.data.update()
                    ob.matrix_world @= matrix
                    if ob.parent:
                        ob.matrix_world = (
                            ob.parent.matrix_world @
                            ob.matrix_world)
                    if smd.jobType == PHYS:
                        ob.display_type = 'SOLID'

                    # Normals
                    ob.data.create_normals_split()
                    ob.data.use_auto_smooth = True

                    normals = DmeVertexData[keywords['norm']]
                    normalsIndices = (
                        DmeVertexData[keywords['norm'] + "Indices"])

                    normals_ordered = [None] * len(ob.data.loops)
                    i = f = 0
                    for vert in [
                        vert for faceset in
                        DmeMesh["faceSets"] for vert in faceset["faces"]
                    ]:
                        if vert == -1:
                            f += 1
                            continue
                        if f in skipfaces:
                            continue

                        normals_ordered[i] = normals[normalsIndices[vert]]
                        i += 1

                    ob.data.normals_split_custom_set(normals_ordered[:i])

                    # Weightmap
                    if have_weightmap:
                        jointList = (
                            DmeModel["jointList"] if dm.format_ver >= 11
                            else DmeModel["jointTransforms"])
                        jointWeights = DmeVertexData[
                            keywords["weight"]]
                        jointIndices = DmeVertexData[
                            keywords["weight_indices"]]
                        jointRange = range(DmeVertexData["jointCount"])
                        full_weights = collections.defaultdict(list)
                        joint_index = 0
                        for vert_index in range(len(ob.data.vertices)):
                            for i in jointRange:
                                weight = jointWeights[joint_index]
                                if weight > 0:
                                    bone_id = jointList[
                                        jointIndices[joint_index]].id
                                    if dm.format_ver >= 11:
                                        bone_name = smd.boneIDs[bone_id]
                                    else:
                                        bone_name = smd.boneTransformIDs[bone_id]
                                    vg = ob.vertex_groups.get(bone_name)
                                    if not vg:
                                        vg = ob.vertex_groups.new(name=bone_name)
                                    if weight == 1:
                                        full_weights[vg].append(vert_index)
                                    elif weight > 0:
                                        vg.add([vert_index], weight,'REPLACE')
                                joint_index += 1

                        for vg, verts in iter(full_weights.items()):
                            vg.add(verts, 1,'REPLACE')
                    elif last_bone: # bone parent
                        ob.parent_type = 'BONE'
                        ob.parent_bone = last_bone.name

                    # Stereo balance
                    if keywords['balance'] in DmeVertexData["vertexFormat"]:
                        vg = ob.vertex_groups.new(
                            name=get_id(
                                "importer_balance_group",
                                data=True))
                        balanceIndices = DmeVertexData[
                            keywords['balance'] + "Indices"]
                        balance = DmeVertexData[keywords['balance']]
                        ones = []
                        for i in balanceIndices:
                            val = balance[i]
                            if val == 0:
                                continue
                            elif val == 1:
                                ones.append(i)
                            else:
                                vg.add([i], val,'REPLACE')
                        vg.add(ones, 1,'REPLACE')

                        ob.data.vs.flex_stereo_mode = 'VGROUP'
                        ob.data.vs.flex_stereo_vg = vg.name
                    # UV
                    if keywords['texco'] in DmeVertexData["vertexFormat"]:
                        ob.data.uv_layers.new()
                        uv_data = ob.data.uv_layers[0].data
                        textureCoordinatesIndices = DmeVertexData[
                            keywords['texco'] + "Indices"]
                        textureCoordinates = DmeVertexData[keywords['texco']]
                        uv_vert = 0
                        dmx_face = 0
                        skipping = False
                        for faceset in DmeMesh["faceSets"]:
                            for vert in faceset["faces"]:
                                if vert == -1:
                                    dmx_face += 1
                                    skipping = dmx_face in skipfaces
                                if skipping:
                                    # need to skip overlapping
                                    # faces which couldn't be imported
                                    continue

                                if vert != -1:
                                    uv_data[uv_vert].uv = textureCoordinates[
                                        textureCoordinatesIndices[vert]]
                                    uv_vert += 1

                    # Shapes
                    if DmeMesh.get("deltaStates"):
                        for DmeVertexDeltaData in DmeMesh["deltaStates"]:
                            if not ob.data.shape_keys:
                                ob.shape_key_add(name="Basis")
                                ob.show_only_shape_key = True
                                ob.data.shape_keys.name = DmeMesh.name
                            shape_key = ob.shape_key_add(
                                name=DmeVertexDeltaData.name)

                            if (keywords['pos'] in
                                    DmeVertexDeltaData["vertexFormat"]):
                                deltaPositions = DmeVertexDeltaData[
                                    keywords['pos']]
                                for i, posIndex in enumerate(
                                    DmeVertexDeltaData[
                                        keywords['pos'] + "Indices"
                                    ]
                                ):
                                    shape_key.data[posIndex].co += Vector(
                                        deltaPositions[i])

            if smd.jobType in [REF, PHYS]:
                parseModel(DmeModel)

            if smd.jobType == ANIM:
                print("Importing DMX animation \"{}\"".format(smd.jobName))

                animation = dm.root["animationList"]["animations"][0]

                # very, very old DMXs don't have this
                frameRate = animation.get("frameRate", 30)
                timeFrame = animation["timeFrame"]

                # unused
                scale = timeFrame.get("scale", 1.0)

                duration = timeFrame[
                    "duration" if dm.format_ver >= 11
                    else "durationTime"
                ]
                offset = timeFrame.get(
                    "offset" if dm.format_ver >= 11
                    else "offsetTime", 0.0)
                start = timeFrame.get("start", 0)

                if type(duration) == int:
                    duration = datamodel.Time.from_int(duration)
                if type(offset) == int:
                    offset = datamodel.Time.from_int(offset)

                # need a frame for 0 too!
                total_frames = ceil(duration * frameRate) + 1

                keyframes = collections.defaultdict(list)
                unknown_bones = []
                for channel in animation["channels"]:
                    toElement = channel["toElement"]
                    if not toElement:
                        continue  # SFM

                    bone_name = smd.boneTransformIDs.get(toElement.id)
                    bone = (
                        smd.a.pose.bones.get(bone_name) if bone_name
                        else None)
                    if not bone:
                        if (self.append != 'NEW_ARMATURE' and
                                toElement.name not in unknown_bones):
                            unknown_bones.append(toElement.name)
                            print(
                                "- Animation refers to "
                                "unrecognised bone \"{}\"".format(
                                    toElement.name))
                        continue

                    is_position_channel = channel["toAttribute"] == "position"
                    is_rotation_channel = (
                        channel["toAttribute"] == "orientation")
                    if not (is_position_channel or is_rotation_channel):
                        continue

                    frame_log = channel["log"]["layers"][0]
                    times = frame_log["times"]
                    values = frame_log["values"]

                    for i in range(len(times)):
                        frame_time = times[i] + start
                        if type(frame_time) == int:
                            frame_time = datamodel.Time.from_int(frame_time)
                        frame_value = values[i]

                        keyframe = KeyFrame()
                        keyframes[bone].append(keyframe)

                        keyframe.frame = frame_time * frameRate

                        if not (bone.parent or keyframe.pos or keyframe.rot):
                            keyframe.matrix = getUpAxisMat(
                                smd.upAxis).inverted()

                        if is_position_channel and not keyframe.pos:
                            keyframe.matrix @= Matrix.Translation(frame_value)
                            keyframe.pos = True
                        elif is_rotation_channel and not keyframe.rot:
                            keyframe.matrix @= getBlenderQuat(
                                frame_value).to_matrix().to_4x4()
                            keyframe.rot = True

                smd.a.hide_viewport = False
                bpy.context.view_layer.objects.active = smd.a
                if unknown_bones:
                    self.warning(
                        get_id("importer_err_missingbones", True).format(
                            smd.jobName, len(unknown_bones), smd.a.name))

                # apply the keframes
                self.applyFrames(keyframes, total_frames, frameRate)

                bpy.context.scene.frame_end += int(
                    round(start * 2 * frameRate, 0))

        except datamodel.AttributeError as e:
            e.args = [
                "Invalid DMX file: {}".format(
                    e.args[0] if e.args else "Unknown error")]
            raise

        bench.report("DMX imported in")
        return 1
