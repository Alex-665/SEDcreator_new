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

    if domeShape == 'I' or domeShape == 'SI':
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=setup_properties.nbSubdiv, radius=setup_properties.clusterRadius, calc_uvs=True, enter_editmode=False, align='WORLD', location=centerCluster, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=setup_properties.nbSegment, ring_count=setup_properties.nbRing, radius=setup_properties.clusterRadius, calc_uvs=True, enter_editmode=False, align='WORLD', location=centerCluster, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    shape = bpy.context.selected_objects[0]
    shape.name = "shape_cluster"
    nbCameras = len(shape.data.vertices)
    cam = SEDcreator_utils.createCamera(56, 'FOV')

    for (i, elem) in enumerate(shape.data.vertices):
        # Get the vertices
        v = shape.data.vertices[i]

        co_final = shape.matrix_world @ v.co
        if  SEDcreator_utils.inCube(co_final, x_min, x_max, y_min, y_max, z_min, z_max):
            camName = f"Camera_{context.scene.InfoSED.camNumber + i}"
            current_cam = SEDcreator_utils.createCameraObj(context, camName, cam, (object.location.x + setup_properties.clusterRadius, 0, 0), (90, 0, 90))
            #to keep the cameras where they should be after parenting operation
            current_cam.parent = object
            current_cam.matrix_parent_inverse = object.matrix_world.inverted()
            current_cam.select_set(True)
            context.view_layer.objects.active = current_cam  # (could be improved)
            #bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            current_cam.location = co_final
            bpy.context.view_layer.update()
            if setup_properties.orientationCameras == 'I':
                SEDcreator_utils.look_at_in(current_cam, shape.matrix_world.to_translation())
            elif setup_properties.orientationCameras == 'O':
                SEDcreator_utils.look_at_out(current_cam, shape.matrix_world.to_translation())
            else:
                if len(selected_objet) == 1:
                    #il y aura peut être un problème ici avec la liste des objets sélectionnés
                    SEDcreator_utils.look_at_select(current_cam, selected_objet[0])
                else:
                    SEDcreator_utils.look_at_in(current_cam, shape.matrix_world.to_translation())

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Select the objects
    bpy.data.objects['shape_cluster'].select_set(True)
    # Delete all selected objects
    bpy.ops.object.delete()

    # done
    print("Done")

    return nbCameras
