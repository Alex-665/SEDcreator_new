import sys
import os
import math
import re
import bpy
from glob import glob
from SEDcreator import SEDcreator_prepareRender

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

    SEDcreator_prepareRender.enableUsePasses(context)

    #ça doit marcher aussi si on ne met que scene.node...
    nodes = context.scene.node_tree.nodes
    links = context.scene.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create input render layer node
    render_layers = nodes.new('CompositorNodeRLayers')

    format = "OPEN_EXR"
    color_depth = "16"

    #fp = os.path.join(imgDir, imgName)
    #print(imgDir)
    #print(imgName)
    os.chdir("//")

    SEDcreator_prepareRender.prepareRenderBeauty(renderProp.bool_beauty, context, imgDir, imgName)
    SEDcreator_prepareRender.prepareRenderDepth(renderProp.bool_depth, nodes, links, format, color_depth, render_layers, imgDir, imgName)
    SEDcreator_prepareRender.prepareRenderNormal(renderProp.bool_normal, nodes, links, format, render_layers, imgDir, imgName)
    SEDcreator_prepareRender.prepareRenderAlbedo(renderProp.bool_albedo, nodes, links, format, color_depth, render_layers, imgDir, imgName)
    SEDcreator_prepareRender.prepareRenderId(renderProp.bool_id, nodes, links, format, color_depth, render_layers, imgDir, imgName)
    SEDcreator_prepareRender.prepareRenderTransmission(renderProp.bool_transmission, nodes, links, format, color_depth, render_layers, imgDir, imgName)

    # Get and define the respective render file paths

    bpy.ops.render.render(write_still=True)  # render still

    # For debugging the workflow
    # bpy.ops.wm.save_as_mainfile(filepath='debug.blend')
    return
