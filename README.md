# BlenderSourceTools
Modified version of the Blender Source Tools with some Source 2 specific features.

Original version: https://github.com/Artfunkel/BlenderSourceTools

__Warning: This version is experimental and untested. It may corrupt your .blend files or have other nasty side effects. Please back up your files before using.__

## Usage
1. Extract the `io_scene_valvesource` directory to `AppData\Roaming\Blender Foundation\Blender\2.83\scripts\addons\`
2. Only DMX version Binary 9 Model 22 is supported

## Features
* Support for vertex float maps
 
 Used for cloth attributes. To add a map, use the + button in the *Float Maps* section of the *Source Engine Exportables* pane. Optionally, the output range can be rescaled with the min and max settings. Paint the map using the weight paint tool.

* Bone axis reorientation

Source 2 expects the X axis of bones to point toward the next bone in a chain, enabling the *Rotate Bone X-axis forward* option under *Source Engine Export* will rotate all bones on export, so that the X-axis will face the original Y-axis.

* Model scaling

Scales the entire model on export. Located under *Source Engine Export*. A value of approximately 39 will scale models from metric to inches.

* Forward parity

Located under *Source Engine Export*. DMX option that determines which axis will map to forward (positive X-axis) when imported to the engine.

* Export direct flex keyframes

Exports flex animations directly to DMX without binding them to bones. Located under *Source Engine Export*. To use, assign an action with animated shape keys both to the mesh and the armature. Currently the exporter uses the length of the skeletal animation keyframes in the action, so place bone keyframes at both the start and end of the animation. This likely does not support NLA or any advanced flex features, and does not currently filter out unused shape keys.
