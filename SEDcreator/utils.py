import bpy
import math

# Useful functions for all the project

def createCameraObj(context, name, cam, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0)):
    radiansRot = tuple([math.radians(a)
                        for a in rot])  # Convert angles to radians
    obj = bpy.data.objects.new(name, cam)
    obj.location = loc
    obj.rotation_euler = radiansRot
    # Nothing changes but it is easier to read in the 3D Viewer like this
    obj.scale = (1, 1, 1)

    context.collection.objects.link(obj)

    # Move origin (could be improved)
    active = context.view_layer.objects.active
    context.view_layer.objects.active = obj
    #bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    #bpy.ops.object.origin_clear()
    context.view_layer.objects.active = active

    return obj

def strVector3(v3):
    return str(v3.x) + "," + str(v3.y) + "," + str(v3.z)

def look_at_in(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

def look_at_out(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = loc_camera - point
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

def look_at_select(obj_camera, object):
    loc_camera = obj_camera.matrix_world.to_translation()
    point = object.matrix_world.to_translation()
    direction = point - loc_camera
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()
