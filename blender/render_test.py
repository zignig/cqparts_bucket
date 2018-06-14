
# using
# https://github.com/ksons/gltf-blender-importer

# snippit , not working script

# make default scene
bpy.ops.import_scene.gltf(filepath="/filepath")

# position camera and stuff
bpy.data.scenes['Scene'].render.filepath = "/filepath/image.png"
bpy.ops.render.render(write_still=True)
