
# using
# https://github.com/ksons/gltf-blender-importer
import bpy
# snippit , not working script

# maybe script build the entire scene
bpy.ops.scene.new(type='NEW')
bpy.context.scene.name = 'cqparts'
# make the world
bpy.ops.world.new()
bpy.data.worlds['World.001'].name = 'NewWorld'

# make default scene
bpy.ops.object.camera_add()
bpy.ops.object.lamp_add(type='POINT')
# turn on ambient occlusion

# 
bpy.ops.import_scene.gltf(filepath="/opt/stash/out.gltf")
# position camera and stuff
theScene = bpy.data.scenes['cqparts']
theScene.render.filepath = "/opt/stash/image.png"
theScene.objects['out'].select = True
bpy.ops.transform.resize(value=(100,100,100))
bpy.ops.render.render(write_still=True)
