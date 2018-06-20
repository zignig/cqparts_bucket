
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
theScene = bpy.data.scenes['cqparts']

# make and bind the camera
bpy.ops.object.camera_add()
cam = bpy.context.selected_objects[0]
bpy.context.scene.camera = cam
cam.location = (5,5,5)

bpy.ops.object.lamp_add(type='POINT')
lamp = bpy.context.selected_objects[0]
lamp.location = (10,10,10)
# turn on ambient occlusion

# 
#bpy.ops.import_scene.gltf(filepath="/opt/stash/out.gltf")
# position camera and stuff
#theScene.render.filepath = "/opt/stash/image.png"
#theScene.objects['out'].select = True
#bpy.ops.transform.resize(value=(100,100,100))
bpy.ops.render.render(write_still=True)
