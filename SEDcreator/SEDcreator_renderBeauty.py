import sys
import os
import math
import re
import bpy
from glob import glob
from SEDcreator import SEDcreator_prepareRender

def renderBeauty(context, imgDir, imgName):

    # Set up rendering
    scene = context.scene
    render = context.scene.render
    renderProp = context.scene.RenderProperties

    SEDcreator_prepareRender.enableUsePasses(context)

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

    bpy.ops.render.render(write_still=True)  # render still
    return
