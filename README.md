This is Blender Source Tools 3.3.1 with fixed importing textures for materials.
Standart-Stock version: When we importing qc\smd this plugin creates materials with same names as texture images. Without importing image-files.
My fix: Automatically importing images in nodes and conecting to material in Node-mode, Roughness 1.0. 
Tested only on Blender 4.1 with GoldSrc models. 
custom function is in "Import_smd.py"
