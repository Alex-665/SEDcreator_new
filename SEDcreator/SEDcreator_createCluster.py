import bpy
import math
from SEDcreator import SEDcreator_utils

# Creation of the cluster of cameras and link them to the associated empty

def create(context, object):
    setup_properties = context.scene.SetupProperties
    centerCluster = object.location
    domeShape = setup_properties.domeShape
    x_min = context.scene.SetupProperties.x_min
    x_max = context.scene.SetupProperties.x_max
    y_min = context.scene.SetupProperties.y_min
    y_max = context.scene.SetupProperties.y_max
    z_min = context.scene.SetupProperties.z_min
    z_max = context.scene.SetupProperties.z_max

    # Delete children of the empty (ancient cameras)
    SEDcreator_utils.deleteChildren(object)

    if domeShape == 'I' or domeShape == 'SI' or domeShape == 'AI':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=setup_properties.nbSubdiv, radius=setup_properties.clusterRadius, calc_uvs=True, enter_editmode=False, align='WORLD', location=centerCluster, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=setup_properties.nbSegment, ring_count=setup_properties.nbRing, radius=setup_properties.clusterRadius, calc_uvs=True, enter_editmode=False, align='WORLD', location=centerCluster, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    shape = bpy.context.selected_objects[0]
    shape.name = "shape_cluster"
    nbCameras = len(shape.data.vertices)
    cam = SEDcreator_utils.createCamera(context, 'FOV')

    for (i, elem) in enumerate(shape.data.vertices):
        # Get the vertices
        v = shape.data.vertices[i]
        co_final = shape.matrix_world @ v.co

        if  (domeShape == 'SI'or domeShape == 'SS') and (object.location.z - co_final.z <= 0):
            SEDcreator_utils.createCameraOnShape(context, object, shape, cam, v, co_final)
        if (domeShape == 'AI' or domeShape == 'AS') and SEDcreator_utils.inCube(co_final, x_min, x_max, y_min, y_max, z_min, z_max):
            SEDcreator_utils.createCameraOnShape(context, object, shape, cam, v, co_final)
        if domeShape == 'I' or domeShape == 'U':
            SEDcreator_utils.createCameraOnShape(context, object, shape, cam, v, co_final)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Select the objects
    bpy.data.objects['shape_cluster'].select_set(True)
    # Delete all selected objects
    bpy.ops.object.delete()

    # done
    print("Done")

    return nbCameras
