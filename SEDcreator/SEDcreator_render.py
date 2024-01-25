import sys
import os
import math
import re
import bpy
from glob import glob
from SEDcreator import SEDcreator_utils

"""
Render functions
"""

def render(context, imgDir, imgName):
    """ Render the scene.

    Args:
        context : the scene context
        imgDir (str): the image save directory
        imgName (str): the image name
    """

    # Set up rendering
    scene = context.scene
    render = context.scene.render
    renderProp = context.scene.RenderProperties

    scene.use_nodes = True
    scene.view_layers["ViewLayer"].use_pass_z = True
    scene.view_layers["ViewLayer"].use_pass_normal = True
    scene.view_layers["ViewLayer"].use_pass_diffuse_color = True
    scene.view_layers["ViewLayer"].use_pass_object_index = True
    scene.view_layers["ViewLayer"].use_pass_transmission_color = True

    nodes = context.scene.node_tree.nodes
    links = context.scene.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create input render layer node
    render_layers = nodes.new('CompositorNodeRLayers')

    format = "OPEN_EXR"
    color_depth = "16"

    if renderProp.bool_depth:
        # Create depth output nodes
        depth_file_output = nodes.new(type="CompositorNodeOutputFile")
        depth_file_output.label = 'Depth Output'
        depth_file_output.base_path = "" 
        depth_file_output.file_slots[0].use_node_format = True
        depth_file_output.format.file_format = format
        depth_file_output.format.color_depth = color_depth
        if format == "OPEN_EXR":
            links.new(render_layers.outputs["Depth"],
                      depth_file_output.inputs[0])
        else:
            depth_file_output.format.color_mode = "BW"

            # Remap as other types can not represent the full range of depth.
            map = nodes.new(type="CompositorNodeMapValue")
            # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
            map.offset = [-0.7]
            map.size = [1.4]
            map.use_min = True
            map.min = [0]
            links.new(render_layers.outputs["Depth"], map.inputs[0])
            links.new(map.outputs[0], depth_file_output.inputs[0])

    if renderProp.bool_normal:
        # Create normal output nodes
        scene.view_layers["ViewLayer"].use_pass_normal = True
        scale_node = nodes.new(type="CompositorNodeMixRGB")
        scale_node.blend_type = "MULTIPLY"
        # scale_node.use_alpha = True
        scale_node.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
        links.new(render_layers.outputs["Normal"], scale_node.inputs[1])

        bias_node = nodes.new(type="CompositorNodeMixRGB")
        bias_node.blend_type = "ADD"
        # bias_node.use_alpha = True
        bias_node.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
        links.new(scale_node.outputs[0], bias_node.inputs[1])

        normal_file_output = nodes.new(type="CompositorNodeOutputFile")
        normal_file_output.label = "Normal Output"
        normal_file_output.base_path = ''
        normal_file_output.file_slots[0].use_node_format = True
        normal_file_output.format.file_format = format
        links.new(bias_node.outputs[0], normal_file_output.inputs[0])

    if renderProp.bool_albedo:
        # Create albedo output nodes
        alpha_albedo = nodes.new(type="CompositorNodeSetAlpha")
        links.new(render_layers.outputs['DiffCol'],
                  alpha_albedo.inputs['Image'])
        links.new(render_layers.outputs['Alpha'], alpha_albedo.inputs['Alpha'])

        albedo_file_output = nodes.new(type="CompositorNodeOutputFile")
        albedo_file_output.label = 'Albedo Output'
        albedo_file_output.base_path = ''
        albedo_file_output.file_slots[0].use_node_format = True
        albedo_file_output.format.file_format = format
        albedo_file_output.format.color_mode = 'RGBA'
        albedo_file_output.format.color_depth = color_depth
        links.new(alpha_albedo.outputs['Image'], albedo_file_output.inputs[0])

    if renderProp.bool_id:
        # Create id map output nodes
        id_file_output = nodes.new(type="CompositorNodeOutputFile")
        id_file_output.label = 'ID Output'
        id_file_output.base_path = ''
        id_file_output.file_slots[0].use_node_format = True
        id_file_output.format.file_format = format
        id_file_output.format.color_depth = color_depth

        if format == 'OPEN_EXR':
            links.new(
                render_layers.outputs['IndexOB'], id_file_output.inputs[0])
        else:
            id_file_output.format.color_mode = 'BW'

            divide_node = nodes.new(type='CompositorNodeMath')
            divide_node.operation = 'DIVIDE'
            divide_node.use_clamp = False
            divide_node.inputs[1].default_value = 2 ** int(color_depth)

            links.new(render_layers.outputs['IndexOB'], divide_node.inputs[0])
            links.new(divide_node.outputs[0], id_file_output.inputs[0])

    if renderProp.bool_transmission:
        transmission_file_output = nodes.new("CompositorNodeOutputFile")
        transmission_file_output.label = "Transmission Output"
        transmission_file_output.base_path = ""
        transmission_file_output.file_slots[0].use_node_format = True
        transmission_file_output.format.file_format = format
        transmission_file_output.format.color_depth = color_depth
        links.new(render_layers.outputs["TransCol"], transmission_file_output.inputs[0])

    if renderProp.bool_roughness:
        #get a list of all objects (selected)
        bpy.ops.object.select_all(action='SELECT')
        selected = bpy.context.selected_objects

        #replace all material for these objects by their roughness image
        for obj in selected:
            if obj.type != 'CAMERA' and obj.type != 'LIGHT':
                SEDcreator_utils.replace_material_by_roughness(obj)

        #deselect all objects    
        bpy.ops.object.select_all(action='DESELECT')

    if renderProp.bool_curvature:
        #create the node tree for our new modifier
        curvature = SEDcreator_utils.curvature_node_group()
        
        #get a list of all objects (selected)
        bpy.ops.object.select_all(action='SELECT')
        selected = bpy.context.selected_objects
        
        #create and apply our new modifier to all these objects
        for obj in selected:
            if obj.type != 'CAMERA' and obj.type != 'LIGHT':
                SEDcreator_utils.add_vertex_group(obj, "Curvature")
                SEDcreator_utils.apply_modifier(obj, curvature)
        
        #add Attibute node to all materials
        SEDcreator_utils.add_attribute_to_all_materials()
        
        #replace all material for these objects by their curvature map
        for obj in selected:
            if obj.type != 'CAMERA' and obj.type != 'LIGHT':
                SEDcreator_utils.replace_material_by_curvature(obj)

        #deselect all objects    
        bpy.ops.object.select_all(action='DESELECT')

    # Get and define the respective render file paths
    fp = os.path.join(imgDir, imgName)
    print(imgDir)
    print(imgName)
    os.chdir("//")

    if renderProp.bool_beauty:
        path_beauty = os.path.join(imgDir, "beauty", imgName)
        scene.render.filepath = path_beauty
    if renderProp.bool_depth:
        path_depth = os.path.join(imgDir, "depth", imgName)
        depth_file_output.file_slots[0].path = path_depth + "_depth"
    if renderProp.bool_normal:
        path_normal = os.path.join(imgDir, "normal", imgName)
        normal_file_output.file_slots[0].path = path_normal + "_normal"
    if renderProp.bool_albedo:
        path_albedo = os.path.join(imgDir, "albedo", imgName)
        albedo_file_output.file_slots[0].path = path_albedo + "_albedo"
    if renderProp.bool_id:
        path_id = os.path.join(imgDir, "id", imgName)
        id_file_output.file_slots[0].path = path_id + "_id"
    if renderProp.bool_transmission:
        path_transmission = os.path.join(imgDir, "transmission", imgName)
        transmission_file_output.file_slots[0].path = path_transmission + "_transmission"
    if renderProp.bool_roughness:
        path_roughness = os.path.join(imgDir, "roughness", imgName)
        scene.render.filepath = path_roughness + "_roughness"
    if renderProp.bool_curvature: 
        path_curvature = os.path.join(imgDir, "curvature", imgName)
        scene.render.filepath = path_curvature + "_curvature"


    bpy.ops.render.render(write_still=True)  # render still

    # For debugging the workflow
    # bpy.ops.wm.save_as_mainfile(filepath='debug.blend')
