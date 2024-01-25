import bpy
import math

# Useful functions for all the project
def inCube(obj_location, x_min, x_max, y_min, y_max, z_min, z_max):
    return (obj_location.x >= x_min and obj_location.x <= x_max) and (obj_location.y >= y_min and obj_location.y <= y_max) and (obj_location.z >= z_min and obj_location.z <= z_max)

def createCamera(angle, lens):
    cam = bpy.data.cameras.new("Camera")
    cam.lens_unit = lens
    cam.angle = math.radians(angle)
    return cam

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

def replace_material_by_original(object):
    if object.material_slots:
        mat = object.material_slots[0].material
        tree = mat.node_tree
        nodes = tree.nodes
        
        #get Principled node
        principled = nodes['Principled BSDF']
        
        #get Material Output node
        material_output = nodes['Material Output']
        
        #change link
        tree.links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])

def remove_attribute_from_all_materials():
    materials = bpy.data.materials
    for mat in materials:
        if mat.node_tree:
            #get Material Output node
            material_output = mat.node_tree.nodes['Material Output']
            mo_sockets = material_output.inputs
            
            #get the node that is connected to the Material Output
            link = mo_sockets['Surface'].links[0]
            link_nodes = link.from_node
            
            #if this node is Attribute, remove it
            if link_nodes.outputs[0].name == "Color":
                mat.node_tree.nodes.remove(mat.node_tree.nodes['Attribute'])

def replace_material_by_curvature(object):
    if object.material_slots:
        mat = object.material_slots[0].material
        tree = mat.node_tree
        nodes = tree.nodes

        #get Attribute node
        attribute = nodes['Attribute']
        
        #get Material Output node
        material_output = nodes['Material Output']
        
        #change link
        tree.links.new(attribute.outputs['Color'], material_output.inputs['Surface'])


def add_attribute_to_all_materials():
    materials = bpy.data.materials
    for mat in materials:
        if mat.node_tree:
            attribute = mat.node_tree.nodes.new("ShaderNodeAttribute")
            attribute.attribute_type = 'GEOMETRY'
            attribute.attribute_name = "Curvature"

def replace_material_by_roughness(object):
    if object.material_slots:
        mat = object.material_slots[0].material
        tree = mat.node_tree
        nodes = tree.nodes
        
        #get Principled node
        principled = nodes['Principled BSDF']
        p_sockets = principled.inputs
        
        #get Roughness image node, if it exists
        if p_sockets['Roughness'].links:
            p_link_roughness = p_sockets['Roughness'].links[0]
            roughness = p_link_roughness.from_node
            
            #get Material Output node
            material_output = nodes['Material Output']
            
            #change link
            tree.links.new(roughness.outputs['Color'], material_output.inputs['Surface'])

#initialize curvature node group
def curvature_node_group():
    curvature = bpy.data.node_groups.new(type = 'GeometryNodeTree', name = "VertexGroupWriterFromCurvature")
    curvature.is_tool = True
    curvature.is_modifier = True

    #initialize curvature nodes
    
    #segmentation inputs
    #input Geometry
    curvature.interface.new_socket(name = 'Geometry', in_out ="INPUT", socket_type = "NodeSocketGeometry")
    curvature.interface.items_tree[0].attribute_domain = 'POINT'

    #node Group Input
    group_input = curvature.nodes.new("NodeGroupInput")
    
    #node Math - Divide
    normalize = curvature.nodes.new("ShaderNodeMath")
    normalize.operation = 'DIVIDE'
    #Value_001
    normalize.inputs[1].default_value = 3.16

    #node Math - Multiply
    eraser = curvature.nodes.new("ShaderNodeMath")
    eraser.operation = 'MULTIPLY'
    #Value_002
    eraser.inputs[1].default_value = 0

    #node Math - Add
    half_of_one = curvature.nodes.new("ShaderNodeMath")
    half_of_one.operation = 'ADD'
    #Value_002
    half_of_one.inputs[1].default_value = 0.5
    
    #node Named Attribute
    named_attribute = curvature.nodes.new("GeometryNodeInputNamedAttribute")
    named_attribute.inputs[0].default_value = "Curvature"
    
    #node Math - Add
    math_add = curvature.nodes.new("ShaderNodeMath")
    math_add.operation = 'ADD'
    math_add.use_clamp = True
    
    #node store named attribute
    store_attribute = curvature.nodes.new("GeometryNodeStoreNamedAttribute")
    store_attribute.data_type = 'FLOAT'
    store_attribute.domain = 'POINT'
    store_attribute.inputs["Name"].default_value = "Curvature"
    
    #node Edge Angle
    edge_angle = curvature.nodes.new("GeometryNodeInputMeshEdgeAngle")
    
    #segmentation outputs
    #output Geometry
    curvature.interface.new_socket(name = 'Geometry', in_out ="OUTPUT", socket_type = "NodeSocketGeometry")
    curvature.interface.items_tree[0].attribute_domain = 'POINT'

    #node Group Output
    group_output = curvature.nodes.new("NodeGroupOutput")

    #Set locations
    group_input.location = (-214.06039428710938, 73.0862045288086)
    store_attribute.location = (29.041637420654297, 58.562652587890625)
    group_output.location = (270.24505615234375, -11.900897979736328)
    named_attribute.location = (-518.30517578125, -93.80853271484375)
    math_add.location = (-282.4539794921875, -164.74874877929688)
    edge_angle.location = (-844.835693359375, -334.1424255371094)
    normalize.location = (-655.8768310546875, -303.60455322265625)
    half_of_one.location = (-470.9601135253906, -294.2790222167969)

    #Set dimensions
    group_input.width, group_input.height = 140.0, 100.0
    normalize.width, normalize.height = 140.0, 100.0
    half_of_one.width, half_of_one.height = 140.0, 100.0
    edge_angle.width, edge_angle.height = 140.0, 100.0
    group_output.width, group_output.height = 140.0, 100.0

    #initialize curvature links
    #group_input.Geometry -> store_attribute.Geometry
    curvature.links.new(group_input.outputs['Geometry'], store_attribute.inputs['Geometry'])
    #store_attribute.Geometry -> group_output.Geometry
    curvature.links.new(store_attribute.outputs['Geometry'], group_output.inputs['Geometry'])
    #edge_angle.Signed Angle -> normalize.Value
    curvature.links.new(edge_angle.outputs['Signed Angle'], normalize.inputs['Value'])
    #narmalize.Value -> half_of_one.Value
    curvature.links.new(normalize.outputs['Value'], half_of_one.inputs['Value'])
    #half_of_one.Value -> math_add.Value
    curvature.links.new(half_of_one.outputs['Value'], math_add.inputs[1])
    #named_attribute.Curvature -> math_add.Value
    curvature.links.new(named_attribute.outputs['Attribute'], eraser.inputs[0])
    curvature.links.new(eraser.outputs['Value'], math_add.inputs[0])
    #math_add.Value -> store_attribute
    curvature.links.new(math_add.outputs['Value'], store_attribute.inputs['Value'])
    return curvature


def add_vertex_group(object, name):
    if object.type == 'MESH':
        vertex_groups = object.vertex_groups
        vertex_groups.new(name = name)
    else:
        return
    
    
def apply_modifier(object, modifier):
    seg_modifier = object.modifiers.new(name = "GeometryNode", type = 'NODES')
    if seg_modifier is not None:
        seg_modifier.node_group = modifier
    else:
        return
