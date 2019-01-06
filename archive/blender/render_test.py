
# using
# https://github.com/ksons/gltf-blender-importer
import bpy

# snippit , not working script

bpy.ops.wm.addon_enable(module="io_scene_gltf")
# maybe script build the entire scene
bpy.ops.scene.new(type="NEW")
bpy.context.scene.name = "cqparts"
# make the world
bpy.ops.world.new()
world = bpy.data.worlds["World.001"]
world.name = "NewWorld"
world.light_settings.use_ambient_occlusion = True

bpy.context.scene.world = world

theScene = bpy.data.scenes["cqparts"]
theScene.render.filepath = "/opt/stash/image.png"

# make and bind the camera
bpy.ops.object.camera_add()
cam = bpy.context.selected_objects[0]
bpy.context.scene.camera = cam
cam.location = (4, -20, 20)
# add the track
bpy.ops.object.constraint_add(type="TRACK_TO")

# make the target and track the camera
bpy.ops.object.empty_add(type="SPHERE")
tgt = bpy.context.selected_objects[0]
tgt.name = "cam_target"
# select the camers
track = cam.constraints["Track To"]
track.target = bpy.data.objects["cam_target"]
track.up_axis = "UP_Y"
track.track_axis = "TRACK_NEGATIVE_Z"


# lamp 1
bpy.ops.object.lamp_add(type="POINT")
lamp = bpy.context.selected_objects[0]
lamp.location = (10, -10, 10)

# lamp 2
bpy.ops.object.lamp_add(type="POINT")
lamp2 = bpy.context.selected_objects[0]
lamp2.location = (-10, -10, 10)

bpy.ops.import_scene.gltf(filepath="/opt/stash/CompleteFlux/out.gltf")
outer = theScene.objects["out"]
outer.scale = (100, 100, 100)

bpy.ops.render.render(write_still=True)
