
# using
# https://github.com/ksons/gltf-blender-importer
import bpy
# snippit , not working script

# make default scene
bpy.ops.import_scene.gltf(filepath="/opt/stash/out.gltf")
# position camera and stuff
bpy.data.scenes['Scene'].render.filepath = "/opt/stash/image.png"
bpy.data.scenes['Scene'].objects['out'].select = True
bpy.ops.transform.resize(value=(100,100,100))
bpy.ops.render.render(write_still=True)
