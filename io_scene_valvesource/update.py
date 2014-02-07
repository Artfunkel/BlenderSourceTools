#  Copyright (c) 2013 Tom Edwards contact@steamreview.org
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

import bpy, io
from .utils import *

class SMD_MT_Updated(bpy.types.Menu):
	bl_label = "Source Tools Update"
	def draw(self,context):
		self.layout.operator("wm.url_open",text="View changelog?",icon='TEXT').url = "http://steamcommunity.com/groups/BlenderSourceTools#announcements"

updater_supported = True
try:
	import urllib.request, urllib.error, zipfile
except:
	updater_supported = False

class SmdToolsUpdate(bpy.types.Operator):
	bl_idname = "script.update_smd"
	bl_label = "Check for Source Tools updates"
	bl_description = "Connects to http://steamreview.org/BlenderSourceTools/latest.php"
	
	@classmethod
	def poll(self,context):
		return updater_supported

	def execute(self,context):	
		print("Source Tools update...")
		
		import sys
		cur_version = sys.modules.get(__name__.split(".")[0]).bl_info['version']		

		try:			
			data = urllib.request.urlopen("http://steamreview.org/BlenderSourceTools/latest.php").read().decode('ASCII').split("\n")
			remote_ver = data[0].strip().split(".")
			remote_bpy = data[1].strip().split(".")
			download_url = "http://steamreview.org/BlenderSourceTools/" + data[2].strip()
			
			for i in range(min( len(remote_bpy), len(bpy.app.version) )):
				if int(remote_bpy[i]) > bpy.app.version[i]:
					self.report({'ERROR'},"The latest Source Tools require Blender {}. Please upgrade.".format( PrintVer(remote_bpy) ))
					return {'FINISHED'}
					
			for i in range(min( len(remote_ver), len(cur_version) )):
				try:
					diff = int(remote_ver[i]) - int(cur_version[i])
				except ValueError:
					continue
				if diff > 0:
					print("Found new version {}, downloading from {}...".format(PrintVer(remote_ver), download_url))
					
					zip = zipfile.ZipFile( io.BytesIO(urllib.request.urlopen(download_url).read()))
					zip.extractall(path=os.path.join(os.path.dirname( os.path.abspath( __file__ ) ),".."))
					
					bpy.ops.script.reload()
					self.report({'INFO'},"Upgraded to Source Tools {}!".format(PrintVer(remote_ver)))
					bpy.ops.wm.call_menu(name="SMD_MT_Updated")
					return {'FINISHED'}
			
			self.report({'INFO'},"The latest Source Tools ({}) are already installed.".format( PrintVer(cur_version) ))
			return {'FINISHED'}
			
		except urllib.error.URLError as err:
			self.report({'ERROR'}," ".join(["Could not complete download:" + str(err)]))
			return {'CANCELLED'}
		except zipfile.BadZipfile:
			self.report({'ERROR'},"Update was downloaded, but file was not valid")
			return {'CANCELLED'}
		except IOError as err:
			self.report({'ERROR'}," ".join(["Could not install update:", str(err)]))
			return {'CANCELLED'}
