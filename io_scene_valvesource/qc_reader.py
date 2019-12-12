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
from bpy import ops
from bpy.props import *
from .utils import *


class QCReader:
    # Parses a QC file
    def readQC(
        self,
        filepath,
        newscene,
        doAnim,
        makeCamera,
        rotMode,
        outer_qc=False
    ):
        filename = os.path.basename(filepath)
        filedir = os.path.dirname(filepath)

        if outer_qc:
            print("\nQC IMPORTER: now working on", filename)

            qc = self.qc = QcInfo()
            qc.startTime = time.time()
            qc.jobName = filename
            qc.root_filedir = filedir
            qc.makeCamera = makeCamera
            qc.animation_names = []
            if newscene:
                # BLENDER BUG: this currently doesn't update bpy.context.scene
                bpy.context.screen.scene = bpy.data.scenes.new(filename)
            else:
                bpy.context.scene.name = filename
        else:
            qc = self.qc

        file = open(filepath, 'r')
        in_bodygroup = in_lod = in_sequence = False
        lod = 0
        for line_str in file:
            line = self.parseQuoteBlockedLine(line_str)
            if len(line) == 0:
                continue
            # print(line)

            # handle individual words
            #  (insert QC variable values, change slashes)
            i = 0
            for word in line:
                for var in qc.vars.keys():
                    kw = "${}$".format(var)
                    pos = word.lower().find(kw)
                    if pos != -1:
                        word = word.replace(
                            word[pos:pos + len(kw)], qc.vars[var])
                line[i] = word.replace("/", "\\")  # studiomdl is Windows-only
                i += 1

            # Skip macros
            if line[0] == "$definemacro":
                self.warning(
                    get_id("importer_qc_macroskip", True).format(filename))
                while line[-1] == "\\\\":
                    line = self.parseQuoteBlockedLine(file.readline())

            # register new QC variable
            if line[0] == "$definevariable":
                qc.vars[line[1]] = line[2].lower()
                continue

            # dir changes
            if line[0] == "$pushd":
                if line[1][-1] != "\\":
                    line[1] += "\\"
                qc.dir_stack.append(line[1])
                continue
            if line[0] == "$popd":
                try:
                    qc.dir_stack.pop()
                except IndexError:
                    pass  # invalid QC, but whatever
                continue

            # up axis
            if line[0] == "$upaxis":
                qc.upAxis = bpy.context.scene.vs.up_axis = line[1].upper()
                qc.upAxisMat = getUpAxisMat(line[1])
                continue

            # bones in pure animation QCs
            if line[0] == "$definebone":
                pass  # TODO

            def import_file(
                word_index,
                default_ext,
                smd_type,
                append='APPEND',
                layer=0,
                in_file_recursion=False
            ):
                path = os.path.join(
                    qc.cd(), appendExt(line[word_index], default_ext))

                if not in_file_recursion and not os.path.exists(path):
                    return import_file(
                        word_index, "dmx", smd_type, append, layer, True)

                #  FIXME: an SMD loaded once relatively and
                #    once absolutely will still pass this test
                if path not in qc.imported_smds:
                    qc.imported_smds.append(path)
                    self.append = append if qc.a else 'NEW_ARMATURE'

                    # import the file
                    self.num_files_imported += (
                        self.readDMX if path.endswith("dmx")
                        else self.readSMD)(
                        path,
                        qc.upAxis,
                        rotMode,
                        False,
                        smd_type,
                        target_layer=layer)
                return True

            # meshes
            if line[0] in ["$body", "$model"]:
                import_file(2, "smd", REF)
                continue
            if line[0] == "$lod":
                in_lod = True
                lod += 1
                continue
            if in_lod:
                if line[0] == "replacemodel":
                    import_file(2, "smd", REF, 'VALIDATE', layer=lod)
                    continue
                if "}" in line:
                    in_lod = False
                    continue
            if line[0] == "$bodygroup":
                in_bodygroup = True
                continue
            if in_bodygroup:
                if line[0] == "studio":
                    import_file(1, "smd", REF)
                    continue
                if "}" in line:
                    in_bodygroup = False
                    continue

            # skeletal animations
            if (in_sequence or
                (
                    doAnim and
                    line[0] in ["$sequence", "$animation"])):
                # there is no easy way to determine whether a SMD is being
                #  defined here or elsewhere, or even precisely where it
                #  is being defined
                num_words_to_skip = 2 if not in_sequence else 0
                for i in range(len(line)):
                    if num_words_to_skip:
                        num_words_to_skip -= 1
                        continue
                    if line[i] == "{":
                        in_sequence = True
                        continue
                    if line[i] == "}":
                        in_sequence = False
                        continue
                    if line[i] in [
                        "hidden",
                        "autolay",
                        "realtime",
                        "snap",
                        "spline",
                        "xfade",
                        "delta",
                        "predelta"
                    ]:
                        continue
                    if line[i] in [
                        "fadein",
                        "fadeout",
                        "addlayer",
                        "blendwidth",
                        "node"
                    ]:
                        num_words_to_skip = 1
                        continue
                    if line[i] in [
                        "activity",
                        "transision",
                        "rtransition"
                    ]:
                        num_words_to_skip = 2
                        continue
                    if line[i] in ["blend"]:
                        num_words_to_skip = 3
                        continue
                    if line[i] in ["blendlayer"]:
                        num_words_to_skip = 5
                        continue
                    # there are many more keywords, but they can only
                    #  appear *after* an SMD is referenced

                    if not qc.a:
                        qc.a = self.findArmature()
                    if not qc.a:
                        self.warning(
                            get_id("qc_warn_noarmature", True).format(
                                line_str.strip()))
                        continue

                    if line[i].lower() not in qc.animation_names:
                        if not qc.a.animation_data:
                            qc.a.animation_data_create()
                        last_action = qc.a.animation_data.action
                        import_file(i, "smd", ANIM, 'VALIDATE')
                        if line[0] == "$animation":
                            qc.animation_names.append(line[1].lower())
                        while i < len(line) - 1:
                            if (line[i] == "fps" and
                                    qc.a.animation_data.action != last_action):
                                if 'fps' in dir(qc.a.animation_data.action):
                                    qc.a.animation_data.action.fps = float(
                                        line[i + 1])
                            i += 1
                    break
                continue

            # flex animation
            if line[0] == "flexfile":
                import_file(1, "vta", FLEX, 'VALIDATE')
                continue

            # naming shapes
            if line[0] in ["flex", "flexpair"]:
                # "flex" is safe because it cannot come before "flexfile"
                for i in range(1, len(line)):
                    if line[i] == "frame":
                        shape = qc.ref_mesh.data.shape_keys.key_blocks.get(
                            line[i + 1])
                        if shape and shape.name.startswith("Key"):
                            shape.name = line[1]
                        break
                continue

            # physics mesh
            if line[0] in ["$collisionmodel", "$collisionjoints"]:
                # FIXME: what if there are >10 LODs?
                import_file(1, "smd", PHYS, 'VALIDATE', layer=10)
                continue

            # origin; this is where viewmodel editors should put their
            #   camera, and is in general something to be aware of
            if line[0] == "$origin":
                if qc.makeCamera:
                    data = bpy.data.cameras.new(qc.jobName + "_origin")
                    name = "camera"
                else:
                    data = None
                    name = "empty object"
                print("QC IMPORTER: created {} at $origin\n".format(name))

                origin = bpy.data.objects.new(qc.jobName + "_origin", data)
                smd.g.objects.link(origin)

                origin.rotation_euler = (
                    #  works, but adding seems very wrong!
                    Vector([pi / 2, 0, pi]) +
                    Vector(getUpAxisMat(qc.upAxis).inverted().to_euler()))
                ops.object.select_all(action="DESELECT")
                origin.select_set(True)
                ops.object.transform_apply(rotation=True)

                for i in range(3):
                    origin.location[i] = float(line[i + 1])
                origin.matrix_world = (
                    getUpAxisMat(qc.upAxis) @
                    origin.matrix_world)

                if qc.makeCamera:
                    bpy.context.scene.camera = origin
                    origin.data.lens_unit = 'DEGREES'

                    # value always in mm; this number == 54 degrees
                    origin.data.lens = 31.401752

                    # Blender's FOV isn't locked to X or Y height,
                    #  so a shift is needed to get the weapon aligned properly.
                    # This is a nasty hack, and the values are only valid for
                    #  the default 54 degrees angle
                    origin.data.shift_y = -0.27
                    origin.data.shift_x = 0.36
                    origin.data.passepartout_alpha = 1
                else:
                    origin.empty_display_type = 'PLAIN_AXES'

                qc.origin = origin

            # QC inclusion
            if line[0] == "$include":
                # special case: ignores dir stack
                path = os.path.join(qc.root_filedir, line[1])
                if not path.endswith(".qc") and not path.endswith(".qci"):
                    if os.path.exists(appendExt(path, ".qci")):
                        path = appendExt(path, ".qci")
                    elif os.path.exists(appendExt(path, ".qc")):
                        path = appendExt(path, ".qc")
                try:
                    self.readQC(path, False, doAnim, makeCamera, rotMode)
                except IOError:
                    self.warning(get_id("importer_err_qci", True).format(path))

        file.close()

        if qc.origin:
            qc.origin.parent = qc.a
            if qc.ref_mesh:
                size = min(qc.ref_mesh.dimensions) / 15
                if qc.makeCamera:
                    qc.origin.data.draw_size = size
                else:
                    qc.origin.empty_draw_size = size

        if outer_qc:
            printTimeMessage(qc.startTime, filename, "import", "QC")
        return self.num_files_imported
